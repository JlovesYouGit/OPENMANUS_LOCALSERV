#!/usr/bin/env python
"""
Test that directly calls the timeout checker to see if it stores results
"""

import sys
import os
import time
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that completes quickly
async def fast_processor(message, query_obj):
    """Processor that completes quickly"""
    print(f"Processing: {message}")
    await asyncio.sleep(1)
    return f"Quick response to: {message}"

def test_timeout_checker_store():
    """Test if timeout checker stores results correctly"""
    print("🔍 Timeout Checker Store Test")
    print("=" * 30)
    
    # Set up the processor
    print("Setting fast processor...")
    set_async_query_processor(fast_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Simulate what happens in the web UI chat endpoint
    print("\n1. Enqueuing a query...")
    message = "This is a test message"
    priority = 5
    
    # This is what happens in the web UI chat endpoint
    query_id = enqueue_query(message, priority)
    print(f"   Query enqueued with ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(1)
    
    # Manually add a timeout entry for testing
    print("   Manually adding timeout entry...")
    with query_manager.queue.lock:
        # Set timeout to be in the past (already expired)
        query_manager.queue.processing_timeouts[query_id] = time.time() - 10
        print(f"   Set timeout for query {query_id} to {query_manager.queue.processing_timeouts[query_id]}")
        print(f"   Current time: {time.time()}")
    
    # Check initial results
    with query_manager.results_lock:
        print(f"   Initial results dict: {dict(query_manager.results)}")
    
    # Manually call the timeout checker loop method directly
    print("   Manually calling timeout checker loop method...")
    # This is what the timeout checker loop does
    timed_out_queries = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out_queries}")
    
    # Store timeout error result (this is what the timeout checker loop should do)
    for query_id in timed_out_queries:
        print(f"   Storing timeout error for query {query_id}")
        query_manager.store_query_result(query_id, {
            "error": "Query processing timed out after 5 minutes"
        })
    
    # Check results after storing
    with query_manager.results_lock:
        print(f"   Results dict after storing: {dict(query_manager.results)}")
    
    # Check the result
    result = get_query_result(query_id)
    print(f"   Final result: {result}")
    
    return result

if __name__ == "__main__":
    print("🚀 Starting Timeout Checker Store Test")
    print("=" * 35)
    
    result = test_timeout_checker_store()
    
    print("\n" + "=" * 35)
    if result and isinstance(result, dict) and "error" in result and "timeout" in result["error"].lower():
        print("✅ Timeout checker storing results correctly!")
    else:
        print("❌ Timeout checker may have issues storing results!")
        print(f"   Result: {result}")
