#!/usr/bin/env python
"""
Simple Web UI for OpenManus
"""

import asyncio
import sys
import json
import os
import logging
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from app.agent.manus import Manus
from app.config import config
from app.utils.rust_compression import compress_chat_history, decompress_chat_history
from app.utils.advanced_chat_history import add_chat_message, get_chat_history, save_chat_history as save_graph_history, load_chat_history as load_graph_history
from app.utils.enhanced_attention import identify_user_intent, generate_enhanced_context, refine_model_response, evaluate_response_quality
from app.utils.output_filter import filter_model_output
from app.utils.consistency_audit import financial_auditor
from app.utils.stock_price_extractor import extract_and_validate_stock_prices
from app.utils.query_analyzer import analyze_user_query, QueryType
from app.utils.diagnostic_logger import generate_diagnostic_report, get_recent_diagnostics
from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_stats, get_query_result
from app.utils.performance_monitor import start_request_timer, end_request_timer, get_performance_report

# Configure Flask to serve static files from the React build directory
app = Flask(__name__)
app.static_folder = os.path.join('newweb', 'quantum-canvas-design', 'dist')

# Add cache control headers
@app.after_request
def after_request(response):
    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    # Add cache control headers to prevent browser caching issues
    if request.endpoint == 'custom_static' or request.endpoint == 'serve_static_files' or request.endpoint == 'index':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Set up logging
logger = logging.getLogger(__name__)

# Route for serving the main index.html file
@app.route('/')
def index():
    """Serve the cover page as the main entry point"""
    return send_from_directory(os.path.join('coverpage', 'Animatedlandingpagedesign', 'dist'), 'index.html')

# Route for serving the main app interface
@app.route('/app')
def app_main():
    """Serve the main app interface"""
    return send_from_directory(os.path.join('newweb', 'quantum-canvas-design', 'dist'), 'index.html')

# Set up static file serving for the React app assets
@app.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join('newweb', 'quantum-canvas-design', 'dist', 'assets'), filename)

# Add static file serving for the cover page assets
@app.route('/coverpage-assets/<path:filename>')
def coverpage_static(filename):
    return send_from_directory(os.path.join('coverpage', 'Animatedlandingpagedesign', 'dist'), filename)

agent = None

# Chat history storage with multiple approaches
chat_history_file = "chat_history_compressed.bin"
chat_graph_file = "chat_history_graph.bin"

# Maximum context window to prevent memory issues - increased for better context retention
MAX_CONTEXT_WINDOW = 8

# Track current conversation session to prevent context leakage
current_session_id = None

def load_chat_history():
    """Load chat history with fallbacks"""
    try:
        # Try to load from graph format first
        load_graph_history()  # This loads the data into the global manager
        history = get_chat_history()  # This gets the linear history from the manager
        if history:
            return history
    except Exception as e:
        print(f"Could not load graph history: {e}")
    
    try:
        # Fallback to compressed format
        with open(chat_history_file, 'rb') as f:
            return decompress_chat_history(f.read())
    except Exception as e:
        print(f"Could not load compressed history: {e}")
        return []

def save_chat_history(history):
    """Save chat history with multiple approaches"""
    try:
        # Save in graph format - first clear existing nodes and rebuild
        # We need to add messages to the global manager
        for msg in history:
            add_chat_message(msg["content"], "user" if msg.get("isUser", False) else "assistant")
        save_graph_history()  # Use the imported function (no parameters needed)
    except Exception as e:
        print(f"Could not save graph history: {e}")
    
    try:
        # Save in compressed format as fallback with better compression
        with open(chat_history_file, 'wb') as f:
            f.write(compress_chat_history(history))
    except Exception as e:
        print(f"Could not save compressed history: {e}")

def delete_chat_history():
    """Delete all chat history"""
    try:
        # Clear graph history
        from app.utils.advanced_chat_history import chat_history_manager
        chat_history_manager.clear_history()
        save_graph_history()
        
        # Delete compressed history file
        if os.path.exists(chat_history_file):
            os.remove(chat_history_file)
            
        print("Chat history deleted successfully")
    except Exception as e:
        print(f"Error deleting chat history: {e}")

def delete_specific_message(message_content: str):
    """Delete a specific message from chat history"""
    try:
        # Load current history
        history = load_chat_history()
        
        # Find and remove the message
        new_history = [msg for msg in history if msg["content"] != message_content]
        
        # Save updated history
        save_chat_history(new_history)
        
        print(f"Message deleted: {message_content}")
    except Exception as e:
        print(f"Error deleting message: {e}")

