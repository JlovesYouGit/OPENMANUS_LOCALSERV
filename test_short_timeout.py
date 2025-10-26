#!/usr/bin/env python
"""
Test script to verify timeout functionality with short timeout
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result
import app.utils.query_manager as query_module

# Override the timeout for testing
original_get_next_query = query_module.QueryQueue.get_next_query

def patched_get_next_query(self):
    """Patched version that sets a short timeout for testing"""
    with self.lock:
        if not self.queue:
            return None
        
        # Get highest priority query
        query = self.queue.popleft()
        query.status = 'processing'
        query.processing_start_time = time.time()
        self.processing.add(query.id)
        # Set timeout for processing (5 seconds for testing)
        self.processing_timeouts[query.id] = time.time() + 5
        
        print(f"Query {query.id} started processing with 5-second timeout")
        return query

# Apply the patch
query_module.QueryQueue.get_next_query = patched_get_next_query

# Processor that simulates a long-running task
async def slow_processor(message, query_obj):
    """Processor that takes a long time to complete"""
    print(f"Processing (slow): {message}")
    # Simulate a very long processing time (10 seconds)
    await asyncio.sleep(10)
    return f"Slow response to: {message}"

def test_short_timeout():
    """Test short timeout scenario"""
    print("⏰ Testing Short Timeout Scenario")
    print("=" * 35)
    
    # Set up the processor
    print("Setting slow processor...")
    set_async_query_processor(slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Test enqueueing a query
    print("\n1. Enqueuing a query that should timeout...")
    query_id = enqueue_query("This should timeout quickly", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(2)
    
    # Check stats
    from app.utils.query_manager import get_query_stats
    stats = get_query_stats()
    print(f"   Stats: {stats}")
    
    # Wait for timeout to occur (6 seconds to be safe)
    print("   Waiting for timeout (6 seconds)...")
    time.sleep(6)
    
    # Manually check for timeouts
    print("   Manually checking for timeouts...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Result: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Short Timeout Test")
    print("=" * 30)
    
    result = test_short_timeout()
    
    print("\n" + "=" * 30)
    if result and isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout handling working correctly!")
    else:
        print("❌ Timeout handling may have issues!")
        print(f"   Result: {result}")