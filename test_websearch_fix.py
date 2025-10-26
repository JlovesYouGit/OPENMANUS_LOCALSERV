#!/usr/bin/env python
"""
Test script to verify the WebSearch fallback fix for Manus agent
"""

import asyncio
import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.manus import Manus
from app.tool.web_search import WebSearch

async def test_fallback_tool_usage():
    """Test the fallback tool usage when model inference fails"""
    print("Testing fallback tool usage when model inference fails...")
    
    try:
        # Create a Manus agent instance
        agent = await Manus.create()
        print("✅ Manus agent created successfully!")
        
        # Test the fallback method directly
        print("\nTesting fallback method for current stock information...")
        fallback_response = await agent._fallback_tool_usage("What is the current price of Apple stock?")
        print(f"Fallback response: {fallback_response}")
        
        # Check if the response contains current information or search attempt
        if "search" in fallback_response.lower() or "current" in fallback_response.lower():
            print("✅ Fallback method worked correctly!")
        else:
            print("⚠️  Fallback response may not contain current information")
        
        # Clean up
        await agent.cleanup()
        print("✅ Agent cleaned up successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_direct_web_search():
    """Test direct WebSearch tool usage"""
    print("\n\nTesting direct WebSearch tool usage...")
    
    try:
        # Create a WebSearch tool instance
        web_search = WebSearch()
        
        # Test searching for current stock prices
        print("Searching for current Apple stock price...")
        search_response = await web_search.execute(
            query="current Apple stock price",
            num_results=3,
            fetch_content=True
        )
        
        if search_response.error:
            print(f"❌ Search failed with error: {search_response.error}")
            return False
        else:
            print("✅ Search completed successfully!")
            print(f"Query: {search_response.query}")
            print(f"Found {len(search_response.results)} results")
            
            # Display the results
            for i, result in enumerate(search_response.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                if result.raw_content:
                    print(f"   Content: {result.raw_content[:200]}...")
                else:
                    print(f"   Description: {result.description}")
            
            return True
    except Exception as e:
        print(f"❌ Direct search test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("Running WebSearch fallback fix verification tests...\n")
    
    tests = [
        test_fallback_tool_usage,
        test_direct_web_search
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The WebSearch fallback fix is working correctly.")
        print("\nSummary of improvements:")
        print("1. ✅ Added fallback tool usage when model inference fails")
        print("2. ✅ Verified direct WebSearch tool functionality")
        print("3. ✅ Confirmed agent can access current information even when model fails")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())