#!/usr/bin/env python
"""
Test script to check if we can retrieve current stock price information
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.tool.web_search import WebSearch

async def test_current_stock_price():
    """Test if we can retrieve current stock price information"""
    print("🔍 Testing current stock price retrieval...")
    
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
            if result.description:
                print(f"Description: {result.description[:200]}...")
            if result.raw_content:
                # Look for stock price patterns in the content
                import re
                # Look for common stock price patterns
                price_patterns = [
                    r'\$([0-9]+\.?[0-9]*)',  # $175.50
                    r'([0-9]+\.?[0-9]*) USD',  # 175.50 USD
                    r'price[:\s]*\$?([0-9]+\.?[0-9]*)',  # price: $175.50 or price: 175.50
                ]
                
                content = result.raw_content.lower()
                if "aapl" in content or "apple" in content or "stock" in content:
                    print(f"Apple/stock related content found!")
                    for pattern in price_patterns:
                        matches = re.findall(pattern, content[:2000])  # Check first 2000 chars
                        if matches:
                            print(f"  Potential prices found: {matches}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_finance_specific_search():
    """Test a more specific finance search query"""
    print("\n🔍 Testing finance-specific search...")
    
    web_search = WebSearch()
    
    # More specific query for financial data
    query = "AAPL stock price today"
    
    try:
        print(f"Executing search for: '{query}'")
        search_response = await web_search.execute(
            query=query,
            num_results=3,
            fetch_content=False  # Start with just metadata
        )
        
        if search_response.error:
            print(f"❌ Search failed: {search_response.error}")
            return False
            
        print(f"✅ Found {len(search_response.results)} results")
        
        for i, result in enumerate(search_response.results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result.title}")
            print(f"URL: {result.url}")
            print(f"Description: {result.description}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing current stock price retrieval functionality...")
    
    # Run the async tests
    try:
        result1 = asyncio.run(test_current_stock_price())
        result2 = asyncio.run(test_finance_specific_search())
        
        if result1 and result2:
            print("\n✅ All stock price retrieval tests completed successfully!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()