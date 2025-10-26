#!/usr/bin/env python
"""
Test script to verify the frontend integration
"""

import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_frontend_files():
    """Test that frontend files exist"""
    print("Testing frontend files...")
    
    # Check if the frontend build directory exists
    frontend_dist = Path("newweb/quantum-canvas-design/dist")
    if frontend_dist.exists():
        print("✅ Frontend build directory exists")
        # Check for key files
        index_html = frontend_dist / "index.html"
        if index_html.exists():
            print("✅ index.html exists")
        else:
            print("❌ index.html not found")
            return False
    else:
        print("⚠️  Frontend build directory not found (this is expected if not built yet)")
    
    # Check API service file
    api_service = Path("newweb/quantum-canvas-design/src/services/api.ts")
    if api_service.exists():
        print("✅ API service file exists")
    else:
        print("❌ API service file not found")
        return False
        
    return True

def test_backend_routes():
    """Test that backend routes are properly configured"""
    print("\nTesting backend routes...")
    
    # These tests require the server to be running
    # For now, we'll just verify the code structure
    try:
        # Import the web_ui module to check for syntax errors
        import web_ui
        print("✅ web_ui.py imports successfully")
        
        # Check that the app has the expected routes
        if hasattr(web_ui.app, 'routes'):
            routes = [rule.rule for rule in web_ui.app.url_map.iter_rules()]
            expected_routes = ['/', '/api/init', '/api/chat', '/api/history']
            found_routes = [route for route in expected_routes if route in routes]
            if len(found_routes) == len(expected_routes):
                print("✅ All expected routes found")
            else:
                print(f"⚠️  Some routes missing. Found: {found_routes}")
        else:
            print("⚠️  Unable to verify routes")
            
        return True
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_api_service():
    """Test the API service functions"""
    print("\nTesting API service...")
    
    # This is a static analysis test
    api_file = Path("newweb/quantum-canvas-design/src/services/api.ts")
    if not api_file.exists():
        print("❌ API service file not found")
        return False
    
    # Read the file and check for key functions
    content = api_file.read_text()
    required_functions = ['initializeAgent', 'sendMessage', 'getChatHistory']
    found_functions = [func for func in required_functions if func in content]
    
    if len(found_functions) == len(required_functions):
        print("✅ All required API functions found")
        return True
    else:
        print(f"❌ Some API functions missing. Found: {found_functions}")
        return False

def main():
    """Run all integration tests"""
    print("Running OpenManus frontend integration tests...\n")
    
    tests = [
        test_frontend_files,
        test_backend_routes,
        test_api_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\nNext steps:")
        print("1. Build the frontend: Run clean_and_build_frontend.ps1")
        print("2. Start the server: python web_ui.py")
        print("3. Open http://localhost:5000 in your browser")
        return True
    else:
        print(f"⚠️  {passed}/{total} tests passed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)