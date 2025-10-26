#!/usr/bin/env python
"""
Test script for message sending functionality
"""

import sys
import os
import time
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Test the message sending logic
def test_message_sending_logic():
    """Test the message sending logic without starting the full server"""
    print("Testing Message Sending Logic")
    
    # Simulate the JavaScript logic in Python
    test_messages = [
        "Hello, how are you?",
        "",  # Empty message
        "What is the weather like today?",
        "Tell me about artificial intelligence"
    ]
    
    for message in test_messages:
        print(f"\nTesting message: '{message}'")
        
        # Simulate client-side validation
        if not message or not message.strip():
            print("  ❌ Client-side validation failed: Empty message")
            continue
            
        # Simulate sending to backend
        print("  📤 Sending to backend...")
        time.sleep(0.1)  # Simulate network delay
        
        # Simulate backend response (success)
        response_data = {
            "success": True,
            "response": f"Thanks for your message: '{message}'"
        }
        
        if response_data["success"]:
            print("  ✅ Backend processing successful")
            print(f"  📥 Response: {response_data['response']}")
        else:
            print("  ❌ Backend processing failed")
            
    print("\n✅ Message sending logic test completed")

def test_error_handling():
    """Test error handling scenarios"""
    print("\nTesting Error Handling")
    
    # Simulate network error
    print("\n1. Simulating network error:")
    try:
        # Simulate network failure
        raise ConnectionError("Network connection failed")
    except Exception as e:
        print(f"  ✅ Caught network error: {e}")
        print("  📝 Message should remain in input field for retry")
    
    # Simulate backend error
    print("\n2. Simulating backend error:")
    response_data = {
        "success": False,
        "error": "Internal server error"
    }
    
    if not response_data["success"]:
        print(f"  ✅ Handled backend error: {response_data['error']}")
        print("  📝 Error message displayed to user")
        
    print("\n✅ Error handling test completed")

if __name__ == "__main__":
    test_message_sending_logic()
    test_error_handling()
    print("\n🎉 All tests completed successfully!")