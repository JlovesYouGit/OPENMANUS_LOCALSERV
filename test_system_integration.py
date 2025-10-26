#!/usr/bin/env python
"""
Integration test for the entire OpenManus system
"""

import sys
import os
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result
from app.utils.output_filter import filter_model_output
from app.utils.query_analyzer import analyze_user_query

def simple_test_processor(message, query_obj):
    """Simple test processor function for queries"""
    print(f"Processing query: {message}")
    
    # Simulate some processing time
    time.sleep(1)
    
    # Generate appropriate responses based on query type
    analysis = analyze_user_query(message)
    
    if analysis.query_type.value == "greeting":
        result = "Hello! How can I help you today? 😊"
    elif analysis.query_type.value == "current_info":
        result = f"I'd be happy to help you with information about {message}. Let me search for the most current information for you."
    elif analysis.query_type.value == "financial":
        result = f"The current information about {message} is quite interesting. Stock prices fluctuate based on market conditions."
    else:
        result = f"Thanks for your query: '{message}'. I've processed your request and here's a comprehensive response that addresses your question."
    
    print(f"Completed processing: {message}")
    return result

def test_system_integration():
    """Test the full system integration"""
    print("Testing Full System Integration")
    
    # Set up the processor
    set_query_processor(simple_test_processor)
    
    # Start processing
    start_query_processing()
    
    # Test cases
    test_messages = [
        "Hello, how are you?",  # Greeting
        "What is the stock price of Apple?",  # Financial
        "Tell me about artificial intelligence",  # General info
        "What's the weather like today?",  # Current info
        "How do I install Python?"  # Technical
    ]
    
    print(f"Enqueuing {len(test_messages)} test queries...")
    
    # Enqueue all queries
    query_ids = []
    for i, message in enumerate(test_messages):
        priority = 8 if i < 2 else 5  # Higher priority for first two
        query_id = enqueue_query(message, priority)
        query_ids.append(query_id)
        print(f"  Enqueued: '{message}' (ID: {query_id})")
    
    # Wait for processing
    print("\nWaiting for queries to be processed...")
    time.sleep(10)  # Wait for all queries to be processed
    
    # Check results
    print("\nChecking results:")
    all_passed = True
    
    for i, (query_id, message) in enumerate(zip(query_ids, test_messages)):
        result = get_query_result(query_id)
        if result:
            print(f"  Query {i+1}: ✅ Processed")
            print(f"    Message: {message}")
            print(f"    Response: {result}")
            
            # Test quality filter
            should_block, filtered_response, metadata = filter_model_output(message, result)
            if should_block:
                print(f"    Quality Filter: ⚠️  Blocked (Score: {metadata.get('overlap_score', 0):.2f})")
                all_passed = False
            else:
                print(f"    Quality Filter: ✅ Passed (Score: {metadata.get('overlap_score', 0):.2f})")
        else:
            print(f"  Query {i+1}: ❌ No result")
            all_passed = False
        print()
    
    # Get system stats
    stats = get_query_stats()
    print(f"System Stats: {stats}")
    
    if all_passed:
        print("🎉 All integration tests passed!")
    else:
        print("❌ Some tests failed.")

if __name__ == "__main__":
    test_system_integration()