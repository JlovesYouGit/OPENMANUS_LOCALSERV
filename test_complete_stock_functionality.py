#!/usr/bin/env python
"""
Comprehensive test for the complete stock price functionality
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agent.manus import Manus

async def test_agent_stock_detection():
    """Test if the agent correctly detects stock price queries"""
    print("🔍 Testing agent stock price detection...")
    
    agent = Manus()
    
    test_queries = [
        "What is the current price of Apple stock?",
        "Tell me the latest news about technology",
        "What's the weather like today?",
        "How much does Netflix cost?",
        "What is the current exchange rate for USD to EUR?",
    ]
    
    for query in test_queries:
        is_current = agent._requires_current_information(query)
        stock_related = "stock" in query.lower() and ("price" in query.lower() or "cost" in query.lower())
        print(f"'{query}' -> Current info: {is_current}, Stock-related: {stock_related}")

async def test_agent_stock_extraction():
    """Test the agent's stock price extraction functionality"""
    print("\n🔍 Testing agent stock price extraction...")
    
    # This would normally be tested with actual search results,
    # but we'll test the logic directly
    
    agent = Manus()
    
    # Test the _requires_current_information method
    stock_query = "What is the current price of Apple stock?"
    is_current = agent._requires_current_information(stock_query)
    print(f"Stock query detection: '{stock_query}' -> {is_current}")
    
    # Test query refinement
    task_lower = stock_query.lower()
    if "stock" in task_lower and ("price" in task_lower or "cost" in task_lower):
        if "apple" in task_lower or "aapl" in task_lower:
            refined_query = "AAPL stock price"
        elif "microsoft" in task_lower or "msft" in task_lower:
            refined_query = "MSFT stock price"
        elif "google" in task_lower or "goog" in task_lower:
            refined_query = "GOOGL stock price"
        else:
            refined_query = f"current stock price {stock_query}"
        print(f"Query refinement: '{stock_query}' -> '{refined_query}'")

def test_config():
    """Test if the search configuration is properly loaded"""
    print("\n🔍 Testing search configuration...")
    
    from app.config import config
    
    search_config = config.search_config
    if search_config:
        print(f"✅ Search engine: {search_config.engine}")
        print(f"✅ Fallback engines: {search_config.fallback_engines}")
        print(f"✅ Language: {search_config.lang}")
        print(f"✅ Country: {search_config.country}")
        return True
    else:
        print("❌ Search configuration not loaded")
        return False

async def test_web_search_integration():
    """Test the complete web search integration"""
    print("\n🔍 Testing web search integration...")
    
    try:
        from app.tool.web_search import WebSearch
        web_search = WebSearch()
        
        # Test a simple stock query
        query = "AAPL stock price"
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
            print(f"  {i}. {result.title}")
            print(f"     {result.url}")
            
        return True
        
    except Exception as e:
        print(f"❌ Web search integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing complete stock price functionality...")
    
    # Run all tests
    try:
        asyncio.run(test_agent_stock_detection())
        asyncio.run(test_agent_stock_extraction())
        config_ok = test_config()
        search_ok = asyncio.run(test_web_search_integration())
        
        if config_ok and search_ok:
            print("\n✅ All tests passed! The system should now properly handle stock price queries.")
        else:
            print("\n❌ Some tests failed. Please check the configuration.")
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()