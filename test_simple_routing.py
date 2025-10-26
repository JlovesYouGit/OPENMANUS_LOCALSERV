#!/usr/bin/env python
"""
Simple test to verify search query routing logic
"""

import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_search_indicators():
    """Test the search indicator detection logic"""
    # This is the logic we added to the Manus agent
    search_indicators = [
        "search for", "search about", "find information", "look up", 
        "important source info", "important historical event"
    ]
    
    # Test cases
    test_cases = [
        ("hi", False),
        ("wassup", False),
        ("search for important source info", True),
        ("important historical event america 2022", True),
        ("who is elon musk", False),
        ("find information about python", True),
        ("look up the weather", True)
    ]
    
    print("Testing search indicator detection logic...")
    print(f"Search indicators: {search_indicators}")
    print()
    
    passed = 0
    total = len(test_cases)
    
    for i, (test_input, should_match) in enumerate(test_cases, 1):
        task_lower = test_input.lower()
        is_search = any(indicator in task_lower for indicator in search_indicators)
        
        print(f"Test {i}/{total}: '{test_input}'")
        print(f"  Expected: {should_match}, Got: {is_search}")
        
        if is_search == should_match:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All routing logic tests passed!")
        return True
    else:
        print("⚠️  Some routing logic tests failed.")
        return False

if __name__ == "__main__":
    success = test_search_indicators()
    sys.exit(0 if success else 1)