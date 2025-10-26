#!/usr/bin/env python
"""
Test script to verify the GPU memory and query timeout fixes
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result
from app.directml_optimized_handler import DirectMLOptimizedHandler

# Simple test processor that simulates model response
async def test_processor(message, query_obj):
    """Test processor that simulates model response"""
    print(f"Processing: {message}")
    # Simulate some processing time
    await asyncio.sleep(2)
    return f"Response to: {message}"

def test_query_management():
    """Test the query management system"""
    print("🔧 Testing Query Management System")
    print("=" * 40)
    
    # Set up the processor
    set_async_query_processor(test_processor)
    start_query_processing()
    
    # Test enqueueing a query
    print("1. Testing query enqueue...")
    query_id = enqueue_query("Hello, world!", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Test getting query result
    print("2. Testing query result retrieval...")
    max_wait = 15
    wait_time = 0
    result = None
    
    while wait_time < max_wait:
        result = get_query_result(query_id)
        if result is not None:
            break
        print(f"   Waiting for result... ({wait_time}s)")
        time.sleep(1)
        wait_time += 1
    
    if result:
        print(f"   ✅ Query completed successfully: {result}")
        return True
    else:
        print(f"   ❌ Query failed or timed out")
        return False

def test_gpu_memory_detection():
    """Test GPU memory detection"""
    print("\n🖥️  Testing GPU Memory Detection")
    print("=" * 35)
    
    try:
        # Test DirectML handler initialization
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
        
        handler = DirectMLOptimizedHandler(config)
        print(f"   ✅ DirectML handler initialized with device: {handler.device}")
        
        # Test device selection logic
        device = handler._get_optimal_device()
        print(f"   🎯 Optimal device selected: {device}")
        
        return True
    except Exception as e:
        print(f"   ❌ GPU memory detection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting GPU Memory and Query Timeout Fix Test")
    print("=" * 50)
    
    # Test GPU memory detection
    gpu_test_passed = test_gpu_memory_detection()
    
    # Test query management
    query_test_passed = test_query_management()
    
    print("\n" + "=" * 50)
    if gpu_test_passed and query_test_passed:
        print("✅ All tests passed! GPU memory and query timeout issues should be fixed.")
    else:
        print("❌ Some tests failed. There may still be issues.")
        if not gpu_test_passed:
            print("   - GPU memory detection failed")
        if not query_test_passed:
            print("   - Query management failed")