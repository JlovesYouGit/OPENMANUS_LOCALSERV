#!/usr/bin/env python
"""
Test script to verify Qwen2-0.5B model loading and inference
"""

import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.directml_fixed_handler import DirectMLFixedHandler

def test_model_loading():
    """Test loading the Qwen2-0.5B model"""
    print("🔍 Testing Qwen2-0.5B model loading...")
    
    # Configuration for testing
    config = {
        "llm": {
            "reasoning": {
                "model_path": "./models/qwen2-0.5b",
                "max_tokens": 512,
                "temperature": 0.7
            }
        }
    }
    
    try:
        # Initialize the handler
        print("🔄 Initializing DirectML handler...")
        handler = DirectMLFixedHandler(config)
        print(f"✅ Handler initialized with device: {handler.device}")
        
        # Test loading the Qwen2-0.5B model
        print("📥 Loading Qwen2-0.5B model...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(handler.load_model_on_demand("qwen2-0.5b"))
            if result:
                print("✅ Qwen2-0.5B model loaded successfully!")
                print(f"📝 Model info: {handler.get_model_info()}")
                
                # Test generating a simple response
                print("💬 Testing model response generation...")
                messages = [
                    {"role": "user", "content": "Hello, how are you?"}
                ]
                
                response = handler._generate_response_transformers(
                    "qwen2-0.5b",
                    handler.tokenizers["qwen2-0.5b"],
                    handler.models["qwen2-0.5b"],
                    messages,
                    max_tokens=100,
                    temperature=0.7,
                    start_time=0,
                    tokens_generated=0
                )
                print(f"📝 Response: {response}")
                
                return True
            else:
                print("❌ Failed to load Qwen2-0.5B model")
                return False
        except Exception as e:
            print(f"❌ Error loading Qwen2-0.5B model: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ Error initializing handler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_loading()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)