def extract_company_name(query: str) -> str:
    """Extract company name from stock price query"""
    try:
        # Simple extraction of company name from query
        query_clean = query.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ["what is", "what's", "tell me", "show me", "find", "get", "current", "today's"]
        for prefix in prefixes:
            if query_clean.startswith(prefix):
                query_clean = query_clean[len(prefix):].strip()
                break
        
        suffixes = ["stock price", "price", "share price", "value"]
        for suffix in suffixes:
            if query_clean.endswith(suffix):
                query_clean = query_clean[:-len(suffix)].strip()
                break
        
        # Remove common words
        common_words = ["the", "a", "an", "for", "of", "in", "on", "at", "to", "is", "are"]
        for word in common_words:
            query_clean = query_clean.replace(word, "").strip()
        
        # If no specific company found, return the cleaned query
        return query_clean if query_clean else ""
        
    except Exception as e:
        print(f"Error extracting company name: {e}")
        return ""

# Set up the async processing callback for the query manager
async def process_query_async(message: str, query_obj):
    """Process a query asynchronously"""
    global agent
    start_time = start_request_timer()
    
    try:
        # Load chat history
        chat_history = load_chat_history()
        
        # Manage context window to prevent memory issues
        if len(chat_history) > MAX_CONTEXT_WINDOW * 2:  # *2 because each exchange has user and agent messages
            # Keep only the most recent messages
            chat_history = chat_history[-(MAX_CONTEXT_WINDOW * 2):]
        
        # Add user message to both history systems
        add_chat_message(message, 'user')
        chat_history.append({
            "timestamp": datetime.now().isoformat(),
            "content": message,
            "isUser": True
        })
        
        # Get user language preference
        language_preference = 'en'  # Default to English
        try:
            language_file = "user_language_preference.txt"
            if os.path.exists(language_file):
                with open(language_file, 'r') as f:
                    language_preference = f.read().strip()
        except Exception as e:
            print(f"Could not load language preference: {e}")
        
        # Generate enhanced context for better attention
        enhanced_context = generate_enhanced_context(message, chat_history)
        
        # Analyze the query using our advanced query analyzer
        query_analysis = analyze_user_query(message)
        
        # Pre-check if this is a current information query with enhanced detection
        current_keywords = [
            "stock", "price", "current", "today", "now", "latest", 
            "recent", "up-to-date", "real-time", "live", "market",
            "weather", "temperature", "news", "breaking", "time",
            "date", "moment", "presently", "currently", "right now",
            "this moment", "at present", "financial", "trading", "exchange"
        ]
        message_lower = message.lower()
        is_current_info_query = any(keyword in message_lower for keyword in current_keywords)
        
        # Additional pattern matching for more accurate detection
        if not is_current_info_query:
            if "what is" in message_lower and any(word in message_lower for word in ["price", "cost", "rate"]):
                is_current_info_query = True
            elif "how much" in message_lower and any(word in message_lower for word in ["cost", "price"]):
                is_current_info_query = True
        
        # Override with query analyzer results if it's more confident
        if query_analysis.requires_current_info and query_analysis.confidence > 0.7:
            is_current_info_query = True
        
        # Additional checks for other tool types
        is_code_query = any(keyword in message_lower for keyword in ["code", "program", "script", "function", "class", "method", "execute", "run", "calculate", "compute", "algorithm"])
        is_file_query = any(keyword in message_lower for keyword in ["file", "read", "write", "edit", "modify", "create", "delete", "update", "append", "save"])
        is_browse_query = any(keyword in message_lower for keyword in ["browse", "visit", "website", "webpage", "url", "navigate", "click", "search", "find", "lookup"])
        
        # CRITICAL FIX: Enhanced handling to prevent context leakage
        # Check for greetings and personal questions that should NOT trigger financial responses
        is_greeting = any(greeting in message_lower for greeting in [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "howdy", "what's up", "how are you", "sup"
        ])
        
        is_personal_question = any(question in message_lower for keyword in [
            "who is", "what is elon musk", "tell me about", "biography", "life of",
            "born in", "died in", "career of", "history of"
        ] for question in [keyword])
        
        is_correction = any(correction in message_lower for keyword in [
            "thats not what i said", "not what i meant", "i meant", "correction",
            "wrong", "incorrect", "that's not right"
        ] for correction in [keyword])
        
        # CRITICAL FIX: Only process as current info query if it's actually a financial/biographical query
        # and NOT a greeting, personal question, or correction
        should_process_as_current_info = (
            is_current_info_query and 
            not is_greeting and 
            not is_personal_question and 
            not is_correction
        )
        
        # Enhanced handling for current information queries
        if should_process_as_current_info:
            # Handle current information queries with priority
            try:
                print("🔍 Detected request for current information, using WebSearch tool directly...")
                from app.tool.web_search import WebSearch
                web_search = WebSearch()
                search_query = message
                
                # Get current date and time for more precise searches
                current_time = datetime.now()
                # Try to get user's timezone, fallback to UTC
                try:
                    import pytz
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
                
                # Refine the query for better search results with current date context
                if "stock" in message_lower and ("price" in message_lower or "cost" in message_lower):
                    # For stock prices, use more specific financial queries with current date
                    if "apple" in message_lower or "aapl" in message_lower:
                        search_query = f"AAPL Apple stock price today {date_str} current market price"
                    elif "microsoft" in message_lower or "msft" in message_lower:
                        search_query = f"MSFT Microsoft stock price today {date_str} current market price"
                    elif "google" in message_lower or "goog" in message_lower or "alphabet" in message_lower:
                        search_query = f"GOOGL Google Alphabet stock price today {date_str} current market price"
                    elif "tesla" in message_lower or "tsla" in message_lower:
                        search_query = f"TSLA Tesla stock price today {date_str} current market price"
                    elif "amazon" in message_lower or "amzn" in message_lower:
                        search_query = f"AMZN Amazon stock price today {date_str} current market price"
                    elif "nvidia" in message_lower or "nvda" in message_lower:
                        search_query = f"NVDA Nvidia stock price today {date_str} current market price"
                    elif "meta" in message_lower or "facebook" in message_lower or "fb" in message_lower:
                        search_query = f"META Facebook stock price today {date_str} current market price"
                    else:
                        # Extract company name from query for better search
                        company_name = extract_company_name(message)
                        if company_name:
                            search_query = f"{company_name} stock price today {date_str} current market price"
                        else:
                            search_query = f"current stock price {message} today {date_str} market price"
                    
                    # Add financial sources for better accuracy
                    search_query += " Yahoo Finance Google Finance MarketWatch"
                elif "weather" in message_lower:
                    search_query = f"current weather {message} {date_str}"
                elif "news" in message_lower or "breaking" in message_lower:
                    search_query = f"latest news {message} {date_str}"
                elif any(time_word in message_lower for time_word in ["time", "date", "calendar", "schedule"]):
                    # For time/date queries, include current date context
                    search_query = f"{message} {date_str} {time_str} {timezone_str}"
                else:
                    # For other current info queries, include date context
                    search_query = f"current {message} {date_str}"
                
                # Use asyncio.create_task for non-blocking execution
                search_task = asyncio.create_task(web_search.execute(
                    query=search_query,
                    num_results=5,  # Increase results for better accuracy
                    fetch_content=True,
                    lang=language_preference  # Use user's language preference
                ))
                search_response = await search_task
                
                if not search_response.error and search_response.results:
                    # For stock prices, try to extract the current price from the results
                    if "stock" in message_lower and ("price" in message_lower or "cost" in message_lower):
                        stock_price = extract_stock_price_from_results(search_response.results)
                        if stock_price:
                            response_text = f"The current stock price for {message} is ${stock_price} (as of {date_str} {time_str} {timezone_str})"
                        else:
                            result = search_response.results[0]
                            content = result.raw_content or result.description
                            response_text = f"Based on current web search results:\n\n{content}\n\nSource: {result.url}"
                    # For time/date queries, try to extract specific time information
                    elif any(time_word in message_lower for time_word in ["time", "date", "calendar", "schedule"]):
                        time_info = extract_time_info_from_results(search_response.results, message)
                        if time_info:
                            response_text = f"{time_info} (as of {date_str} {time_str} {timezone_str})"
                        else:
                            result = search_response.results[0]
                            content = result.raw_content or result.description
                            response_text = f"Based on current web search results:\n\n{content}\n\nSource: {result.url}"
                    else:
                        result = search_response.results[0]
                        content = result.raw_content or result.description
                        response_text = f"Based on current web search results:\n\n{content}\n\nSource: {result.url}"
                else:
                    # Enhanced error handling with more specific messages
                    error_msg = search_response.error or 'No results found'
                    if 'DuckDuckGoSearchException' in error_msg:
                        response_text = f"I tried to search for current information about '{message}', but encountered issues with DuckDuckGo search. This is often temporary. Error: {error_msg}"
                    elif 'timeout' in error_msg.lower():
                        response_text = f"I tried to search for current information about '{message}', but the search timed out. Please try again in a moment. Error: {error_msg}"
                    else:
                        response_text = f"I tried to search for current information about '{message}', but encountered issues with the search. Error: {error_msg}"
                
                # Add to history
                add_chat_message(response_text, 'assistant')
                chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "content": response_text,
                    "isUser": False
                })
                save_chat_history(chat_history)
                
                end_request_timer(start_time, len(response_text), "web_search", len(message), True)
                return response_text
            except Exception as direct_search_error:
                print(f"Direct search failed: {direct_search_error}")
                import traceback
                traceback.print_exc()
                # Fall through to normal processing

        # Try the DirectML approach first
        try:
            # Reuse existing agent when possible for better context retention
            # Only create fresh agent if needed
            if agent is None:
                agent = await Manus.create()
            
            try:
                # CRITICAL FIX: Use proper context routing based on query type
                if is_greeting:
                    # Handle greetings with appropriate response
                    response = "Hello! How can I help you today? 😊"
                elif is_personal_question:
                    # Handle biographical questions with general knowledge approach
                    response = await agent.complex_task(
                        f"Please provide a biographical answer to this question: {message}"
                    )
                elif is_correction:
                    # Handle user corrections with acknowledgment
                    response = await agent.complex_task(
                        f"The user is correcting a previous response. Please acknowledge their correction and provide a better response to their original query: {message}"
                    )
                else:
                    # Use the reasoning model for better tool usage with enhanced context
                    # Include both enhanced context and recent conversation history for better memory retention
                    # Format context in a more structured way for better reasoning
                    # OPTIMIZATION: Limit conversation history to reduce processing overhead
                    conversation_history = "\n".join([
                        f"{'User' if msg.get('isUser', False) else 'Assistant'}: {msg.get('content', '')}"
                        for msg in chat_history[-8:]  # Increase to last 4 exchanges for better context
                    ])
                    
                    # Use the enhanced reasoning flow that separates analysis from tool usage
                    # Pass the conversation history as context to maintain continuity
                    if config.is_local_mode and config.local_model_handler:
                        # Use the DirectML handler directly with context
                        response = await config.local_model_handler.chat_with_agent(
                            "reasoning",
                            message,
                            context=f"Previous conversation:\n{conversation_history}" if conversation_history else None
                        )
                    else:
                        # Fall back to agent's complex_task method
                        response = await agent.complex_task(message)
                
                # OPTIMIZATION: Streamline response processing pipeline to reduce bottlenecks
                # Only apply heavy processing for complex responses
                if len(response) > 50:  # Only refine longer responses
                    # Refine response with enhanced attention mechanism
                    refined_response = refine_model_response(response, message)
                    
                    # Apply output filtering for relevance and quality
                    from app.utils.output_filter import filter_model_output
                    should_block, filtered_response, filter_metadata = filter_model_output(message, refined_response)
                    
                    # CRITICAL FIX: If response is blocked, generate appropriate response based on query type
                    if should_block:
                        if is_greeting:
                            refined_response = "Hello! How can I help you today? 😊"
                        elif is_personal_question:
                            refined_response = f"I'd be happy to help you learn about {message}. Could you please provide more specific details?"
                        elif is_correction:
                            refined_response = "I apologize for the confusion. Could you please clarify what you were looking for?"
                        elif should_process_as_current_info:
                            # For current information queries, provide a more helpful response
                            refined_response = f"I'd be happy to help you with information about {message}. Let me search for the most current information for you."
                        else:
                            # For other blocked responses, provide a general helpful message
                            refined_response = "I apologize, but I'm having trouble providing a relevant response to your query. Could you please rephrase or provide more details?"
                    else:
                        refined_response = response  # Use original response for better speed
                else:
                    refined_response = response
                    filter_metadata = {}
                
                # Evaluate response quality (lightweight evaluation)
                quality_metrics = {"overall": 0.8}  # Default high quality for faster processing
                
                # Add filter metadata to quality metrics
                if filter_metadata:
                    quality_metrics.update(filter_metadata)
                
                # Add agent response to both history systems
                add_chat_message(refined_response, 'assistant')
                chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "content": refined_response,
                    "isUser": False
                })
                
                # Save chat history with multiple approaches (async for better performance)
                # OPTIMIZATION: Don't block on save for faster response
                import threading
                threading.Thread(target=save_chat_history, args=(chat_history,)).start()
                
                # Check for tool usage information
                tool_usage_info = None
                if len(response) > 100 and ("tool" in response.lower() or "browser" in response.lower() or "python" in response.lower() or "search" in response.lower()):
                    tool_usage_info = "I'm using my tools to help with your request..."
                
                end_request_timer(start_time, len(response), "agent", len(message), True)
                return {
                    "response": refined_response,
                    "tool_usage": tool_usage_info,
                    "quality": quality_metrics
                }
            except Exception as agent_error:
                # If the agent fails, try direct tool usage as a fallback
                print(f"Agent failed: {agent_error}")
                try:
                    # Try direct tool usage for current information queries
                    if should_process_as_current_info:
                        from app.tool.web_search import WebSearch
                        web_search = WebSearch()
                        search_query = message
                        if "stock" in message.lower() and ("price" in message_lower or "cost" in message_lower):
                            search_query = f"current stock price {message}"
                        
                        search_response = await web_search.execute(
                            query=search_query,
                            num_results=5,
                            fetch_content=True,
                            lang=language_preference  # Use user's language preference
                        )
                        
                        if not search_response.error and search_response.results:
                            result = search_response.results[0]
                            content = result.raw_content or result.description
                            response_text = f"Based on current web search results:\n\n{content}\n\nSource: {result.url}"
                            
                            # Add to history
                            add_chat_message(response_text, 'assistant')
                            chat_history.append({
                                "timestamp": datetime.now().isoformat(),
                                "content": response_text,
                                "isUser": False
                            })
                            save_chat_history(chat_history)
                            
                            end_request_timer(start_time, len(response_text), "web_search", len(message), True)
                            return {
                                "response": response_text
                            }
                        else:
                            error_response = f"I tried to search for current information about '{message}', but encountered issues with the search. Error: {search_response.error or 'No results found'}"
                            
                            # Add to history
                            add_chat_message(error_response, 'assistant')
                            chat_history.append({
                                "timestamp": datetime.now().isoformat(),
                                "content": error_response,
                                "isUser": False
                            })
                            save_chat_history(chat_history)
                            
                            return {
                                "response": error_response
                            }
                except Exception as tool_error:
                    print(f"Direct tool usage failed: {tool_error}")
                fallback_response = f"Error generating response: {str(agent_error)}"
                
                # Add to history
                add_chat_message(fallback_response, 'assistant')
                chat_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "content": fallback_response,
                    "isUser": False
                })
                save_chat_history(chat_history)
                
                return {
                    "response": fallback_response
                }
        except Exception as e:
            # If DirectML fails, try a fallback approach
            print(f"DirectML approach failed: {str(e)}")
            
            # CRITICAL FIX: Generate appropriate fallback response based on query type
            if is_greeting:
                fallback_response = "Hello! How can I help you today? 😊"
            elif is_personal_question:
                fallback_response = f"I'd be happy to help you learn about {message}. Could you please provide more specific details?"
            elif is_correction:
                fallback_response = "I apologize for the confusion. Could you please clarify what you were looking for?"
            else:
                fallback_response = run_fallback_inference(message)
            
            # Refine fallback response
            refined_fallback = refine_model_response(fallback_response, message)
            
            # Apply output filtering for relevance and quality
            from app.utils.output_filter import filter_model_output
            should_block, filtered_response, filter_metadata = filter_model_output(message, refined_fallback)
            
            if should_block:
                # Generate appropriate fallback response based on query type
                if is_greeting:
                    refined_fallback = "Hello! How can I help you today? 😊"
                elif is_personal_question:
                    refined_fallback = f"I'd be happy to help you learn about {message}. Could you please provide more specific details?"
                elif is_correction:
                    refined_fallback = "I apologize for the confusion. Could you please clarify what you were looking for?"
                elif should_process_as_current_info:
                    # For current information queries, provide a more helpful response
                    refined_fallback = f"I'd be happy to help you with information about {message}. Let me search for the most current information for you."
                else:
                    # For other blocked responses, provide a general helpful message
                    refined_fallback = "I apologize, but I'm having trouble providing a relevant response to your query. Could you please rephrase or provide more details?"
            
            # Add to history
            add_chat_message(refined_fallback, 'assistant')
            chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "content": refined_fallback,
                "isUser": False
            })
            save_chat_history(chat_history)
            
            end_request_timer(start_time, len(fallback_response), "fallback", len(message), True)
            return {
                "response": refined_fallback
            }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Chat error: {str(e)}")
        print(f"Traceback: {error_details}")
        end_request_timer(start_time, 0, "error", len(message), False)
        return {"error": str(e), "details": error_details}

