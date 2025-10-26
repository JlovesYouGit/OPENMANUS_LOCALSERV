#!/usr/bin/env python
"""
Test script to check if the web search tool can retrieve current stock price information
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.tool.web_search import WebSearch

async def test_stock_price_retrieval():
    """Test if we can retrieve current stock price information"""
    print("🔍 Testing stock price retrieval using web search...")
    
    # Create web search tool
    web_search = WebSearch()
    
    # Test query for Apple stock price
    query = "Apple stock price current"
    
    try:
        # Execute search
        print(f"Executing search for: '{query}'")
        search_response = await web_search.execute(
            query=query,
            num_results=5,
            fetch_content=True
        )
        
        # Check results
        if search_response.error:
            print(f"❌ Search failed with error: {search_response.error}")
            return False
            
        if not search_response.results:
            print("❌ No search results found")
            return False
            
        print(f"✅ Found {len(search_response.results)} search results")
        
        # Display results
        for i, result in enumerate(search_response.results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"Description: {result.description}")
            if result.raw_content:
                # Show first 500 characters of content
                content_preview = result.raw_content[:500].replace('\n', ' ')
                print(f"Content preview: {content_preview}...")
        
        # Try to extract stock price from results
        print("\n--- Attempting to extract stock price ---")
        stock_price_found = False
        for result in search_response.results:
            content = (result.raw_content or result.description or result.title).lower()
            if "aapl" in content or "apple" in content:
                print(f"Found Apple-related content in: {result.title}")
                # Look for price patterns
                import re
                price_patterns = [
                    r'\$([0-9]+\.?[0-9]*)',
                    r'([0-9]+\.?[0-9]*) dollars',
                    r'price[:\s]*([0-9]+\.?[0-9]*)'
                ]
                for pattern in price_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"Potential prices found: {matches}")
                        stock_price_found = True
        
        if not stock_price_found:
            print("⚠️ No clear stock price information found in search results")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_engines():
    """Test individual search engines"""
    print("\n🔍 Testing individual search engines...")
    
    # Test Google search engine
    try:
        from app.tool.search.google_search import GoogleSearchEngine
        google_engine = GoogleSearchEngine()
        print("Testing Google search engine...")
        results = google_engine.perform_search("Apple stock price", num_results=3)
        print(f"Google search returned {len(results)} results")
        for result in results:
            print(f"  - {result.title}: {result.url}")
    except Exception as e:
        print(f"❌ Google search failed: {e}")
    
    # Test DuckDuckGo search engine
    try:
        from app.tool.search.duckduckgo_search import DuckDuckGoSearchEngine
        ddg_engine = DuckDuckGoSearchEngine()
        print("Testing DuckDuckGo search engine...")
        results = ddg_engine.perform_search("Apple stock price", num_results=3)
        print(f"DuckDuckGo search returned {len(results)} results")
        for result in results:
            print(f"  - {result.title}: {result.url}")
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing stock price retrieval functionality...")
    
    # Run the async test
    try:
        result = asyncio.run(test_stock_price_retrieval())
        if result:
            print("\n✅ Stock price retrieval test completed successfully")
        else:
            print("\n❌ Stock price retrieval test failed")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test individual search engines
    test_search_engines()
    
    print("\n🏁 Test complete")