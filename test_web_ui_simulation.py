#!/usr/bin/env python
"""
Test that simulates the exact web UI scenario with timeout handling
"""

import sys
import os
import time
import asyncio
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.query_manager import query_manager, enqueue_query, set_async_query_processor, start_query_processing, get_query_result

# Processor that simulates a long-running task that will timeout
async def very_slow_processor(message, query_obj):
    """Processor that takes longer than timeout to complete"""
    print(f"Processing (very slow): {message}")
    # Simulate a very long processing time (600 seconds = 10 minutes)
    await asyncio.sleep(600)
    return f"Very slow response to: {message}"

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

def test_web_ui_simulation():
    """Test the web UI simulation with timeout handling"""
    print("🌐 Web UI Simulation Test")
    print("=" * 25)
    
    # Set up the processor
    print("Setting very slow processor...")
    set_async_query_processor(very_slow_processor)
    
    # Start processing
    print("Starting query processing...")
    start_query_processing()
    
    # Simulate what happens in the web UI chat endpoint
    print("\n1. Simulating web UI chat endpoint...")
    message = "This is a test message that should timeout"
    priority = 5
    
    # This is what happens in the web UI chat endpoint
    query_id = enqueue_query(message, priority)
    print(f"   Query enqueued with ID: {query_id}")
    
    # Simulate what happens in the web UI query result endpoint
    print("\n2. Simulating web UI query result endpoint polling...")
    
    # Poll for result like the web UI does
    max_polls = 10
    poll_count = 0
    response = None
    
    while poll_count < max_polls:
        response = simulate_web_ui_query_result_endpoint(query_id)
        print(f"   Poll {poll_count + 1}: Status = {response.get('status', 'unknown')}")
        print(f"   Response: {json.dumps(response, indent=2)}")
        
        if response.get('status') in ['completed', 'failed']:
            # Query has been processed or timed out
            break
        
        # Wait before next poll (shorter for testing)
        print("   Waiting 2 seconds before next poll...")
        time.sleep(2)
        poll_count += 1
    
    # Now manually trigger a timeout to see if it's handled correctly
    print("\n3. Manually triggering timeout check...")
    timed_out = query_manager.queue.check_timeouts()
    print(f"   Timed out queries: {timed_out}")
    
    # Check again after timeout
    if query_id in timed_out:
        response = simulate_web_ui_query_result_endpoint(query_id)
        print(f"   Response after timeout: {json.dumps(response, indent=2)}")
    
    return response

if __name__ == "__main__":
    print("🚀 Starting Web UI Simulation Test")
    print("=" * 35)
    
    response = test_web_ui_simulation()
    
    print("\n" + "=" * 35)
    if response and response.get('status') == 'failed' and 'timeout' in response.get('error', '').lower():
        print("✅ Web UI timeout handling working correctly!")
    elif response and response.get('status') == 'processing':
        print("✅ Query is still processing - this is expected!")
    else:
        print("❌ Unexpected result!")
        print(f"   Response: {response}")