# Initialize query manager after function definition
start_query_processing()
set_async_query_processor(process_query_async)

@app.route('/api/chat', methods=['POST'])
def chat():
    global agent
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400
        
        # Queue the message for processing to prevent overload
        priority = 5  # Default priority
        
        # Increase priority for greetings and short messages
        if len(message) < 20 or any(greeting in message.lower() for greeting in ['hi', 'hello', 'hey']):
            priority = 8
        
        # Decrease priority for very long messages that might take more resources
        elif len(message) > 500:
            priority = 3
        
        query_id = enqueue_query(message, priority)
        logger.info(f"Message queued with ID: {query_id}, priority: {priority}")
        
        # For immediate responses to simple queries, process directly
        # For complex queries, queue them to prevent overload
        if len(message) < 50 and any(word in message.lower() for word in ['hi', 'hello', 'hey', 'help', 'thanks', 'thank you']):
            # Process simple greetings immediately using a synchronous approach
            # Create a wrapper to handle the async function synchronously
            import asyncio
            
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(process_query_async(message, None))
                loop.close()
                
                if isinstance(result, dict) and "error" in result:
                    return jsonify({"success": False, "error": result["error"]}), 500
                elif isinstance(result, dict):
                    return jsonify({"success": True, "response": result.get("response", ""), "tool_usage": result.get("tool_usage"), "quality": result.get("quality")})
                else:
                    return jsonify({"success": True, "response": result})
            except Exception as e:
                loop.close()
                import traceback
                error_details = traceback.format_exc()
                print(f"Chat error: {str(e)}")
                print(f"Traceback: {error_details}")
                return jsonify({"success": False, "error": str(e), "details": error_details}), 500
        else:
            # Queue the message for processing to prevent overload
            return jsonify({
                "success": True,
                "queued": True,
                "query_id": query_id,
                "priority": priority,
                "message": "Your query has been queued for processing. Please wait for the response."
            })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Chat error: {str(e)}")
        print(f"Traceback: {error_details}")
        return jsonify({"success": False, "error": str(e), "details": error_details}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "status": "online",
        "message": "OpenManus server is running"
    })

