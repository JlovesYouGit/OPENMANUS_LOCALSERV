#!/usr/bin/env python
"""
Test script to simulate query timeout scenario
"""

import sys
import os
import time
import asyncio
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that simulates a long-running task
async def slow_processor(message, query_obj):
    """Processor that takes a long time to complete"""
    print(f"Processing (slow): {message}")
    # Simulate a very long processing time (10 seconds)
    await asyncio.sleep(10)
    return f"Slow response to: {message}"

def test_timeout_scenario():
    """Test timeout scenario"""
    print("⏰ Testing Timeout Scenario")
    print("=" * 30)
    
    # Set up the processor
    print("Setting slow processor...")
    set_async_query_processor(slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Test enqueueing a query
    print("\n1. Enqueuing a query that will timeout...")
    query_id = enqueue_query("This should timeout", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Wait for a bit to let it start processing
    print("   Waiting for query to start processing...")
    time.sleep(2)
    
    # Check if it's being processed
    from app.utils.query_manager import get_query_stats
    stats = get_query_stats()
    print(f"   Stats: {stats}")
    
    # Now let's manually trigger a timeout check
    print("   Manually checking for timeouts...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Result: {result}")
    
    # Wait a bit more and check again
    print("   Waiting 5 more seconds...")
    time.sleep(5)
    
    # Check result again
    result = get_query_result(query_id)
    print(f"   Result after waiting: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Timeout Test")
    print("=" * 25)
    
    result = test_timeout_scenario()
    
    print("\n" + "=" * 25)
    if result and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout handling working correctly!")
    else:
        print("❌ Timeout handling may have issues!")
        print(f"   Result: {result}")