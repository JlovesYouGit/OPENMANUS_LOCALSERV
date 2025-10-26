#!/usr/bin/env python
"""
Test script to verify the cover page implementation
"""

import sys
import os
from pathlib import Path

def test_cover_page_exists():
    """Test that the cover page files exist"""
    cover_page_dir = Path("coverpage/Animatedlandingpagedesign")
    if not cover_page_dir.exists():
        print("❌ Cover page directory not found")
        return False
    
    # Check for required files
    required_files = [
        "src/components/LandingPage.tsx",
        "package.json",
        "vite.config.ts"
    ]
    
    for file_path in required_files:
        full_path = cover_page_dir / file_path
        if not full_path.exists():
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All cover page files exist")
    return True

def test_backend_routes():
    """Test that the backend routes are correctly configured"""
    web_ui_path = Path("web_ui.py")
    if not web_ui_path.exists():
        print("❌ web_ui.py not found")
        return False
    
    try:
        with open(web_ui_path, 'r') as f:
            content = f.read()
        
        # Check for cover page route
        if "send_from_directory(os.path.join('coverpage', 'Animatedlandingpagedesign', 'dist'), 'index.html')" not in content:
            print("❌ Cover page route not found in web_ui.py")
            return False
        
        # Check for app route
        if "send_from_directory(os.path.join('newweb', 'quantum-canvas-design', 'dist'), 'index.html')" not in content:
            print("❌ App route not found in web_ui.py")
            return False
        
        print("✅ Backend routes are correctly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading web_ui.py: {e}")
        return False

def test_landing_page_content():
    """Test that the LandingPage component has the expected content"""
    landing_page_path = Path("coverpage/Animatedlandingpagedesign/src/components/LandingPage.tsx")
    if not landing_page_path.exists():
        print("❌ LandingPage.tsx not found")
        return False
    
    try:
        with open(landing_page_path, 'r') as f:
            content = f.read()
        
        # Check for key elements
        required_elements = [
            "OpenManus",
            "Access Chat",
            "View on GitHub",
            "username",
            "login"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing required elements in LandingPage.tsx: {missing_elements}")
            return False
        
        print("✅ LandingPage component has expected content")
        return True
        
    except Exception as e:
        print(f"❌ Error reading LandingPage.tsx: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing cover page implementation...\n")
    
    tests = [
        test_cover_page_exists,
        test_backend_routes,
        test_landing_page_content
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())