#!/usr/bin/env python
"""
Simple test for current information handling
"""

# Test the current information detection directly
def test_detection():
    # Define the enhanced keywords
    current_keywords = [
        "stock", "price", "current", "today", "now", "latest", 
        "recent", "up-to-date", "real-time", "live", "market",
        "weather", "temperature", "news", "breaking", "time",
        "date", "moment", "presently", "currently", "right now",
        "this moment", "at present", "financial", "trading", "exchange"
    ]
    
    # Test queries
    test_queries = [
        "What is the current price of Apple stock?",
        "Tell me today's weather",
        "What's the latest news?",
        "How much does a Tesla cost right now?",
        "Explain photosynthesis"
    ]
    
    print("Testing current information detection:")
    for query in test_queries:
        is_current = any(keyword in query.lower() for keyword in current_keywords)
        # Additional pattern checks
        if not is_current:
            query_lower = query.lower()
            if "what is" in query_lower and any(word in query_lower for word in ["price", "cost", "rate"]):
                is_current = True
            elif "how much" in query_lower and any(word in query_lower for word in ["cost", "price"]):
                is_current = True
        
        print(f"'{query}' -> {is_current}")

if __name__ == "__main__":
    test_detection()