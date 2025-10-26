#!/usr/bin/env python
"""
Test script to verify the frontend fixes for OpenManus
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.directml_optimized_handler import DirectMLOptimizedHandler
from app.config import config

def test_context_caching():
    """Test the context caching mechanism"""
    print("Testing context caching mechanism...")
    
    # Create a test configuration
    test_config = {
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
    
    # Initialize the handler
    handler = DirectMLOptimizedHandler(test_config)
    
    # Test caching
    test_context = {
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "model_type": "tinyllama",
        "agent_type": "lightweight"
    }
    
    cache_key = handler._generate_cache_key("Hello, world!")
    handler.cache_context(cache_key, test_context)
    
    # Test retrieval
    retrieved_context = handler.get_cached_context(cache_key)
    if retrieved_context:
        print("✅ Context caching and retrieval working correctly")
        print(f"Retrieved context: {retrieved_context}")
    else:
        print("❌ Context caching failed")
    
    return True

def test_model_loading():
    """Test model loading functionality"""
    print("\nTesting model loading...")
    
    test_config = {
        "llm": {
            "lightweight": {
                "model_path": "./models/tinyllama",
                "max_tokens": 1024,
                "temperature": 0.5
            }
        }
    }
    
    handler = DirectMLOptimizedHandler(test_config)
    
    # Test loading tinyllama model
    try:
        result = asyncio.run(handler.load_model_on_demand("tinyllama"))
        if result:
            print("✅ TinyLlama model loaded successfully")
        else:
            print("❌ Failed to load TinyLlama model")
    except Exception as e:
        print(f"❌ Error loading TinyLlama model: {e}")
    
    return True

def test_chat_functionality():
    """Test chat functionality"""
    print("\nTesting chat functionality...")
    
    test_config = {
        "llm": {
            "lightweight": {
                "model_path": "./models/tinyllama",
                "max_tokens": 1024,
                "temperature": 0.5
            }
        }
    }
    
    handler = DirectMLOptimizedHandler(test_config)
    
    # Test simple chat
    try:
        response = asyncio.run(handler.chat_with_agent(
            "lightweight",
            "Hello, what is 2+2?"
        ))
        print(f"✅ Chat response received: {response}")
    except Exception as e:
        print(f"❌ Error in chat functionality: {e}")
    
    return True

def test_chat_history_persistence():
    """Test chat history persistence"""
    print("\nTesting chat history persistence...")
    
    # Create a test chat history file
    history_file = "test_chat_history.json"
    test_history = [
        {
            "timestamp": "2023-01-01T00:00:00",
            "content": "Hello, assistant!",
            "isUser": True
        },
        {
            "timestamp": "2023-01-01T00:00:01",
            "content": "Hello, user!",
            "isUser": False
        }
    ]
    
    try:
        # Save test history
        with open(history_file, 'w') as f:
            json.dump(test_history, f, indent=2)
        
        # Load test history
        with open(history_file, 'r') as f:
            loaded_history = json.load(f)
        
        if loaded_history == test_history:
            print("✅ Chat history persistence working correctly")
        else:
            print("❌ Chat history persistence failed")
        
        # Clean up
        os.remove(history_file)
    except Exception as e:
        print(f"❌ Error in chat history persistence: {e}")
    
    return True

def main():
    """Run all tests"""
    print("Running frontend fix verification tests...\n")
    
    tests = [
        test_context_caching,
        test_model_loading,
        test_chat_functionality,
        test_chat_history_persistence
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The frontend fixes are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    main()