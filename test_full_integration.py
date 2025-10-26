#!/usr/bin/env python
"""
Full Integration Test
This test simulates the complete flow from frontend to backend to verify
that all components work together correctly, especially focusing on
response handling for long or complex responses.
"""

import sys
import os
import time
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.parse

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result
from app.utils.output_filter import filter_model_output

def comprehensive_processor(message, query_obj):
    """Comprehensive test processor that simulates various response types"""
    print(f"🔧 Processing query: {message}")
    
    # Simulate different types of responses based on the message content
    if "long" in message.lower():
        # Simulate a very long response
        response = "This is a comprehensive response to test long message handling. " * 50
        response += "This is the end of the very long response."
    elif "empty" in message.lower():
        # Simulate an empty response
        response = ""
    elif "error" in message.lower():
        # Simulate an error response
        response = "This response contains an error pattern that should be filtered."
    elif "json" in message.lower():
        # Simulate a JSON response
        response = json.dumps({
            "message": "This is a JSON response",
            "data": {"key": "value"},
            "status": "success"
        })
    else:
        # Normal response
        response = f"Thank you for your message: '{message}'. This is a comprehensive response that addresses your query."
    
    # Simulate processing time
    time.sleep(2)
    
    # Apply output filtering
    should_block, filtered_response, metadata = filter_model_output(message, response)
    
    if should_block:
        print(f"  ⚠️  Response blocked (Score: {metadata.get('overlap_score', 0):.2f})")
        return f"Filtered response: {filtered_response}"
    else:
        print(f"  ✅ Response passed quality filter (Score: {metadata.get('overlap_score', 0):.2f})")
        return response

def test_query_lifecycle():
    """Test the complete query lifecycle"""
    print("🔄 Testing Complete Query Lifecycle")
    print("=" * 40)
    
    # Set up the processor
    set_query_processor(comprehensive_processor)
    start_query_processing()
    
    # Test different types of queries
    test_queries = [
        "Hello, this is a normal message",
        "long response test please",
        "empty response test",
        "json response test",
        "error pattern test"
    ]
    
    print(f"Enqueuing {len(test_queries)} test queries...")
    
    query_results = []
    
    # Enqueue all queries
    for i, message in enumerate(test_queries):
        priority = 5
        query_id = enqueue_query(message, priority)
        query_results.append((query_id, message))
        print(f"  📥 Enqueued: '{message}' (ID: {query_id})")
    
    # Wait for processing
    print("\n⏳ Waiting for queries to be processed...")
    time.sleep(15)  # Wait for all queries to be processed
    
    # Check results
    print("\n📋 Checking results:")
    all_passed = True
    
    for query_id, original_message in query_results:
        result = get_query_result(query_id)
        if result:
            result_str = str(result)
            print(f"  ✅ Query processed successfully")
            print(f"    Original: {original_message}")
            print(f"    Response length: {len(result_str)} characters")
            print(f"    Response preview: {result_str[:100]}...")
            if len(result_str) > 200:
                print(f"    (Long response handled correctly)")
        else:
            print(f"  ❌ Query not processed: {original_message}")
            all_passed = False
    
    # Get final stats
    stats = get_query_stats()
    print(f"\n📊 Final System Stats:")
    print(f"  Total queued: {stats.get('stats', {}).get('total_queued', 0)}")
    print(f"  Total processed: {stats.get('stats', {}).get('total_processed', 0)}")
    print(f"  Total failed: {stats.get('stats', {}).get('total_failed', 0)}")
    
    return all_passed

def simulate_frontend_backend_flow():
    """Simulate the exact flow between frontend and backend"""
    print("\n🌐 Simulating Frontend-Backend Flow")
    print("=" * 35)
    
    # This simulates what happens in the web UI
    set_query_processor(comprehensive_processor)
    start_query_processing()
    
    # Simulate sending a message (like the frontend would)
    message = "Test message for frontend-backend simulation"
    print(f"1. Frontend sends message: '{message}'")
    
    # Backend receives and queues the message
    query_id = enqueue_query(message, priority=5)
    print(f"2. Backend queues message with ID: {query_id}")
    
    # Backend immediately responds to frontend that message is queued
    queued_response = {
        "success": True,
        "queued": True,
        "query_id": query_id,
        "priority": 5,
        "message": "Your query has been queued for processing. Please wait for the response."
    }
    print(f"3. Backend sends queued response: {queued_response}")
    
    # Frontend would then poll for results
    print("4. Frontend begins polling for results...")
    
    max_polls = 10
    poll_count = 0
    result = None
    
    while poll_count < max_polls:
        # This simulates the /api/query/{query_id} endpoint
        result = get_query_result(query_id)
        
        if result is not None:
            # Query is complete
            completed_response = {
                "success": True,
                "status": "completed",
                "response": result
            }
            print(f"5. Query completed! Response: {completed_response}")
            break
        else:
            # Still processing
            processing_response = {
                "success": True,
                "status": "processing",
                "message": "Query is still being processed. Please wait."
            }
            print(f"   Poll {poll_count + 1}: Still processing...")
            time.sleep(1)
            poll_count += 1
    
    if result:
        print("✅ Frontend-backend flow completed successfully!")
        return True
    else:
        print("❌ Frontend-backend flow failed - timeout waiting for response")
        return False

def test_edge_cases():
    """Test edge cases that might cause frontend issues"""
    print("\n⚠️  Testing Edge Cases")
    print("=" * 20)
    
    set_query_processor(comprehensive_processor)
    start_query_processing()
    
    edge_case_tests = [
        ("", "Empty message"),
        ("a", "Single character"),
        ("Special chars: !@#$%^&*()", "Special characters"),
        ("Emoji test: 🚀✨🎉", "Emoji handling"),
        ("Very long message: " + "A" * 1000, "Very long input"),
    ]
    
    all_passed = True
    
    for message, description in edge_case_tests:
        print(f"\nTesting: {description}")
        try:
            if message:  # Skip empty messages as they're filtered out
                query_id = enqueue_query(message, priority=5)
                print(f"  Enqueued with ID: {query_id}")
                
                # Wait for processing
                time.sleep(3)
                
                result = get_query_result(query_id)
                if result:
                    result_str = str(result)
                    print(f"  ✅ Processed successfully (length: {len(result_str)})")
                else:
                    print(f"  ❌ Failed to process")
                    all_passed = False
            else:
                print(f"  ⚠️  Skipped (empty message)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting Full Integration Test")
    print("=" * 50)
    
    # Run all tests
    test1_passed = test_query_lifecycle()
    test2_passed = simulate_frontend_backend_flow()
    test3_passed = test_edge_cases()
    
    print("\n" + "=" * 50)
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    if test1_passed:
        print("✅ Query Lifecycle Test: PASSED")
    else:
        print("❌ Query Lifecycle Test: FAILED")
    
    if test2_passed:
        print("✅ Frontend-Backend Flow Test: PASSED")
    else:
        print("❌ Frontend-Backend Flow Test: FAILED")
    
    if test3_passed:
        print("✅ Edge Cases Test: PASSED")
    else:
        print("❌ Edge Cases Test: FAILED")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("The system is working correctly with proper response handling.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("There may be issues with response handling that need to be addressed.")