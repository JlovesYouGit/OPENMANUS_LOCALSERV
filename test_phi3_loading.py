#!/usr/bin/env python
"""
Test script to verify Phi-3 model loading with DirectML optimizations
"""

import os
import sys
import torch
import asyncio
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.directml_optimized_handler import DirectMLOptimizedHandler

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test loading the Phi-3 model with DirectML optimizations"""
    print("🔍 Testing Phi-3 model loading with DirectML optimizations...")
    
    # Check if DirectML is available
    try:
        import torch_directml
        if torch_directml.is_available():
            print("✅ DirectML is available")
            dml_device = torch_directml.device()
            print(f"🎮 DirectML device: {dml_device}")
            
            # Check available memory
            try:
                if hasattr(torch_directml, 'get_device_properties'):
                    props = torch_directml.get_device_properties(dml_device)
                    total_memory = props.total_memory
                    total_memory_gb = total_memory / (1024**3)
                    print(f"📊 DirectML GPU total memory: {total_memory_gb:.2f}GB")
            except Exception as e:
                print(f"⚠️ Could not get DirectML device properties: {e}")
        else:
            print("⚠️ DirectML is not available")
            return False
    except ImportError:
        print("⚠️ torch_directml not installed")
        return False
    
    # Configuration for testing
    config = {
        "llm": {
            "reasoning": {
                "model_path": "./models/phi-3-mini",
                "max_tokens": 512,
                "temperature": 0.7
            }
        }
    }
    
    try:
        # Initialize the handler
        print("🔄 Initializing DirectML handler...")
        handler = DirectMLOptimizedHandler(config)
        print(f"✅ Handler initialized with device: {handler.device}")
        
        # Test loading the Phi-3 model
        print("📥 Loading Phi-3 model...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(handler.load_model_on_demand("phi3"))
            if result:
                print("✅ Phi-3 model loaded successfully!")
                print(f"📝 Model info: {handler.get_model_info()}")
                
                # Test generating a simple response
                print("💬 Testing model response generation...")
                messages = [
                    {"role": "user", "content": "Hello, how are you?"}
                ]
                
                response = handler._generate_response_transformers(
                    "phi3",
                    handler.tokenizers["phi3"],
                    handler.models["phi3"],
                    messages,
                    max_tokens=100,
                    temperature=0.7,
                    start_time=0,
                    tokens_generated=0
                )
                
                print(f"🤖 Model response: {response}")
                print("🎉 All tests passed!")
                return True
            else:
                print("❌ Failed to load Phi-3 model")
                return False
        except Exception as e:
            print(f"❌ Error during model loading: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ Error initializing handler: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)