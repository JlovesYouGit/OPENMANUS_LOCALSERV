#!/usr/bin/env python
"""
Test script to verify stock price extraction functionality
"""

import re

def test_stock_price_extraction():
    """Test stock price extraction from sample content"""
    print("🔍 Testing stock price extraction...")
    
    # Sample content that might be found in search results
    sample_contents = [
        "Apple Inc. (AAPL) stock price is $175.42 today",
        "Current price: $175.42 USD",
        "AAPL stock is trading at $175.42 per share",
        "The stock price for Apple is $175.42 as of now",
        "Apple (AAPL) $175.42 USD",
        "Price: $175.42",
    ]
    
    # Price patterns to test
    price_patterns = [
        r'\$([0-9]+\.?[0-9]*)',  # $175.50
        r'([0-9]+\.?[0-9]*)\s*usd',  # 175.50 USD
        r'price[:\s]*\$?([0-9]+\.?[0-9]*)',  # price: $175.50 or price: 175.50
    ]
    
    for i, content in enumerate(sample_contents):
        print(f"\nTest {i+1}: '{content}'")
        content_lower = content.lower()
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                print(f"  Pattern '{pattern}' found: {matches}")
                for match in matches:
                    try:
                        price = float(match)
                        if price > 0 and price < 10000:  # Reasonable stock price range
                            print(f"    Valid stock price: ${price:.2f}")
                    except ValueError:
                        print(f"    Invalid price format: {match}")

def test_query_refinement():
    """Test query refinement for stock price searches"""
    print("\n🔍 Testing query refinement...")
    
    test_queries = [
        "What is the current price of Apple stock?",
        "How much does Microsoft stock cost?",
        "What is Google's current stock price?",
        "Tell me the price of Tesla stock",
        "What is the stock price of Amazon?"
    ]
    
    for query in test_queries:
        query_lower = query.lower()
        refined_query = query
        
        if "stock" in query_lower and ("price" in query_lower or "cost" in query_lower):
            if "apple" in query_lower or "aapl" in query_lower:
                refined_query = "AAPL stock price"
            elif "microsoft" in query_lower or "msft" in query_lower:
                refined_query = "MSFT stock price"
            elif "google" in query_lower or "goog" in query_lower:
                refined_query = "GOOGL stock price"
            else:
                refined_query = f"current stock price {query}"
        
        print(f"'{query}' -> '{refined_query}'")

if __name__ == "__main__":
    print("🧪 Testing stock price extraction functionality...")
    test_stock_price_extraction()
    test_query_refinement()
    print("\n✅ Test completed!")