#!/usr/bin/env python
"""
Test script with debug output for timeout handling
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
        # Set timeout for processing (3 seconds for testing)
        self.processing_timeouts[query.id] = time.time() + 3
        
        print(f"Query {query.id} started processing with 3-second timeout")
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

def test_timeout_debug():
    """Test timeout with debug output"""
    print("🔍 Timeout Test with Debug")
    print("=" * 25)
    
    # Set up the processor
    print("Setting slow processor...")
    set_async_query_processor(slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Test enqueueing a query
    print("\n1. Enqueuing a query that should timeout...")
    query_id = enqueue_query("Debug timeout test", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(1)
    
    # Check processing timeouts
    with query_manager.queue.lock:
        print(f"   Processing timeouts: {dict(query_manager.queue.processing_timeouts)}")
    
    # Wait for timeout to occur (4 seconds to be safe)
    print("   Waiting for timeout (4 seconds)...")
    time.sleep(4)
    
    # Check if timeout checker detected it
    print("   Checking results after timeout...")
    with query_manager.results_lock:
        print(f"   Results dict: {dict(query_manager.results)}")
    
    # Manually check for timeouts
    print("   Manually checking for timeouts...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check results again
    with query_manager.results_lock:
        print(f"   Results dict after manual check: {dict(query_manager.results)}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Final result: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Timeout Debug Test")
    print("=" * 30)
    
    result = test_timeout_debug()
    
    print("\n" + "=" * 30)
    if result and isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout handling working correctly!")
    else:
        print("❌ Timeout handling may have issues!")
        print(f"   Result: {result}")