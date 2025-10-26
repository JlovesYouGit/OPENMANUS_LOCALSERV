#!/usr/bin/env python
"""
Test script to verify the improved reasoning flow
"""

import requests
import json
import time

def test_reasoning_flow():
    """Test the improved reasoning flow"""
    url = "http://localhost:5000/api/chat"
    
    # Test cases
    test_cases = [
        "What is the capital of France?",
        "What is the current stock price of Apple?",
        "Calculate 15*24",
        "Explain quantum computing in simple terms",
        "Hello, how are you?"
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
            response = requests.post(url, data=json.dumps(payload), headers=headers)
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
        time.sleep(2)

if __name__ == "__main__":
    test_reasoning_flow()