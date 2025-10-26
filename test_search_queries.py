#!/usr/bin/env python
"""
Test script to verify search query handling fixes
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.manus import Manus
from app.config import config

async def test_search_queries():
    """Test various search-related queries to ensure they don't get stuck in greeting loops"""
    print("🔍 Testing search query handling...")
    
    # Create agent instance
    agent = await Manus.create()
    
    # Test cases that were previously causing issues
    test_cases = [
        "hi",
        "wassup",
        "search for important source info",
        "important historical event america 2022",
        "what is the weather like today?",
        "who is elon musk",
        "thats not what i said"
    ]
    
    print(f"Running {len(test_cases)} test cases...\n")
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{total}: '{test_case}'")
        try:
            response = await agent.complex_task(test_case)
            print(f"  Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            # Check if response is appropriate (not just a greeting for non-greeting queries)
            if test_case.lower() in ["hi", "wassup", "how are you"]:
                # These should return greetings
                if "Hello! How can I help you today? 😊" in response:
                    print("  ✅ Correctly returned greeting")
                    passed += 1
                else:
                    print("  ❌ Should have returned greeting")
            elif "search for" in test_case.lower() or "important historical event" in test_case.lower():
                # These should NOT return greetings
                if "Hello! How can I help you today? 😊" not in response and len(response) > 50:
                    print("  ✅ Correctly processed search query")
                    passed += 1
                else:
                    print("  ❌ Incorrectly returned greeting for search query")
            else:
                # Other queries should have meaningful responses
                if len(response) > 20:
                    print("  ✅ Returned meaningful response")
                    passed += 1
                else:
                    print("  ❌ Response too short")
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All search query tests passed!")
        return True
    else:
        print("⚠️  Some search query tests failed.")
        return False

def main():
    """Run search query tests"""
    print("Running search query handling tests...\n")
    
    try:
        success = asyncio.run(test_search_queries())
        if success:
            print("\n✅ Search query handling is working correctly!")
        else:
            print("\n❌ Search query handling needs attention!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()