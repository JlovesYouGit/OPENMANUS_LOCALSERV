from typing import Dict, List, Optional, Union
import time

from pydantic import Field, model_validator

from app.agent.browser import BrowserContextHelper
from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.ask_human import AskHuman
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.mcp import MCPClients, MCPClientTool
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
from app.tool.web_search import WebSearch
from app.utils.entity_resolution import resolve_entities_in_query, is_financial_query
from app.utils.consistency_audit import financial_auditor
from app.utils.output_filter import filter_model_output, handle_ambiguous_entity_response
from app.utils.stock_price_extractor import extract_and_validate_stock_prices
from app.utils.query_analyzer import analyze_user_query, QueryType, get_query_type_description
from app.utils.diagnostic_logger import diagnostic_logger, log_query_processing, log_error, DiagnosticLevel


class Manus(ToolCallAgent):
    """A versatile general-purpose agent with support for both local and MCP tools."""

    name: str = "Manus"
    description: str = "A versatile agent that can solve various tasks using multiple tools including MCP-based tools"

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: Union[int, bool, None] = 10000
    max_steps: int = 20

    # MCP clients for remote tool access
    mcp_clients: MCPClients = Field(default_factory=MCPClients)

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            WebSearch(),  # Add the WebSearch tool for current information
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])
    browser_context_helper: Optional[BrowserContextHelper] = None

    # Track connected MCP servers
    connected_servers: Dict[str, str] = Field(
        default_factory=dict
    )  # server_id -> url/command
    _initialized: bool = False

    @model_validator(mode="after")
    def initialize_helper(self) -> "Manus":
        """Initialize basic components synchronously."""
        self.browser_context_helper = BrowserContextHelper(self)
        return self

    @classmethod
    async def create(cls, **kwargs) -> "Manus":
        """Factory method to create and properly initialize a Manus instance."""
        instance = cls(**kwargs)
        await instance.initialize_mcp_servers()
        
        # Initialize local models if configured
        if config.is_local_mode and config.local_model_handler:
            print("🔄 Initializing Manus agent with local models...")
            # For DirectMLOptimizedHandler, we don't need to pre-load models
            # Models are loaded on-demand when needed
            print("✅ Local models will be loaded on-demand when needed")
            
        instance._initialized = True
        return instance

    async def initialize_mcp_servers(self) -> None:
        """Initialize connections to configured MCP servers."""
        if config.mcp_config and config.mcp_config.servers:
            for server_id, server_config in config.mcp_config.servers.items():
                try:
                    if server_config.type == "sse":
                        if server_config.url:
                            await self.connect_mcp_server(server_config.url, server_id)
                            logger.info(
                                f"Connected to MCP server {server_id} at {server_config.url}"
                            )
                    elif server_config.type == "stdio":
                        if server_config.command:
                            await self.connect_mcp_server(
                                server_config.command,
                                server_id,
                                use_stdio=True,
                                stdio_args=server_config.args or [],
                            )
                            logger.info(
                                f"Connected to MCP server {server_id} using command {server_config.command}"
                            )
                except Exception as e:
                    logger.error(f"Failed to connect to MCP server {server_id}: {e}")

    async def connect_mcp_server(
        self,
        server_url: str,
        server_id: str = "",
        use_stdio: bool = False,
        stdio_args: Optional[List[str]] = None,
    ) -> None:
        """Connect to an MCP server and add its tools."""
        if use_stdio:
            await self.mcp_clients.connect_stdio(
                server_url, stdio_args or [], server_id
            )
            self.connected_servers[server_id or server_url] = server_url
        else:
            await self.mcp_clients.connect_sse(server_url, server_id)
            self.connected_servers[server_id or server_url] = server_url

        # Update available tools with only the new tools from this server
        new_tools = [
            tool for tool in self.mcp_clients.tools if tool.server_id == server_id
        ]
        self.available_tools.add_tools(*new_tools)

    async def disconnect_mcp_server(self, server_id: str = "") -> None:
        """Disconnect from an MCP server and remove its tools."""
        await self.mcp_clients.disconnect(server_id)
        if server_id:
            self.connected_servers.pop(server_id, None)
        else:
            self.connected_servers.clear()

        # Rebuild available tools without the disconnected server's tools
        base_tools = [
            tool
            for tool in self.available_tools.tools
            if not isinstance(tool, MCPClientTool)
        ]
        self.available_tools = ToolCollection(*base_tools)
        self.available_tools.add_tools(*self.mcp_clients.tools)

    async def cleanup(self):
        """Clean up Manus agent resources."""
        if self.browser_context_helper:
            await self.browser_context_helper.cleanup_browser()
        # Disconnect from all MCP servers only if we were initialized
        if self._initialized:
            await self.disconnect_mcp_server()
            self._initialized = False

    async def think(self) -> bool:
        """Process current state and decide next actions with appropriate context."""
        if not self._initialized:
            await self.initialize_mcp_servers()
            self._initialized = True

        original_prompt = self.next_step_prompt
        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            tc.function.name == BrowserUseTool().name
            for msg in recent_messages
            if msg.tool_calls
            for tc in msg.tool_calls
        )

        if browser_in_use and self.browser_context_helper:
            self.next_step_prompt = (
                await self.browser_context_helper.format_next_step_prompt()
            )

        result = await super().think()

        # Restore original prompt
        self.next_step_prompt = original_prompt

        return result

    async def run_with_local_models(self, request: Optional[str] = None) -> str:
        """Run the agent with local models when available"""
        start_time = time.time()
        
        try:
            if config.is_local_mode and config.local_model_handler:
                # Use local models
                print("🤖 Using local models for inference...")
                if not request:
                    request = "Hello, what can you do?"
                
                # Analyze the query first
                query_analysis = analyze_user_query(request)
                diagnostic_logger.log_diagnostic(
                    DiagnosticLevel.INFO,
                    f"Query analyzed as {query_analysis.query_type.value} with confidence {query_analysis.confidence:.2f}",
                    {
                        "query": request,
                        "analysis": {
                            "type": query_analysis.query_type.value,
                            "confidence": query_analysis.confidence,
                            "entities": query_analysis.entities,
                            "requires_current_info": query_analysis.requires_current_info,
                            "tools_required": query_analysis.requires_tools
                        }
                    },
                    "query_analyzer"
                )
                
                # For certain query types, provide immediate responses
                if query_analysis.query_type == QueryType.GREETING:
                    response = "Hello! How can I help you today? 😊"
                    processing_time = time.time() - start_time
                    log_query_processing(request, {
                        "type": "greeting",
                        "confidence": 1.0
                    }, response, processing_time)
                    return response
                
                # Try the DirectML handler first - ensure model is loaded
                try:
                    # Wait for model to be ready if using local model handler
                    if hasattr(config.local_model_handler, 'model_ready'):
                        import time
                        timeout = 60  # 60 second timeout
                        start_wait = time.time()
                        
                        # Wait for at least the lightweight model to be ready
                        while not config.local_model_handler.model_ready.get("tinyllama", False) and \
                              (time.time() - start_wait) < timeout:
                            time.sleep(0.5)  # Check every 500ms
                            print("⏳ Waiting for model to be ready...")
                        
                        # For reasoning tasks, also wait for phi3 model
                        if not config.local_model_handler.model_ready.get("phi3", False) and \
                           (time.time() - start_wait) < timeout:
                            print("⏳ Waiting for reasoning model to be ready...")
                    
                    response = await config.local_model_handler.chat_with_agent(
                        "reasoning",  # Use reasoning agent for main tasks
                        request
                    )
                    print(f"Response: {response}")
                    
                    # Log the processing details
                    processing_time = time.time() - start_time
                    log_query_processing(request, {
                        "type": query_analysis.query_type.value,
                        "confidence": query_analysis.confidence
                    }, response, processing_time)
                    
                    return response
                except Exception as e:
                    logger.error(f"DirectML handler failed: {e}")
                    log_error("directml_handler", e, {"request": request})
                    # Fall back to a simpler approach
                    return await self._fallback_local_inference(request)
            else:
                # Fall back to original implementation
                return await super().run(request)
                
        except Exception as e:
            logger.error(f"Error running Manus agent with local models: {e}")
            return f"Error: {str(e)}"
    
    async def _fallback_local_inference(self, request: str) -> str:
        """Fallback method for local inference when DirectML handler fails"""
        try:
            # Use a simpler approach that might work with DirectML
            import asyncio
            import subprocess
            import json
            import tempfile
            import os
            
            # Create a simple script to run the model
            script_content = f'''
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load model and tokenizer
model_path = "./models/phi-3-mini"
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    local_files_only=True,
    dtype=torch.float32,
    low_cpu_mem_usage=True
)

# Move to appropriate device
device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
elif hasattr(torch, 'directml') and torch.directml.is_available():
    device = "privateuseone:0"
    
model = model.to(device)

# Process input
prompt = "Human: {request}\\nAssistant:"
inputs = tokenizer(prompt, return_tensors="pt").to(device)

# Generate response
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

# Decode response
response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
print(response)
'''
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Run the script in a separate process
                result = subprocess.run(
                    ['python', script_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    raise Exception(f"Script failed: {result.stderr}")
            finally:
                # Clean up temporary file
                os.unlink(script_path)
            
        except Exception as e:
            logger.error(f"Fallback local inference failed: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
            
    async def quick_task(self, task: str) -> str:
        """Handle quick tasks with lightweight agent"""
        if config.is_local_mode and config.local_model_handler:
            print("⚡ Using lightweight agent for quick task...")
            return await config.local_model_handler.chat_with_agent(
                "lightweight",
                task
            )
        else:
            # Fall back to main agent
            return await super().run(task)
            
    def _requires_current_information(self, task: str) -> bool:
        """Determine if a task requires current information"""
        # CRITICAL FIX: Enhanced detection to prevent context leakage
        task_lower = task.lower()
        
        # Check for greetings - these should NEVER trigger current information processing
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "howdy", "what's up", "how are you", "sup"
        ]
        if any(greeting in task_lower for greeting in greetings):
            return False
            
        # Check for personal questions - these should use general knowledge, not forced financial responses
        personal_questions = [
            "who is", "what is elon musk", "tell me about", "biography", "life of",
            "born in", "died in", "career of", "history of"
        ]
        if any(question in task_lower for question in personal_questions):
            return False
            
        # Check for corrections - these should be handled as conversation corrections
        corrections = [
            "thats not what i said", "not what i meant", "i meant", "correction",
            "wrong", "incorrect", "that's not right"
        ]
        if any(correction in task_lower for correction in corrections):
            return False
        
        current_keywords = [
            "stock", "price", "current", "today", "now", "latest", 
            "recent", "up-to-date", "real-time", "live", "market",
            "weather", "temperature", "news", "breaking", "time",
            "date", "moment", "presently", "currently", "right now",
            "this moment", "at present", "financial", "trading", "exchange",
            "calendar", "schedule", "event", "meeting", "appointment"
        ]
        # Check for exact matches first
        if any(keyword in task_lower for keyword in current_keywords):
            return True
        # Additional checks for specific patterns
        if "what is" in task_lower and any(word in task_lower for word in ["price", "cost", "rate"]):
            return True
        if "how much" in task_lower and any(word in task_lower for word in ["cost", "price"]):
            return True
        # Check for time-related patterns
        time_patterns = [
            r"what time", r"current time", r"time now", 
            r"what date", r"today's date", r"current date"
        ]
        import re
        for pattern in time_patterns:
            if re.search(pattern, task_lower):
                return True
        return False

    async def complex_task(self, task: str) -> str:
        """Handle complex tasks with reasoning agent"""
        # CRITICAL FIX: Enhanced task handling with proper context routing
        task_lower = task.lower()
        
        # Check for greetings
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "howdy", "what's up", "how are you", "sup"
        ]
        if any(greeting in task_lower for greeting in greetings):
            return "Hello! How can I help you today? 😊"
            
        # Check for personal questions
        personal_questions = [
            "who is", "what is elon musk", "tell me about", "biography", "life of",
            "born in", "died in", "career of", "history of"
        ]
        if any(question in task_lower for question in personal_questions):
            # Handle biographical questions with general knowledge approach
            return await self._handle_biographical_question(task)
            
        # Check for corrections
        corrections = [
            "thats not what i said", "not what i meant", "i meant", "correction",
            "wrong", "incorrect", "that's not right"
        ]
        if any(correction in task_lower for correction in corrections):
            return "I apologize for the confusion. Could you please clarify what you were looking for so I can provide a better response?"
        
        # CRITICAL FIX: Handle search-related queries properly to prevent response loop
        search_indicators = [
            "search for", "search about", "find information", "look up", 
            "important source info", "important historical event"
        ]
        if any(indicator in task_lower for indicator in search_indicators):
            print(f"🔍 Detected search request: {task}")
            # For search queries, use the web search tool directly
            return await self._get_current_information(task)
        
        # Pre-check if this task requires current information before even trying model inference
        if self._requires_current_information(task):
            print("🔍 Detected request for current information, using WebSearch tool directly...")
            return await self._get_current_information(task)
        
        if config.is_local_mode and config.local_model_handler:
            print("🧠 Using reasoning agent for complex task...")
            try:
                # First, let the model analyze the task and decide what tools are needed
                analysis_prompt = f"""
Analyze the following task and determine what actions are needed:

Task: {task}

Please provide your analysis in the following format:
1. Task Analysis: Break down what needs to be done
2. Required Tools: List any tools that would be helpful (web_search, python_execute, etc.)
3. Reasoning Steps: Outline your approach to solving this task
4. Information Needed: Identify any current information that would be useful

Do not attempt to solve the task yet, just analyze it."""
                
                # Get model's analysis
                analysis_response = await config.local_model_handler.chat_with_agent(
                    "reasoning",
                    analysis_prompt
                )
                
                # Now let the model decide if tools are needed based on analysis
                decision_prompt = f"""
Based on your analysis:

{analysis_response}

Task: {task}

Should any tools be used before providing a final response? If so, which ones?
Please respond with either:
- YES: [tool_name] - if a specific tool should be used
- NO - if no tools are needed

Be concise."""
                
                decision_response = await config.local_model_handler.chat_with_agent(
                    "reasoning",
                    decision_prompt
                )
                
                # Parse the decision and use tools if needed
                tool_results = {}
                if "YES:" in decision_response.upper():
                    # Extract tool name
                    import re
                    tool_match = re.search(r'YES:\s*(\w+)', decision_response.upper())
                    if tool_match:
                        tool_name = tool_match.group(1).lower()
                        
                        # Use appropriate tool based on decision
                        if tool_name == "web_search":
                            print("🔍 Using WebSearch tool based on model decision...")
                            search_result = await self._get_current_information(task)
                            tool_results["web_search"] = search_result
                        elif tool_name == "python_execute":
                            # For python execution, we would need to extract code from the task
                            # This is a simplified approach
                            tool_results["python_execute"] = "Python execution tool activated"
                
                # Now provide the final response with all available information
                final_prompt = f"""
Based on your analysis and any tool results, provide a comprehensive and natural response to the task:

Task: {task}

Analysis: {analysis_response}

Tool Results: {tool_results if tool_results else 'No tools were needed'}

Please provide a clear, well-reasoned, and natural response to the original task. Feel free to express yourself naturally without being overly constrained by formal structure."""
                
                return await config.local_model_handler.chat_with_agent(
                    "reasoning",
                    final_prompt
                )
            except Exception as e:
                logger.error(f"DirectML handler failed for complex task: {e}")
                # Fall back to direct tool usage when model fails
                return await self._fallback_tool_usage(task)
        else:
            # Fall back to main agent
            return await super().run(task)
            
    async def _handle_biographical_question(self, task: str) -> str:
        """Handle biographical questions with appropriate response generation"""
        try:
            # For biographical questions, use a more focused prompt
            biographical_prompt = f"""
Please provide a clear and accurate biographical answer to the following question:
{task}

Focus on factual information about the person's life, career, achievements, and significance.
If you don't have specific information about this person, please say so rather than making things up.
"""
            
            if config.is_local_mode and config.local_model_handler:
                return await config.local_model_handler.chat_with_agent(
                    "reasoning",
                    biographical_prompt
                )
            else:
                # Fall back to main agent with focused prompt
                return await super().run(biographical_prompt)
        except Exception as e:
            logger.error(f"Error handling biographical question: {e}")
            return f"I'd be happy to help you learn about {task}. Could you please provide more specific details about what you'd like to know?"

    async def _get_current_information(self, task: str) -> str:
        """Get current information using WebSearch tool with enhanced accuracy and anti-hallucination measures"""
        try:
            # Use WebSearch tool directly
            from app.tool.web_search import WebSearch
            web_search_tool = WebSearch()
            
            # Get current date and time for more precise searches
            from datetime import datetime
            import pytz
            current_time = datetime.now()
            # Try to get user's timezone, fallback to UTC
            try:
                # You might want to configure this based on user preferences
                user_tz = pytz.timezone('US/Eastern')  # Default to US Eastern time
                localized_time = current_time.astimezone(user_tz)
                date_str = localized_time.strftime("%Y-%m-%d")
                time_str = localized_time.strftime("%H:%M:%S")
                timezone_str = str(user_tz)
            except:
                date_str = current_time.strftime("%Y-%m-%d")
                time_str = current_time.strftime("%H:%M:%S")
                timezone_str = "UTC"
            
            # Enhanced query refinement for better search results
            task_lower = task.lower()
            
            # Use advanced entity resolution
            enhanced_context, entities = resolve_entities_in_query(task)
            
            # Extract company name for better stock price queries
            def extract_company_name(query: str) -> str:
                import re
                # Remove common stock price phrases
                query_clean = re.sub(r'(stock|price|current|today|what is|how much|\?)', '', query, flags=re.IGNORECASE)
                query_clean = query_clean.strip()
                
                # Common company mappings
                company_mappings = {
                    'apple': 'Apple', 'microsoft': 'Microsoft', 'google': 'Google',
                    'alphabet': 'Alphabet', 'tesla': 'Tesla', 'amazon': 'Amazon',
                    'nvidia': 'Nvidia', 'meta': 'Meta', 'facebook': 'Facebook',
                    'netflix': 'Netflix', 'ibm': 'IBM', 'intel': 'Intel',
                    'amd': 'AMD', 'adobe': 'Adobe', 'salesforce': 'Salesforce'
                }
                
                for keyword, company in company_mappings.items():
                    if keyword in query_clean.lower():
                        return company
                
                return query_clean if query_clean else ""
            
            if "stock" in task_lower and ("price" in task_lower or "cost" in task_lower):
                # Enhanced stock price queries with financial sources
                company_name = extract_company_name(task)
                if company_name:
                    search_query = f"{company_name} stock price today {date_str} current market price"
                else:
                    search_query = f"current stock price {task} today {date_str} market price"
                
                # Add financial sources for better accuracy
                search_query += " Yahoo Finance Google Finance MarketWatch Bloomberg"
            elif "weather" in task_lower:
                search_query = f"current weather {task} {date_str}"
            elif "news" in task_lower or "breaking" in task_lower:
                search_query = f"latest news {task} {date_str}"
            elif any(time_word in task_lower for time_word in ["time", "date", "calendar", "schedule"]):
                search_query = f"{task} {date_str} {time_str} {timezone_str}"
            else:
                search_query = f"current {task} {date_str}"
                
            search_response = await web_search_tool.execute(
                query=search_query,
                num_results=8,  # Increase results for better accuracy and validation
                fetch_content=True
            )
            
            # Perform consistency audit for financial queries
            if "stock" in task_lower and ("price" in task_lower or "cost" in task_lower):
                # Check if we have a result to audit
                if not search_response.error and search_response.results:
                    result = search_response.results[0]
                    content = result.raw_content or result.description
                    # Record audit result
                    from app.utils.consistency_audit import financial_auditor
                    audit_result = financial_auditor.check_consistency(task, content)
                    financial_auditor.record_audit_result(audit_result)
                    
                    # If inconsistent, add warning to response
                    if not audit_result.is_consistent:
                        print(f"⚠️  Consistency warning for '{task}': {audit_result.deviation_percentage:.2f}% deviation")
            
            if not search_response.error and search_response.results:
                # Enhanced stock price extraction with multiple validation
                if "stock" in task_lower and ("price" in task_lower or "cost" in task_lower):
                    stock_price = self._extract_stock_price(search_response.results)
                    if stock_price:
                        # Get company name for better formatting
                        company_name = extract_company_name(task)
                        if company_name:
                            return f"📈 **Current Stock Price**\n\n**{company_name}**: ${stock_price}\n\n*Data retrieved from financial sources on {date_str} at {time_str} {timezone_str}*"
                        else:
                            return f"📈 **Current Stock Price**\n\n**{task}**: ${stock_price}\n\n*Data retrieved from financial sources on {date_str} at {time_str} {timezone_str}*"
                    else:
                        # If extraction fails, provide the raw search results with better formatting
                        result = search_response.results[0]
                        content = result.raw_content or result.description
                        # Try to extract any price information from the content
                        import re
                        price_match = re.search(r'\$\s*([0-9]+[0-9,]*\.?[0-9]+)', content)
                        if price_match:
                            extracted_price = price_match.group(1).replace(',', '')
                            return f"📊 **Stock Information**\n\nBased on current market data, the price appears to be approximately **${extracted_price}**\n\n*Source: {result.url}*\n*Data as of {date_str} {time_str} {timezone_str}*"
                        else:
                            return f"📊 **Stock Information**\n\nBased on current web search results:\n\n{content}\n\n*Source: {result.url}*\n*Data as of {date_str} {time_str} {timezone_str}*"
                
                # For time/date queries
                if any(time_word in task_lower for time_word in ["time", "date", "calendar", "schedule"]):
                    time_info = self._extract_time_info(search_response.results, task)
                    if time_info:
                        return f"{time_info} (as of {date_str} {time_str} {timezone_str})"
                
                # For other queries, provide the most relevant information
                result = search_response.results[0]
                content = result.raw_content or result.description
                return f"Based on current web search results:\n\n{content}\n\nSource: {result.url}"
            else:
                return f"I tried to search for current information about '{task}', but encountered issues with the search. Error: {search_response.error or 'No results found'}"
        except Exception as e:
            logger.error(f"Error getting current information: {e}")
            return f"Sorry, I encountered an error while searching for current information: {str(e)}"
    
    def _extract_stock_price(self, search_results) -> Optional[str]:
        """Extract stock price from search results with enhanced accuracy and validation"""
        try:
            # Look through the results for stock price information
            for result in search_results:
                content = (result.raw_content or result.description or result.title)
                if not content:
                    continue
                
                # Use enhanced stock price extractor with validation
                prices, formatted_output = extract_and_validate_stock_prices(content, result.url)
                
                if prices:
                    # Return the highest confidence price
                    primary_price = prices[0]
                    return f"{primary_price.price:.2f}"
            
            return None
        except Exception as e:
            logger.error(f"Error extracting stock price: {e}")
            return None
    
    def _extract_time_info(self, search_results, original_query: str) -> Optional[str]:
        """Extract time/date information from search results"""
        try:
            import re
            
            # Look through the results for time/date information
            for result in search_results:
                content = (result.raw_content or result.description or result.title)
                
                # For time queries, look for time patterns
                if "time" in original_query.lower():
                    # Look for time patterns like 14:30, 2:30 PM, etc.
                    time_patterns = [
                        r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\s*(?:AM|PM|am|pm)?\b',  # 14:30 or 2:30 PM
                        r'\b(?:at\s+)?([0-1]?[0-9]|2[0-3])\s*(?::\s*[0-5][0-9])?\s*(?:AM|PM|am|pm)\b',  # 2:30 PM
                    ]
                    
                    for pattern in time_patterns:
                        matches = re.findall(pattern, content[:500])  # Check first 500 chars
                        if matches:
                            return f"The current time information: {matches[0]}"
                
                # For date queries, look for date patterns
                if "date" in original_query.lower():
                    # Look for date patterns like 2025-10-23, October 23, 2025, etc.
                    date_patterns = [
                        r'\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b',  # 2025-10-23
                        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2}\b',  # October 23, 2025
                        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b',  # 23 October 2025
                    ]
                    
                    for pattern in date_patterns:
                        matches = re.findall(pattern, content[:500])  # Check first 500 chars
                        if matches:
                            return f"The current date information: {matches[0]}"
            
            return None
        except Exception as e:
            logger.error(f"Error extracting time info: {e}")
            return None

    async def _fallback_tool_usage(self, task: str) -> str:
        """Fallback method to use tools directly when model inference fails"""
        try:
            # Check if this is a query that requires current information
            if self._requires_current_information(task):
                return await self._get_current_information(task)
            
            # For other types of queries, use the standard fallback
            return await self._fallback_local_inference(task)
        except Exception as e:
            logger.error(f"Fallback tool usage failed: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"

    async def coordinate_agents(self, task: str) -> Dict[str, str]:
        """Coordinate both agents for complex decision making"""
        if config.is_local_mode and config.local_model_handler:
            print("🤝 Coordinating both agents...")
            return await config.local_model_handler.coordinate_agents(task)
        else:
            # Fall back to single agent
            response = await super().run(task)
            return {
                "main_agent": response,
                "coordination": "Single agent mode - no coordination available"
            }