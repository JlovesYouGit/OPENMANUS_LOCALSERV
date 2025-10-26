#!/usr/bin/env python
"""
Test script for backend endpoints
"""

import sys
import os
import time
import threading
import json
import requests

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result

def simple_processor(message, query_obj):
    """Simple test processor"""
    print(f"Processing: {message}")
    time.sleep(2)  # Simulate processing time
    return f"Response to: {message}"

def test_backend_endpoints():
    """Test the backend endpoints"""
    print("🔧 Testing Backend Endpoints")
    print("=" * 30)
    
    # Set up the processor
    set_query_processor(simple_processor)
    start_query_processing()
    
    # Test enqueueing a query
    print("1. Testing query enqueue...")
    query_id = enqueue_query("Hello, world!", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Test getting query stats
    print("2. Testing query stats...")
    stats = get_query_stats()
    print(f"   Stats: {stats}")
    
    # Wait a bit for processing
    print("3. Waiting for processing...")
    time.sleep(3)
    
    # Test getting query result
    print("4. Testing query result retrieval...")
    result = get_query_result(query_id)
    print(f"   Result: {result}")
    
    # Test stats again
    print("5. Testing final stats...")
    final_stats = get_query_stats()
    print(f"   Final Stats: {final_stats}")
    
    print("\n✅ Backend endpoint test completed!")

def test_api_flow():
    """Test the complete API flow"""
    print("\n🔄 Testing Complete API Flow")
    print("=" * 30)
    
    # This would simulate what the web UI does
    # Since we can't easily test the Flask endpoints without running the server,
    # let's verify the underlying logic works
    
    print("Testing query processing flow...")
    
    # Set up processor
    set_query_processor(simple_processor)
    start_query_processing()
    
    # Enqueue query
    query_id = enqueue_query("Test message", priority=5)
    print(f"  Enqueued query {query_id}")
    
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
        print(f"  Waiting... ({wait_time}s)")
    
    if result:
        print(f"  ✅ Query processed successfully: {result}")
    else:
        print(f"  ❌ Query not processed within {max_wait} seconds")
    
    print("\n✅ API flow test completed!")

if __name__ == "__main__":
    test_backend_endpoints()
    test_api_flow()