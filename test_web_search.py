#!/usr/bin/env python
"""
Test script to verify WebSearch tool functionality in OpenManus
"""

import asyncio
import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.tool.web_search import WebSearch

async def test_web_search():
    """Test the WebSearch tool"""
    print("Testing WebSearch tool...")
    
    # Create a WebSearch tool instance
    web_search = WebSearch()
    
    # Test searching for current stock prices
    print("\nSearching for current stock prices...")
    try:
        search_response = await web_search.execute(
            query="current Apple stock price",
            num_results=3,
            fetch_content=False
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
                print(f"   Description: {result.description}")
                
            return True
    except Exception as e:
        print(f"❌ Search failed with exception: {e}")
        return False

async def test_current_info():
    """Test searching for current information"""
    print("\n\nTesting search for current information...")
    
    web_search = WebSearch()
    
    # Test with a time-sensitive query
    try:
        search_response = await web_search.execute(
            query="what is today's date",
            num_results=2,
            fetch_content=False
        )
        
        if search_response.error:
            print(f"❌ Search failed with error: {search_response.error}")
            return False
        else:
            print("✅ Current info search completed successfully!")
            print(f"Query: {search_response.query}")
            
            # Display the results
            for i, result in enumerate(search_response.results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Description: {result.description}")
                
            return True
    except Exception as e:
        print(f"❌ Current info search failed with exception: {e}")
        return False

async def main():
    """Run all tests"""
    print("Running WebSearch tool verification tests...\n")
    
    tests = [
        test_web_search,
        test_current_info
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
        print("🎉 All tests passed! The WebSearch tool is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())