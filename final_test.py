#!/usr/bin/env python
"""
Final test script to verify the improved natural responses
"""

import requests
import json
import time

def test_natural_responses():
    """Test for more natural model responses"""
    url = "http://localhost:5000/api/chat"
    
    # Test cases that should produce natural responses
    test_cases = [
        "What is the capital of France?",
        "Tell me a fun fact about space",
        "How are you doing today?",
        "What's the weather like?",
        "Can you explain quantum computing?"
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case} ---")
        
        payload = {
            "message": test_case
        }
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"Response: {result.get('response')}")
                    if result.get("tool_usage"):
                        print(f"Tool Usage: {result.get('tool_usage')}")
                else:
                    print(f"Error: {result.get('error')}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        # Add a small delay between requests
        time.sleep(3)

if __name__ == "__main__":
    test_natural_responses()