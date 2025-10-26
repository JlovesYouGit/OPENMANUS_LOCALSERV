#!/usr/bin/env python
"""
Simple test to check stock price retrieval
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_duckduckgo_direct():
    """Test DuckDuckGo search directly"""
    print("Testing DuckDuckGo search directly...")
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = ddgs.text("Apple stock price", max_results=3)
        results_list = list(results)
        print(f"Found {len(results_list)} results:")
        for result in results_list:
            print(f"  - {result.get('title', 'No title')}: {result.get('href', 'No URL')}")
        return len(results_list) > 0
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return False

async def test_web_search_simple():
    """Test web search with minimal configuration"""
    print("\nTesting web search tool...")
    try:
        from app.tool.web_search import WebSearch
        web_search = WebSearch()
        
        # Test with a simple query
        search_response = await web_search.execute(
            query="Apple stock price",
            num_results=2,
            fetch_content=False
        )
        
        if search_response.error:
            print(f"Search failed: {search_response.error}")
            return False
            
        print(f"Found {len(search_response.results)} results:")
        for i, result in enumerate(search_response.results, 1):
            print(f"  {i}. {result.title}")
            print(f"     {result.url}")
            
        return len(search_response.results) > 0
        
    except Exception as e:
        print(f"Web search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing stock price retrieval...")
    
    # Test DuckDuckGo directly
    ddg_success = test_duckduckgo_direct()
    
    # Test web search tool
    web_success = asyncio.run(test_web_search_simple())
    
    if ddg_success or web_success:
        print("\n✅ At least one method worked!")
    else:
        print("\n❌ Both methods failed")