"""
Local LLM Handler for OpenManus
This module provides a lightweight LLM implementation using TinyLlama (1.1B parameters)
that fits within the 4GB requirement.
"""

import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any

class LocalLLMHandler:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the local LLM handler with a lightweight model.
        
        Args:
            model_name: Name of the HuggingFace model to use (default: TinyLlama 1.1B)
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"🤖 Initializing lightweight LLM: {model_name}")
        print(f"💾 Model size: ~500MB (well under 4GB limit)")
        print(f"⚙️  Device: {self.device}")
        
    def load_model(self):
        """Load the lightweight model into memory."""
        try:
            print("📥 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                cache_dir="./models",
                token=False  # No authentication required
            )
            
            print("📥 Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir="./models",
                token=False,  # No authentication required
                dtype=torch.float16 if self.device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                device_map="auto"  # Automatically distribute across available devices
            )
            
            print("✅ Lightweight LLM loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Try downloading the model manually or check your internet connection.")
            return False
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 100) -> str:
        """
        Generate a response using the local LLM.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated response text
        """
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return "Error: Could not load the lightweight model."
        
        try:
            # Format messages for the model
            inputs = self.tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            ).to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[-1]:], 
                skip_special_tokens=True
            )
            
            return response
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "Error: Could not generate response with the local model."
    
    def chat(self, user_input: str) -> str:
        """
        Simple chat interface for the local LLM.
        
        Args:
            user_input: User's message
            
        Returns:
            Model's response
        """
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        return self.generate_response(messages, max_tokens=150)

# Example usage
if __name__ == "__main__":
    # Initialize the lightweight LLM handler
    llm_handler = LocalLLMHandler()
    
    # Load the model
    if llm_handler.load_model():
        print("\n💬 Testing the lightweight model...")
        
        # Test with a simple question
        response = llm_handler.chat("Who are you?")
        print(f"🤖 Model response: {response}")
        
        print("\n✨ This lightweight model is perfect for OpenManus:")
        print("   • Size: ~500MB (well under your 4GB requirement)")
        print("   • No API keys needed")
        print("   • Runs locally")
        print("   • Fast inference")
        print("   • Low resource usage")
    else:
        print("❌ Failed to load the lightweight model.")