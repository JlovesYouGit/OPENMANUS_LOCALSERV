#!/usr/bin/env python
"""
Performance test for the Query Management System
"""

import sys
import os
import time
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result
from app.utils.performance_monitor import start_request_timer, end_request_timer, get_performance_report

def performance_test_processor(message, query_obj):
    """Performance test processor function for queries"""
    start_time = start_request_timer()
    
    # Simulate processing with varying complexity
    message_length = len(message)
    processing_time = 0.1 + (message_length / 1000)  # Base time + time based on message length
    time.sleep(processing_time)
    
    result = f"Processed: {message}"
    end_request_timer(start_time, len(result), "test_model", message_length, True)
    return result

def run_performance_test():
    """Run a performance test"""
    print("Running Performance Test")
    
    # Set up the processor
    set_query_processor(performance_test_processor)
    
    # Start processing
    start_query_processing()
    
    # Enqueue multiple test queries to measure performance
    query_ids = []
    test_messages = [
        "Short message",
        "This is a medium length message that contains more content than the short one",
        "This is a significantly longer message that is designed to test the performance of the system with larger inputs and more complex processing requirements that would take more time to process",
        "Another short one",
        "Medium length message with some additional content to increase processing time",
        "Very long message that contains a lot of text and would require more processing time than shorter messages because it has more characters and words to process which increases the computational requirements for handling this particular query in the system",
        "Hi",
        "What is the weather today?",
        "Tell me about artificial intelligence and machine learning technologies",
        "How do I optimize my computer for better performance with large language models?"
    ] * 3  # Repeat to get more data points
    
    print(f"Enqueuing {len(test_messages)} test queries...")
    
    # Record start time
    test_start_time = time.time()
    
    # Enqueue all queries
    for i, message in enumerate(test_messages):
        priority = 8 if len(message) < 50 else 3  # Higher priority for short messages
        query_id = enqueue_query(message, priority)
        query_ids.append(query_id)
    
    # Wait for all queries to be processed
    print("Waiting for all queries to be processed...")
    processed_count = 0
    max_wait_time = 60  # Maximum wait time in seconds
    start_wait_time = time.time()
    
    while processed_count < len(query_ids) and (time.time() - start_wait_time) < max_wait_time:
        processed_count = sum(1 for qid in query_ids if get_query_result(qid) is not None)
        print(f"Processed {processed_count}/{len(query_ids)} queries...")
        time.sleep(1)
    
    # Calculate test duration
    test_duration = time.time() - test_start_time
    
    # Get system stats
    stats = get_query_stats()
    performance_report = get_performance_report()
    
    print(f"\nPerformance Test Results:")
    print(f"Total test duration: {test_duration:.2f} seconds")
    print(f"Queries processed: {processed_count}/{len(query_ids)}")
    print(f"Average processing time per query: {test_duration/processed_count:.3f} seconds")
    print(f"Queries per second: {processed_count/test_duration:.2f}")
    
    print(f"\nQuery Manager Stats: {stats}")
    print(f"\nPerformance Monitor Report: {performance_report}")

if __name__ == "__main__":
    run_performance_test()