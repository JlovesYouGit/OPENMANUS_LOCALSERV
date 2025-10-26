#!/usr/bin/env python
"""
Test script to verify search query routing without actually performing web searches
"""

import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.manus import Manus

async def test_search_routing():
    """Test that search queries are properly routed and don't get stuck in greeting loops"""
    print("🔍 Testing search query routing...")
    
    # Create agent instance
    agent = await Manus.create()
    
    # Mock the web search method to avoid actual network calls
    async def mock_get_current_information(task):
        return f"Mock search results for: {task}"
    
    # Test cases that were previously causing issues
    test_cases = [
        ("hi", "greeting"),
        ("wassup", "greeting"),
        ("search for important source info", "search"),
        ("important historical event america 2022", "search"),
        ("who is elon musk", "biography"),
        ("thats not what i said", "correction")
    ]
    
    print(f"Running {len(test_cases)} test cases...\n")
    
    passed = 0
    total = len(test_cases)
    
    for i, (test_case, expected_type) in enumerate(test_cases, 1):
        print(f"Test {i}/{total}: '{test_case}' (expected: {expected_type})")
        try:
            # Mock the web search method
            with patch.object(agent, '_get_current_information', side_effect=mock_get_current_information):
                response = await agent.complex_task(test_case)
            
            print(f"  Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            # Check if response is appropriate based on expected type
            if expected_type == "greeting":
                # These should return greetings
                if "Hello! How can I help you today? 😊" in response:
                    print("  ✅ Correctly returned greeting")
                    passed += 1
                else:
                    print("  ❌ Should have returned greeting")
            elif expected_type == "search":
                # These should NOT return greetings and should contain search-related content
                if "Hello! How can I help you today? 😊" not in response and "Mock search results" in response:
                    print("  ✅ Correctly processed search query")
                    passed += 1
                else:
                    print("  ❌ Incorrectly returned greeting for search query")
            elif expected_type == "biography":
                # Should not return greeting
                if "Hello! How can I help you today? 😊" not in response:
                    print("  ✅ Correctly processed biographical query")
                    passed += 1
                else:
                    print("  ❌ Incorrectly returned greeting for biographical query")
            elif expected_type == "correction":
                # Should return correction response
                if "I apologize for the confusion" in response:
                    print("  ✅ Correctly processed correction")
                    passed += 1
                else:
                    print("  ❌ Should have returned correction response")
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All search routing tests passed!")
        return True
    else:
        print("⚠️  Some search routing tests failed.")
        return False

def main():
    """Run search routing tests"""
    print("Running search query routing tests...\n")
    
    try:
        success = asyncio.run(test_search_routing())
        if success:
            print("\n✅ Search query routing is working correctly!")
            return 0
        else:
            print("\n❌ Search query routing needs attention!")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())