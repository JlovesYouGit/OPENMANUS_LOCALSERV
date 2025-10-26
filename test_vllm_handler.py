#!/usr/bin/env python
"""
Test script to check VLLM handler initialization
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vllm_handler():
    """Test VLLM handler initialization"""
    print("🔍 Testing VLLM handler initialization...")
    
    try:
        print("Importing VLLM handler...")
        from app.vllm_optimized_handler import VLLMOptimizedHandler
        print("✅ VLLM handler class imported")
        
        # Create a minimal config
        config = {
            "llm": {
                "lightweight": {
                    "model_path": "./models/tinyllama",
                    "max_tokens": 1024,
                    "temperature": 0.5
                },
                "reasoning": {
                    "model_path": "./models/phi-3-mini",
                    "max_tokens": 2048,
                    "temperature": 0.7
                }
            }
        }
        
        print("Creating VLLM handler instance...")
        handler = VLLMOptimizedHandler(config)
        print("✅ VLLM handler instance created successfully")
        
        return True
    except Exception as e:
        print(f"❌ VLLM handler initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting VLLM handler test...")
    
    success = test_vllm_handler()
    
    if success:
        print("\n🎉 VLLM handler test passed!")
    else:
        print("\n❌ VLLM handler test failed.")
    
    sys.exit(0 if success else 1)