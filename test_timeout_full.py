#!/usr/bin/env python
"""
Full test of timeout functionality waiting for timeout checker loop
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that simulates a long-running task that will definitely timeout
async def very_slow_processor(message, query_obj):
    """Processor that takes longer than timeout to complete"""
    print(f"Processing (very slow): {message}")
    # Simulate a very long processing time (300 seconds = 5 minutes)
    await asyncio.sleep(300)
    return f"Very slow response to: {message}"

def test_timeout_full():
    """Test timeout with full wait for timeout checker"""
    print("⏰ Full Timeout Test")
    print("=" * 20)
    
    # Set up the processor
    print("Setting very slow processor...")
    set_async_query_processor(very_slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Test enqueueing a query
    print("\n1. Enqueuing a query that should timeout...")
    query_id = enqueue_query("This should definitely timeout", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(2)
    
    # Wait long enough for timeout checker to run and detect timeout (35 seconds)
    print("   Waiting 35 seconds for timeout checker to detect timeout...")
    time.sleep(35)
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Final result: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Full Timeout Test")
    print("=" * 25)
    
    result = test_timeout_full()
    
    print("\n" + "=" * 25)
    if result and isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout handling working correctly!")
    else:
        print("❌ Timeout handling may have issues!")
        print(f"   Result: {result}")
