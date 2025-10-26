#!/usr/bin/env python
"""
Direct model test to verify our fixes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.directml_optimized_handler import DirectMLOptimizedHandler
from app.config import config
import asyncio

async def test_direct_model():
    """Test the model directly"""
    print("Testing DirectML model loading and inference...")
    
    # Create handler
    handler = DirectMLOptimizedHandler(config._load_config())
    
    # Test simple query
    print("\n1. Testing simple greeting...")
    try:
        response = await handler.chat_with_agent("lightweight", "Hello, how are you?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test more complex query
    print("\n2. Testing complex query...")
    try:
        response = await handler.chat_with_agent("reasoning", "What is the capital of France?")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test analytical query
    print("\n3. Testing analytical query...")
    try:
        response = await handler.chat_with_agent("reasoning", "Explain quantum computing in simple terms")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_model())