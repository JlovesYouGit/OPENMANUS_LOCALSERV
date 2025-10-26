#!/usr/bin/env python
"""
Test script to verify the API is working
"""

import requests
import json

def test_api():
    """Test the chat API"""
    url = "http://localhost:5000/api/chat"
    payload = {
        "message": "Hello, how are you?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()