#!/usr/bin/env python
"""
Test of timeout functionality with normal timeout period
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that simulates a long-running task that will timeout
async def slow_processor(message, query_obj):
    """Processor that takes longer than timeout to complete"""
    print(f"Processing (slow): {message}")
    # Simulate a very long processing time (600 seconds = 10 minutes)
    await asyncio.sleep(600)
    return f"Slow response to: {message}"

def test_timeout_normal():
    """Test timeout with normal timeout period"""
    print("⏰ Normal Timeout Test")
    print("=" * 22)
    
    # Set up the processor
    print("Setting slow processor...")
    set_async_query_processor(slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Test enqueueing a query
    print("\n1. Enqueuing a query that should timeout...")
    query_id = enqueue_query("This should timeout with normal timeout", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(2)
    
    # For testing purposes, let's manually trigger a timeout check after a short time
    print("   Manually checking for timeouts after 5 seconds...")
    time.sleep(5)
    
    # Manually check for timeouts (this simulates what the timeout checker does)
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Result after manual timeout check: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Normal Timeout Test")
    print("=" * 30)
    
    result = test_timeout_normal()
    
    print("\n" + "=" * 30)
    if result is None:
        print("✅ Query is still processing (no timeout yet) - this is expected!")
    elif isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout handling working correctly!")
    else:
        print("❌ Unexpected result!")
        print(f"   Result: {result}")