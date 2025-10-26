#!/usr/bin/env python
"""
Test script to verify the response handling fixes
"""

import sys
import os
import time
import threading

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_stats, get_query_result

def simple_test_processor(message, query_obj):
    """Simple test processor that doesn't rely on models"""
    print(f"🔧 Processing: {message}")
    
    # Simulate processing time
    time.sleep(1)
    
    # Return a simple response
    if "error" in message.lower():
        return "This is an error response that should be handled properly by the frontend."
    elif "long" in message.lower():
        return "This is a very long response to test how the frontend handles long messages. " * 20 + "End of long response."
    else:
        return f"Response to your message: '{message}'"

def test_response_handling():
    """Test response handling fixes"""
    print("🧪 Testing Response Handling Fixes")
    print("=" * 40)
    
    # Set up the processor
    set_query_processor(simple_test_processor)
    start_query_processing()
    
    # Test different response types
    test_cases = [
        "Normal message",
        "long response test",
        "error response test"
    ]
    
    query_results = []
    
    # Enqueue all test cases
    for message in test_cases:
        query_id = enqueue_query(message, priority=5)
        query_results.append((query_id, message))
        print(f"📥 Enqueued: '{message}' (ID: {query_id})")
    
    # Wait for processing
    print("\n⏳ Waiting for processing...")
    time.sleep(5)
    
    # Check results
    print("\n📋 Results:")
    all_successful = True
    
    for query_id, original_message in query_results:
        result = get_query_result(query_id)
        if result:
            result_str = str(result)
            print(f"✅ Success: '{original_message}'")
            print(f"   Length: {len(result_str)} chars")
            print(f"   Preview: {result_str[:50]}...")
        else:
            print(f"❌ Failed: '{original_message}'")
            all_successful = False
    
    # Final stats
    stats = get_query_stats()
    print(f"\n📊 Stats:")
    print(f"   Total queued: {stats.get('stats', {}).get('total_queued', 0)}")
    print(f"   Total processed: {stats.get('stats', {}).get('total_processed', 0)}")
    
    return all_successful

def simulate_frontend_flow():
    """Simulate the complete frontend-backend flow"""
    print("\n🌐 Simulating Frontend-Backend Flow")
    print("=" * 35)
    
    set_query_processor(simple_test_processor)
    start_query_processing()
    
    # Simulate frontend sending message
    message = "Test message for frontend simulation"
    print(f"1. Frontend sends: '{message}'")
    
    # Backend queues message
    query_id = enqueue_query(message, priority=5)
    print(f"2. Backend queues with ID: {query_id}")
    
    # Backend responds to frontend immediately
    queued_response = {
        "success": True,
        "queued": True,
        "query_id": query_id,
        "priority": 5
    }
    print(f"3. Backend response: {queued_response}")
    
    # Frontend polls for result
    print("4. Frontend polling for result...")
    
    max_polls = 5
    poll_count = 0
    result = None
    
    while poll_count < max_polls:
        result = get_query_result(query_id)
        if result is not None:
            # Query completed
            completed_response = {
                "success": True,
                "status": "completed",
                "response": result
            }
            print(f"5. Query completed! Response length: {len(str(result))} chars")
            break
        else:
            print(f"   Poll {poll_count + 1}: Still processing...")
            time.sleep(1)
            poll_count += 1
    
    if result:
        print("✅ Frontend-backend flow successful!")
        return True
    else:
        print("❌ Frontend-backend flow failed!")
        return False

if __name__ == "__main__":
    print("🚀 Starting Response Handling Test")
    print("=" * 50)
    
    test1 = test_response_handling()
    test2 = simulate_frontend_flow()
    
    print("\n" + "=" * 50)
    print("🏁 TEST RESULTS")
    print("=" * 50)
    
    if test1:
        print("✅ Response Handling Test: PASSED")
    else:
        print("❌ Response Handling Test: FAILED")
    
    if test2:
        print("✅ Frontend-Backend Flow Test: PASSED")
    else:
        print("❌ Frontend-Backend Flow Test: FAILED")
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
        print("The response handling fixes are working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("There may still be issues with response handling.")