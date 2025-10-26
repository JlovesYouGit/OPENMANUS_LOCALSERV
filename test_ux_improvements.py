#!/usr/bin/env python
"""
Test script to verify the UX improvements have been implemented correctly
"""

import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_header_button_text():
    """Test that the Header component shows correct button text based on auth state"""
    
    # Path to the Header component file
    header_file_path = Path("newweb/quantum-canvas-design/src/components/Header.tsx")
    full_path = Path(__file__).parent / header_file_path
    
    if not full_path.exists():
        print(f"❌ Header file not found at {full_path}")
        return False
    
    # Read the file content
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key elements
    required_elements = [
        "useAuth",  # Import and usage of useAuth
        "isAuthenticated",  # Check for auth state
        "{isAuthenticated ? \"New Chat\" : \"Get Started\"}",  # Correct button text logic
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print("❌ Missing required elements in Header component:")
        for element in missing_elements:
            print(f"  - {element}")
        return False
    
    print("✅ Header component correctly implements dynamic button text")
    return True

def test_dashboard_view():
    """Test that the Index page implements a dashboard view"""
    
    # Path to the Index component file
    index_file_path = Path("newweb/quantum-canvas-design/src/pages/Index.tsx")
    full_path = Path(__file__).parent / index_file_path
    
    if not full_path.exists():
        print(f"❌ Index file not found at {full_path}")
        return False
    
    # Read the file content
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key elements of dashboard implementation
    required_elements = [
        "!currentChatId",  # Conditional rendering for dashboard
        "Welcome to OpenManus",  # Dashboard title
        "Start New Chat",  # Dashboard CTA
        "grid-cols-3",  # Feature grid
        "handleNewChat",  # New chat handler
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print("❌ Missing required elements in Index component for dashboard:")
        for element in missing_elements:
            print(f"  - {element}")
        return False
    
    print("✅ Index component correctly implements dashboard view")
    return True

def test_chat_deletion_redirect():
    """Test that chat deletion redirects to dashboard"""
    
    # Path to the Sidebar component file
    sidebar_file_path = Path("newweb/quantum-canvas-design/src/components/Sidebar.tsx")
    full_path = Path(__file__).parent / sidebar_file_path
    
    if not full_path.exists():
        print(f"❌ Sidebar file not found at {full_path}")
        return False
    
    # Read the file content
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key elements of chat deletion redirect
    required_elements = [
        "chatToDelete === currentChatId",  # Check if deleting current chat
        "onChatSelect(\"\")",  # Redirect to dashboard
        "navigate(\"/\")",  # Navigate to root
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print("❌ Missing required elements in Sidebar component for chat deletion redirect:")
        for element in missing_elements:
            print(f"  - {element}")
        return False
    
    print("✅ Sidebar component correctly implements chat deletion redirect")
    return True

def main():
    """Run all UX improvement tests"""
    print("Testing UX improvements...\n")
    
    tests = [
        test_header_button_text,
        test_dashboard_view,
        test_chat_deletion_redirect
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All UX improvement tests passed!")
        return 0
    else:
        print("\n❌ Some UX improvement tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())