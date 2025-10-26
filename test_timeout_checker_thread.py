#!/usr/bin/env python
"""
Test that waits for the timeout checker thread to run
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Add debug prints to the timeout checker loop
original_timeout_checker_loop = query_manager._timeout_checker_loop

def debug_timeout_checker_loop(self):
    """Debug version of timeout checker loop"""
    print("DEBUG: Timeout checker loop started")
    while self.is_running:
        try:
            print("DEBUG: Timeout checker loop iteration")
            # Check for timed out queries every 30 seconds
            timed_out_queries = self.queue.check_timeouts()
            if timed_out_queries:
                print(f"DEBUG: Found timed out queries: {timed_out_queries}")
            for query_id in timed_out_queries:
                print(f"DEBUG: Storing timeout error for query {query_id}")
                # Store timeout error result
                self.store_query_result(query_id, {
                    "error": "Query processing timed out after 5 minutes"
                })
                print(f"DEBUG: Stored timeout error for query {query_id}")
            print("DEBUG: Sleeping for 5 seconds (reduced for testing)")
            time.sleep(5)  # Reduced for testing
        except Exception as e:
            print(f"DEBUG: Error in timeout checker loop: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)  # Reduced for testing

# Patch the timeout checker loop
query_manager._timeout_checker_loop = debug_timeout_checker_loop.__get__(query_manager)

# Processor that takes a long time
async def slow_processor(message, query_obj):
    """Processor that takes a long time"""
    print(f"Processing (slow): {message}")
    await asyncio.sleep(60)  # 60 seconds
    return f"Slow response to: {message}"

def test_timeout_checker_thread():
    """Test timeout checker thread"""
    print("🧵 Timeout Checker Thread Test")
    print("=" * 30)
    
    # Set up the processor
    print("Setting slow processor...")
    set_async_query_processor(slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Check if threads are running
    print(f"Worker thread alive: {query_manager.worker_thread.is_alive() if query_manager.worker_thread else 'No thread'}")
    print(f"Timeout checker thread alive: {query_manager.timeout_checker_thread.is_alive() if query_manager.timeout_checker_thread else 'No thread'}")
    
    # Simulate what happens in the web UI chat endpoint
    print("\n1. Enqueuing a query...")
    message = "This is a test message that will timeout"
    priority = 5
    
    # This is what happens in the web UI chat endpoint
    query_id = enqueue_query(message, priority)
    print(f"   Query enqueued with ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(2)
    
    # Manually set a short timeout for testing
    print("   Manually setting short timeout...")
    with query_manager.queue.lock:
        # Set timeout to be in the past (already expired)
        query_manager.queue.processing_timeouts[query_id] = time.time() - 5
        print(f"   Set timeout for query {query_id} to {query_manager.queue.processing_timeouts[query_id]}")
        print(f"   Current time: {time.time()}")
    
    # Check initial results
    with query_manager.results_lock:
        print(f"   Initial results dict: {dict(query_manager.results)}")
    
    # Wait for timeout checker to run (10 seconds)
    print("   Waiting 10 seconds for timeout checker to run...")
    time.sleep(10)
    
    # Check results after timeout checker should have run
    with query_manager.results_lock:
        print(f"   Results dict after timeout checker: {dict(query_manager.results)}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Final result: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Timeout Checker Thread Test")
    print("=" * 35)
    
    result = test_timeout_checker_thread()
    
    print("\n" + "=" * 35)
    if result and isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout checker thread working correctly!")
    else:
        print("❌ Timeout checker thread may have issues!")
        print(f"   Result: {result}")
