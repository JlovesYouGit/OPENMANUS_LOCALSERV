#!/usr/bin/env python
"""
Long test of timeout checker loop
"""

import sys
import os
import time
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager

def test_timeout_checker_long():
    """Test timeout checker loop with longer wait"""
    print("🔍 Long Timeout Checker Test")
    print("=" * 30)
    
    # Start the query manager processing
    print("Starting query processing...")
    query_manager.start_processing()
    
    # Check if threads are running
    print(f"Worker thread alive: {query_manager.worker_thread.is_alive() if query_manager.worker_thread else 'No thread'}")
    print(f"Timeout checker thread alive: {query_manager.timeout_checker_thread.is_alive() if query_manager.timeout_checker_thread else 'No thread'}")
    
    # Add a fake timeout entry for testing
    expired_time = time.time() - 10  # Expired 10 seconds ago
    with query_manager.queue.lock:
        query_manager.queue.processing_timeouts['test_query'] = expired_time
        query_manager.queue.processing.add('test_query')
        print(f"Added fake timeout entry with expired time: {expired_time}")
        print(f"Current time: {time.time()}")
        print(f"Processing timeouts: {dict(query_manager.queue.processing_timeouts)}")
    
    # Wait longer to see if the timeout checker detects it
    print("Waiting 10 seconds for timeout checker...")
    time.sleep(10)
    
    # Check results
    with query_manager.results_lock:
        print(f"Results dict: {dict(query_manager.results)}")
    
    # Clean up
    with query_manager.queue.lock:
        if 'test_query' in query_manager.queue.processing:
            query_manager.queue.processing.remove('test_query')
        if 'test_query' in query_manager.queue.processing_timeouts:
            del query_manager.queue.processing_timeouts['test_query']

if __name__ == "__main__":
    print("🚀 Starting Long Timeout Checker Test")
    print("=" * 35)
    
    test_timeout_checker_long()
    
    print("\n" + "=" * 35)
    print("Test completed!")