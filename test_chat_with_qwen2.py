#!/usr/bin/env python
"""
Test script to verify chat_with_agent method with Qwen2-0.5B model
"""

import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.directml_fixed_handler import DirectMLFixedHandler

async def test_chat_with_agent():
    """Test the chat_with_agent method with Qwen2-0.5B model"""
    print("🔍 Testing chat_with_agent method with Qwen2-0.5B model...")
    
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
        
        # Test chat_with_agent with reasoning agent type
        print("💬 Testing chat_with_agent with reasoning agent...")
        response = await handler.chat_with_agent(
            "reasoning",
            "Hello, what is 2+2?"
        )
        print(f"📝 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing chat_with_agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_chat_with_agent())
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)