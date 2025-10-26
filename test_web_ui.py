#!/usr/bin/env python
"""
Test script to verify the web UI functionality for OpenManus
"""

import requests
import json
import time
import threading
import subprocess
import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def start_web_server():
    """Start the web UI server in a separate process"""
    try:
        # Start the web UI server on a different port to avoid conflicts
        process = subprocess.Popen([
            sys.executable, 
            "web_ui.py", 
            "--port", "5002"
        ], cwd="N:\\Openmanus\\OpenManus", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
    except Exception as e:
        print(f"Error starting web server: {e}")
        return None

def test_web_ui_endpoints():
    """Test the web UI endpoints"""
    print("Testing web UI endpoints...")
    
    base_url = "http://localhost:5002"
    
    try:
        # Test the root endpoint
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Root endpoint accessible")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
            
        # Test the init endpoint
        response = requests.get(f"{base_url}/api/init")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Init endpoint working correctly")
            else:
                print(f"❌ Init endpoint failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Init endpoint failed with status {response.status_code}")
            return False
            
        # Test the history endpoint
        response = requests.get(f"{base_url}/api/history")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") is not None:
                print("✅ History endpoint working correctly")
            else:
                print(f"❌ History endpoint failed: {data.get('error')}")
                return False
        else:
            print(f"❌ History endpoint failed with status {response.status_code}")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web server. Make sure it's running.")
        return False
    except Exception as e:
        print(f"❌ Error testing web UI endpoints: {e}")
        return False

def test_chat_api():
    """Test the chat API endpoint"""
    print("\nTesting chat API endpoint...")
    
    base_url = "http://localhost:5002"
    
    try:
        # Test sending a message
        test_message = {"message": "Hello, what is the capital of France?"}
        response = requests.post(
            f"{base_url}/api/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_message)
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Chat API working correctly")
                print(f"   Response: {data.get('response')[:100]}...")
                return True
            else:
                print(f"❌ Chat API failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Chat API failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web server. Make sure it's running.")
        return False
    except Exception as e:
        print(f"❌ Error testing chat API: {e}")
        return False

def main():
    """Run web UI tests"""
    print("Running web UI functionality tests...\n")
    
    # Note: For a complete test, we would start the web server here
    # However, for this demonstration, we'll just test the endpoint logic
    print("Note: This test verifies endpoint logic. For full testing,")
    print("manually start the web UI server and test with a browser.\n")
    
    # Test endpoint functionality
    endpoint_test = test_web_ui_endpoints()
    chat_test = test_chat_api()
    
    if endpoint_test and chat_test:
        print("\n🎉 Web UI endpoint tests passed!")
        print("To fully test the web UI:")
        print("1. Run: python web_ui.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Test sending messages and verify responses")
        print("4. Refresh the page and verify chat history persistence")
        return True
    else:
        print("\n⚠️  Some web UI tests failed.")
        return False

if __name__ == "__main__":
    main()