#!/usr/bin/env python
"""
Test script to verify query processing flow
"""

import sys
import os
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_result

def simple_processor(message, query_obj):
    """Simple test processor"""
    print(f"Processing: {message}")
    time.sleep(2)  # Simulate processing time
    return f"Response to: {message}"

def test_query_flow():
    """Test the complete query flow"""
    print("Testing query processing flow...")
    
    # Set up processor
    set_query_processor(simple_processor)
    start_query_processing()
    
    # Enqueue query
    query_id = enqueue_query("test message", priority=5)
    print(f"Enqueued query {query_id}")
    
    # Check if it's processed
    max_wait = 10
    wait_time = 0
    result = None
    
    while wait_time < max_wait:
        result = get_query_result(query_id)
        if result is not None:
            break
        time.sleep(1)
        wait_time += 1
        print(f"Waiting... ({wait_time}s)")
    
    if result:
        print(f"✅ Query processed successfully: {result}")
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Result keys: {result.keys()}")
    else:
        print(f"❌ Query not processed within {max_wait} seconds")
    
    return result

if __name__ == "__main__":
    test_query_flow()