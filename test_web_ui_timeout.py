#!/usr/bin/env python
"""
Test that simulates the web UI timeout handling by manually setting a timeout
"""

import sys
import os
import time
import asyncio
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that completes quickly
async def fast_processor(message, query_obj):
    """Processor that completes quickly"""
    print(f"Processing: {message}")
    await asyncio.sleep(1)
    return f"Quick response to: {message}"

def simulate_web_ui_query_result_endpoint(query_id):
    """Simulate the web UI query result endpoint"""
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

def test_web_ui_timeout():
    """Test the web UI timeout handling"""
    print("🌐 Web UI Timeout Handling Test")
    print("=" * 30)
    
    # Set up the processor
    print("Setting fast processor...")
    set_async_query_processor(fast_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Simulate what happens in the web UI chat endpoint
    print("\n1. Simulating web UI chat endpoint...")
    message = "This is a test message"
    priority = 5
    
    # This is what happens in the web UI chat endpoint
    query_id = enqueue_query(message, priority)
    print(f"   Query enqueued with ID: {query_id}")
    
    # Wait for it to start processing
    print("   Waiting for query to start processing...")
    time.sleep(1)
    
    # Manually add a timeout entry for testing
    print("   Manually adding timeout entry...")
    with query_manager.queue.lock:
        # Set timeout to be in the past (already expired)
        query_manager.queue.processing_timeouts[query_id] = time.time() - 10
        print(f"   Set timeout for query {query_id} to {query_manager.queue.processing_timeouts[query_id]}")
        print(f"   Current time: {time.time()}")
    
    # Manually trigger timeout check
    print("   Manually triggering timeout check...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check if the timeout error was stored
    with query_manager.results_lock:
        print(f"   Results dict: {dict(query_manager.results)}")
    
    # Simulate what happens in the web UI query result endpoint
    print("\n2. Simulating web UI query result endpoint...")
    response = simulate_web_ui_query_result_endpoint(query_id)
    print(f"   Response: {json.dumps(response, indent=2)}")
    
    return response

if __name__ == "__main__":
    print("🚀 Starting Web UI Timeout Handling Test")
    print("=" * 40)
    
    response = test_web_ui_timeout()
    
    print("\n" + "=" * 40)
    if response and response.get('status') == 'failed' and 'timeout' in response.get('error', '').lower():
        print("✅ Web UI timeout handling working correctly!")
    else:
        print("❌ Web UI timeout handling may have issues!")
        print(f"   Response: {response}")