#!/usr/bin/env python
"""
Debug script to test query manager functionality
"""

import sys
import os
import time
import asyncio
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result, get_query_stats

# Simple test processor that simulates model response
async def test_processor(message, query_obj):
    """Test processor that simulates model response"""
    print(f"Processing: {message}")
    # Simulate some processing time
    await asyncio.sleep(2)
    return f"Response to: {message}"

def debug_query_manager():
    """Debug the query manager functionality"""
    print("🔍 Debugging Query Manager")
    print("=" * 30)
    
    # Check initial state
    print(f"Initial state - is_running: {query_manager.is_running}")
    print(f"Initial stats: {get_query_stats()}")
    
    # Set up the processor
    print("Setting async processor...")
    set_async_query_processor(test_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Check state after start
    print(f"After start - is_running: {query_manager.is_running}")
    print(f"Worker thread alive: {query_manager.worker_thread.is_alive() if query_manager.worker_thread else 'No thread'}")
    print(f"Timeout checker thread alive: {query_manager.timeout_checker_thread.is_alive() if query_manager.timeout_checker_thread else 'No thread'}")
    
    # Test enqueueing a query
    print("\n1. Testing query enqueue...")
    query_id = enqueue_query("Debug test message", priority=5)
    print(f"   Query ID: {query_id}")
    
    # Check stats after enqueue
    print(f"   Stats after enqueue: {get_query_stats()}")
    
    # Test getting query result
    print("\n2. Testing query result retrieval...")
    max_wait = 20
    wait_time = 0
    result = None
    
    while wait_time < max_wait:
        result = get_query_result(query_id)
        if result is not None:
            break
        print(f"   Waiting for result... ({wait_time}s)")
        time.sleep(1)
        wait_time += 1
    
    # Check final stats
    print(f"   Final stats: {get_query_stats()}")
    
    if result:
        print(f"   ✅ Query completed successfully: {result}")
        return True
    else:
        print(f"   ❌ Query failed or timed out")
        return False

if __name__ == "__main__":
    print("🚀 Starting Query Manager Debug Test")
    print("=" * 40)
    
    success = debug_query_manager()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Query manager debug test passed!")
    else:
        print("❌ Query manager debug test failed!")