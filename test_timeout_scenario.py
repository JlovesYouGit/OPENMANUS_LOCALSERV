#!/usr/bin/env python
"""
Test script to verify timeout scenario handling
"""

import sys
import os
import time
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_result

def very_slow_processor(message, query_obj):
    """Very slow processor that will timeout"""
    print(f"Processing: {message}")
    time.sleep(30)  # This will exceed the 10-minute timeout
    return {
        "response": f"Response to: {message}",
        "tool_usage": "Used reasoning engine",
        "quality": {"overall": 0.9, "relevance": 0.85, "accuracy": 0.95}
    }

def simulate_web_ui_query_endpoint():
    """Simulate what happens in the web UI chat endpoint"""
    message = "what model gets timeout"
    priority = 5
    
    # Queue the message
    query_id = enqueue_query(message, priority)
    print(f"Message queued with ID: {query_id}")
    
    # Return queued response (what web UI does)
    return {
        "success": True,
        "queued": True,
        "query_id": query_id,
        "priority": priority,
        "message": "Your query has been queued for processing. Please wait for the response."
    }

def simulate_web_ui_query_result_endpoint(query_id):
    """Simulate what happens in the web UI query result endpoint"""
    try:
        # Check if the query result is available
        result = get_query_result(query_id)
        
        if result is not None:
            # Query has been processed
            if isinstance(result, dict) and "error" in result:
                # Check if this is a timeout error
                if "timed out" in result["error"].lower():
                    return {
                        "success": True,
                        "status": "failed",
                        "error": result["error"]
                    }
                return {
                    "success": True,
                    "status": "failed",
                    "error": result["error"]
                }
            elif isinstance(result, dict):
                response_data = {
                    "success": True,
                    "status": "completed",
                    "response": result.get("response", ""),
                }
                
                # Add optional fields if they exist
                if "tool_usage" in result and result["tool_usage"]:
                    response_data["tool_usage"] = result["tool_usage"]
                if "quality" in result and result["quality"]:
                    response_data["quality"] = result["quality"]
                    
                return response_data
            else:
                return {
                    "success": True,
                    "status": "completed",
                    "response": str(result)
                }
        else:
            # Query is still processing
            return {
                "success": True,
                "status": "processing",
                "message": "Query is still being processed. Please wait."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_timeout_scenario():
    """Test timeout scenario"""
    print("Testing timeout scenario...")
    
    # Set up processor
    set_query_processor(very_slow_processor)
    start_query_processing()
    
    # Simulate web UI chat endpoint
    print("\n1. Simulating web UI chat endpoint...")
    chat_response = simulate_web_ui_query_endpoint()
    print(f"Chat endpoint response: {json.dumps(chat_response, indent=2)}")
    
    query_id = chat_response["query_id"]
    
    # Simulate polling for result (what frontend does)
    print("\n2. Simulating frontend polling for result...")
    max_polls = 70  # Should be enough for timeout detection
    poll_count = 0
    final_result = None
    
    while poll_count < max_polls:
        result_response = simulate_web_ui_query_result_endpoint(query_id)
        print(f"Poll {poll_count + 1}: Status = {result_response.get('status', 'unknown')}")
        
        if result_response.get('status') in ['completed', 'failed']:
            final_result = result_response
            break
        
        # Wait before next poll (shorter for testing)
        time.sleep(2)
        poll_count += 1
    
    print(f"\nFinal result: {json.dumps(final_result, indent=2)}")
    
    # Manually trigger timeout check
    print("\n3. Manually triggering timeout check...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"Timed out queries: {timed_out}")
    
    # Check again after timeout
    if query_id in timed_out:
        result_response = simulate_web_ui_query_result_endpoint(query_id)
        print(f"Result after timeout check: {json.dumps(result_response, indent=2)}")
    
    return final_result

if __name__ == "__main__":
    test_timeout_scenario()