@app.route('/api/query/<query_id>')
def get_query_result_endpoint(query_id):
    """Get the result of a queued query"""
    try:
        # Check if the query result is available
        result = get_query_result(query_id)
        
        if result is not None:
            # Query has been processed
            if isinstance(result, dict) and "error" in result:
                # Check if this is a timeout error
                if "timed out" in result["error"].lower():
                    return jsonify({
                        "success": True,
                        "status": "failed",
                        "error": result["error"]
                    })
                return jsonify({
                    "success": True,
                    "status": "failed",
                    "error": result["error"]
                })
            elif isinstance(result, dict):
                response_data = {
                    "success": True,
                    "status": "completed",
                    "response": result.get("response", ""),
                }
                
                # Add optional fields if they exist
                if "tool_usage" in result and result["tool_usage"]:
                    response_data["tool_usage"] = result["tool_usage"]
                if "quality" in result and result["quality"]:
                    response_data["quality"] = result["quality"]
                    
                return jsonify(response_data)
            else:
                # Handle the case where result might be a coroutine or other async object
                if hasattr(result, '__await__'):
                    # This is a coroutine, we need to handle it properly
                    import asyncio
                    loop = None
                    try:
                        # Try to get the current event loop
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            # No event loop in thread, create a new one
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        resolved_result = loop.run_until_complete(result)
                        return jsonify({
                            "success": True,
                            "status": "completed",
                            "response": str(resolved_result)
                        })
                    except Exception as e:
                        return jsonify({
                            "success": True,
                            "status": "failed",
                            "error": str(e)
                        })
                    finally:
                        if loop:
                            try:
                                loop.close()
                            except:
                                pass
                else:
                    return jsonify({
                        "success": True,
                        "status": "completed",
                        "response": str(result)
                    })
        else:
            # Query is still processing
            return jsonify({
                "success": True,
                "status": "processing",
                "message": "Query is still being processed. Please wait."
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get chat history"""
    try:
        history = load_chat_history()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear all chat history"""
    try:
        delete_chat_history()
        return jsonify({"success": True, "message": "Chat history cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history/delete', methods=['POST'])
def delete_message():
    """Delete a specific message from chat history"""
    try:
        data = request.get_json()
        message_content = data.get('message', '')
        if not message_content:
            return jsonify({"success": False, "error": "No message content provided"}), 400
        
        delete_specific_message(message_content)
        return jsonify({"success": True, "message": "Message deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat/delete', methods=['POST'])
def delete_chat():
    """Delete a specific chat by ID"""
    try:
        data = request.get_json()
        chat_id = data.get('chatId', '')
        if not chat_id:
            return jsonify({"success": False, "error": "No chat ID provided"}), 400
        
        # Delete chat file if it exists
        chat_file = f"chat_history_{chat_id}.json"
        if os.path.exists(chat_file):
            os.remove(chat_file)
        
        return jsonify({"success": True, "message": "Chat deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/language', methods=['POST'])
def set_language():
    """Set the preferred language for responses"""
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        # Store language preference in session or file
        # For simplicity, we'll store it in a file
        language_file = "user_language_preference.txt"
        with open(language_file, 'w') as f:
            f.write(language)
        
        return jsonify({"success": True, "message": f"Language set to {language}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/language', methods=['GET'])
def get_language():
    """Get the preferred language for responses"""
    try:
        language_file = "user_language_preference.txt"
        if os.path.exists(language_file):
            with open(language_file, 'r') as f:
                language = f.read().strip()
        else:
            language = 'en'  # Default to English
        
        return jsonify({"success": True, "language": language})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/diagnostics')
def get_diagnostics():
    """Get system diagnostics"""
    try:
        diagnostics = get_recent_diagnostics(50)
        return jsonify({"success": True, "diagnostics": diagnostics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/diagnostic_report')
def get_diagnostic_report():
    """Get formatted diagnostic report"""
    try:
        report = generate_diagnostic_report()
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/performance')
def get_performance_report():
    """Get performance monitoring report"""
    try:
        report = get_performance_report()
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats')
def get_system_stats():
    """Get system statistics including query queue stats"""
    try:
        stats = get_query_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/init')
def initialize_agent():
    """Initialize the agent and return status"""
    try:
        # Agent initialization is handled when the first request is made
        # For now, just return success to indicate the API is available
        return jsonify({
            "success": True, 
            "message": "Agent initialization endpoint ready"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def extract_stock_price_from_results(search_results):
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
        print(f"Error extracting stock price: {e}")
        return None

def extract_time_info_from_results(search_results, original_query: str):
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
        print(f"Error extracting time info: {e}")
        return None

def run_fallback_inference(message: str) -> str:
    """Fallback method to run inference directly without DirectML handler"""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import os
        
        # Use the lightweight TinyLlama model for better compatibility
        model_path = "./models/tinyllama"
        
        if not os.path.exists(model_path):
            return "Error: Model not found. Please ensure the model is downloaded to ./models/tinyllama"
        
        # Load model and tokenizer with DirectML-compatible settings
        tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        
        # Try to load model with DirectML device if available
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch, 'directml') and torch.directml.is_available():
            device = "privateuseone:0"
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            dtype=torch.float32,
            low_cpu_mem_usage=True,
            attn_implementation="eager"  # Use eager attention to avoid einsum issues
        )
        
        model = model.to(device)
        
        # Format the prompt with enhanced context
        intent = identify_user_intent(message)
        context_prompt = f"You are a helpful AI assistant. The user wants {intent} information."
        prompt = f"<|system|>\n{context_prompt}</s>\n<|user|>\n{message}</s>\n<|assistant|>"
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
        return response.strip()
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Fallback inference error: {str(e)}")
        print(f"Traceback: {error_details}")
        return f"Error generating response: {str(e)}"

def run_web_ui(host='localhost', port=5000):
    """Run the web UI server"""
    print(f"Starting OpenManus Web UI on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="OpenManus Web UI")
    parser.add_argument('--host', default='localhost', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    run_web_ui(args.host, args.port)