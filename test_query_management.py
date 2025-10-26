#!/usr/bin/env python
"""
Test script for the Query Management System
"""

import sys
import os
import time
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result

def test_query_processor(message, query_obj):
    """Test processor function for queries"""
    print(f"Processing query: {message}")
    # Simulate some processing time
    time.sleep(2)
    result = f"Processed: {message}"
    print(f"Completed processing: {message}")
    return result

def test_query_management():
    """Test the query management system"""
    print("Testing Query Management System")
    
    # Set up the processor
    set_query_processor(test_query_processor)
    
    # Start processing
    start_query_processing()
    
    # Enqueue some test queries
    query_ids = []
    test_messages = [
        "Hello, how are you?",
        "What is the weather like today?",
        "Tell me a joke",
        "What is the stock price of Apple?",
        "How do I cook pasta?"
    ]
    
    # Enqueue queries with different priorities
    for i, message in enumerate(test_messages):
        priority = 8 if i < 2 else 5  # Higher priority for first two
        query_id = enqueue_query(message, priority)
        query_ids.append(query_id)
        print(f"Enqueued query '{message}' with ID: {query_id}, priority: {priority}")
    
    # Wait for processing
    print("Waiting for queries to be processed...")
    time.sleep(15)  # Wait for all queries to be processed
    
    # Check results
    print("\nChecking results:")
    for query_id in query_ids:
        result = get_query_result(query_id)
        if result:
            print(f"Query {query_id}: {result}")
        else:
            print(f"Query {query_id}: No result yet")
    
    # Get system stats
    stats = get_query_stats()
    print(f"\nSystem Stats: {stats}")

if __name__ == "__main__":
    test_query_management()