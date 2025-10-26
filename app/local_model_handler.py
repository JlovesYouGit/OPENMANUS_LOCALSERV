"""
Local Model Handler for OpenManus
This module manages local LLM inference for both lightweight and reasoning agents.
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class LocalModelHandler:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the local model handler with configuration.
        
        Args:
            config: Configuration dictionary containing model paths and settings
        """
        self.config = config
        self.models = {}
        self.tokenizers = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing LocalModelHandler with device: {self.device}")
        
    async def load_models(self):
        """Load all configured local models asynchronously."""
        try:
            # Load lightweight model (TinyLlama)
            lightweight_config = self.config.get("llm", {}).get("lightweight", {})
            if lightweight_config:
                await self._load_model("tinyllama", lightweight_config)
            
            # Load reasoning model (Phi-3 Mini)
            reasoning_config = self.config.get("llm", {}).get("reasoning", {})
            if reasoning_config:
                await self._load_model("phi3", reasoning_config)
                
            logger.info("✅ All local models loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading local models: {e}")
            return False
    
    async def _load_model(self, model_name: str, model_config: Dict[str, Any]):
        """Load a specific model asynchronously."""
        try:
            model_path = model_config.get("model_path")
            if not model_path or not os.path.exists(model_path):
                raise ValueError(f"Model path not found: {model_path}")
            
            logger.info(f"📥 Loading {model_name} model from: {model_path}")
            
            # Load tokenizer
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            # Load model
            self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                device_map="auto"
            )
            
            logger.info(f"✅ {model_name} model loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading {model_name} model: {e}")
            raise
    
    def generate_response(self, model_type: str, messages: List[Dict[str, str]], 
                         max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Generate a response using the specified local model.
        
        Args:
            model_type: Type of model to use ("tinyllama" or "phi3")
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} not loaded")
        
        try:
            tokenizer = self.tokenizers[model_type]
            model = self.models[model_type]
            
            # Format messages for the model
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs, 
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response = tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[-1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating response with {model_type}: {e}")
            return f"Error generating response: {str(e)}"
    
    async def chat_with_agent(self, agent_type: str, user_input: str, 
                             context: Optional[str] = None) -> str:
        """
        Chat with a specific agent type.
        
        Args:
            agent_type: Type of agent ("lightweight" or "reasoning")
            user_input: User's message
            context: Additional context for the conversation
            
        Returns:
            Agent's response
        """
        # Map agent types to model types
        model_mapping = {
            "lightweight": "tinyllama",
            "reasoning": "phi3"
        }
        
        model_type = model_mapping.get(agent_type)
        if not model_type:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Get model configuration
        model_config = self.config.get("llm", {}).get(agent_type, {})
        max_tokens = model_config.get("max_tokens", 100)
        temperature = model_config.get("temperature", 0.7)
        
        # Prepare messages
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self.generate_response(
            model_type, messages, max_tokens, temperature
        )
        
        return response
    
    async def coordinate_agents(self, task: str) -> Dict[str, str]:
        """
        Coordinate both agents to work on a task.
        
        Args:
            task: Task description
            
        Returns:
            Dictionary with responses from both agents
        """
        logger.info(f"🤖 Coordinating agents for task: {task}")
        
        # Get lightweight agent's quick response
        lightweight_response = await self.chat_with_agent(
            "lightweight", 
            f"Quickly analyze this task: {task}"
        )
        
        # Get reasoning agent's detailed response
        reasoning_response = await self.chat_with_agent(
            "reasoning",
            f"Provide a detailed analysis of this task: {task}",
            f"Quick analysis from lightweight agent: {lightweight_response}"
        )
        
        return {
            "lightweight_agent": lightweight_response,
            "reasoning_agent": reasoning_response
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about loaded models."""
        info = {}
        for model_name in self.models.keys():
            info[model_name] = {
                "status": "loaded",
                "device": self.device,
                "path": self.config.get("llm", {}).get(model_name, {}).get("model_path", "unknown")
            }
        return info

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "llm": {
            "lightweight": {
                "model_path": "./models/tinyllama/TinyLlama-1.1B-Chat-v1.0",
                "max_tokens": 1024,
                "temperature": 0.5
            },
            "reasoning": {
                "model_path": "./models/phi-3-mini/Phi-3-mini-4k-instruct",
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
    }
    
    # Initialize and test
    handler = LocalModelHandler(config)
    print("Local Model Handler initialized!")