#!/usr/bin/env python
"""
Test script to verify the new frontend is being served correctly
"""

import requests
import time
import os

def test_frontend_serving():
    """Test that the new React frontend is being served"""
    try:
        # Wait a moment for server to be ready
        time.sleep(2)
        
        # Test the root endpoint
        response = requests.get('http://localhost:5000/')
        
        if response.status_code == 200:
            content = response.text
            
            # Check if it's the new React frontend (look for React-specific content)
            if '<div id="root"></div>' in content:
                print("✅ SUCCESS: New React frontend is being served!")
                return True
            # Check if it's the old frontend (look for old template content)
            elif 'OpenManus' in content and 'AI Assistant' in content:
                print("⚠️  WARNING: Still serving the old frontend")
                return False
            else:
                print("❓ UNKNOWN: Serving some other content")
                print(f"Content preview: {content[:200]}...")
                return False
        else:
            print(f"❌ ERROR: Server returned status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_static_assets():
    """Test that static assets are being served"""
    try:
        # Test a static asset
        response = requests.get('http://localhost:5000/assets/index-Byt0rU3D.js')
        
        if response.status_code == 200:
            print("✅ SUCCESS: Static assets are being served!")
            return True
        else:
            print(f"⚠️  WARNING: Static assets not found (status code {response.status_code})")
            return False
            
    except Exception as e:
        print(f"⚠️  WARNING: Error testing static assets: {e}")
        return False

if __name__ == "__main__":
    print("Testing frontend serving...")
    print("=" * 40)
    
    frontend_test = test_frontend_serving()
    assets_test = test_static_assets()
    
    print("\n" + "=" * 40)
    if frontend_test and assets_test:
        print("🎉 ALL TESTS PASSED: New frontend is properly integrated!")
    elif frontend_test:
        print("✅ Frontend serving works, but check static assets")
    else:
        print("❌ TESTS FAILED: Frontend integration needs more work")