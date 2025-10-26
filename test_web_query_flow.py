#!/usr/bin/env python
"""
Test script to verify web query flow including timeout handling
"""

import sys
import os
import time
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_query_processor, start_query_processing, get_query_result

def slow_processor(message, query_obj):
    """Slow processor that takes time to simulate real processing"""
    print(f"Processing: {message}")
    time.sleep(5)  # Simulate processing time
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

def test_web_query_flow():
    """Test the complete web query flow"""
    print("Testing web query flow...")
    
    # Set up processor
    set_query_processor(slow_processor)
    start_query_processing()
    
    # Simulate web UI chat endpoint
    print("\n1. Simulating web UI chat endpoint...")
    chat_response = simulate_web_ui_query_endpoint()
    print(f"Chat endpoint response: {json.dumps(chat_response, indent=2)}")
    
    query_id = chat_response["query_id"]
    
    # Simulate polling for result (what frontend does)
    print("\n2. Simulating frontend polling for result...")
    max_polls = 20
    poll_count = 0
    final_result = None
    
    while poll_count < max_polls:
        result_response = simulate_web_ui_query_result_endpoint(query_id)
        print(f"Poll {poll_count + 1}: Status = {result_response.get('status', 'unknown')}")
        
        if result_response.get('status') in ['completed', 'failed']:
            final_result = result_response
            break
        
        # Wait before next poll
        time.sleep(1)
        poll_count += 1
    
    print(f"\nFinal result: {json.dumps(final_result, indent=2)}")
    
    return final_result

if __name__ == "__main__":
    test_web_query_flow()