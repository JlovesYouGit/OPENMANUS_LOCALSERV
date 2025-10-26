#!/usr/bin/env python
"""
Test script to verify enhanced time/date search functionality
"""

import re
from datetime import datetime
import pytz

def test_time_date_patterns():
    """Test time and date pattern matching"""
    print("🔍 Testing time and date pattern matching...")
    
    # Test time patterns
    time_test_strings = [
        "The current time is 14:30:25",
        "Meeting scheduled for 2:30 PM",
        "Event starts at 9:00 AM",
        "The time now is 16:45",
        "Appointment at 11:15 AM"
    ]
    
    time_patterns = [
        r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\s*(?:AM|PM|am|pm)?\b',  # 14:30 or 2:30 PM
        r'\b(?:at\s+)?([0-1]?[0-9]|2[0-3])\s*(?::\s*[0-5][0-9])?\s*(?:AM|PM|am|pm)\b',  # 2:30 PM
    ]
    
    print("\n--- Time Pattern Matching ---")
    for test_string in time_test_strings:
        print(f"\nTesting: '{test_string}'")
        for pattern in time_patterns:
            matches = re.findall(pattern, test_string)
            if matches:
                print(f"  Pattern '{pattern}' found: {matches}")
    
    # Test date patterns
    date_test_strings = [
        "Today is 2025-10-23",
        "The event is on October 23, 2025",
        "Deadline: 23 October 2025",
        "Date: 2025/10/23",
        "Meeting on January 5, 2026"
    ]
    
    date_patterns = [
        r'\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2})\b',  # 2025-10-23
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+20\d{2}\b',  # October 23, 2025
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+20\d{2}\b',  # 23 October 2025
    ]
    
    print("\n--- Date Pattern Matching ---")
    for test_string in date_test_strings:
        print(f"\nTesting: '{test_string}'")
        for pattern in date_patterns:
            matches = re.findall(pattern, test_string)
            if matches:
                print(f"  Pattern '{pattern}' found: {matches}")

def test_current_time_injection():
    """Test current time injection into search queries"""
    print("\n🔍 Testing current time injection...")
    
    # Get current time
    current_time = datetime.now()
    try:
        user_tz = pytz.timezone('US/Eastern')
        localized_time = current_time.astimezone(user_tz)
        date_str = localized_time.strftime("%Y-%m-%d")
        time_str = localized_time.strftime("%H:%M:%S")
        timezone_str = str(user_tz)
    except:
        date_str = current_time.strftime("%Y-%m-%d")
        time_str = current_time.strftime("%H:%M:%S")
        timezone_str = "UTC"
    
    print(f"Current date: {date_str}")
    print(f"Current time: {time_str}")
    print(f"Timezone: {timezone_str}")
    
    # Test query refinement with time context
    test_queries = [
        "What time is it?",
        "What is today's date?",
        "What is the current stock price of Apple?",
        "What is the weather today?",
        "What are the latest news headlines?"
    ]
    
    print("\n--- Query Refinement with Time Context ---")
    for query in test_queries:
        query_lower = query.lower()
        refined_query = query
        
        if "stock" in query_lower and ("price" in query_lower or "cost" in query_lower):
            if "apple" in query_lower or "aapl" in query_lower:
                refined_query = f"AAPL stock price {date_str}"
            elif "microsoft" in query_lower or "msft" in query_lower:
                refined_query = f"MSFT stock price {date_str}"
            elif "google" in query_lower or "goog" in query_lower:
                refined_query = f"GOOGL stock price {date_str}"
            else:
                refined_query = f"current stock price {query} {date_str}"
        elif "weather" in query_lower:
            refined_query = f"current weather {query} {date_str}"
        elif "news" in query_lower or "breaking" in query_lower:
            refined_query = f"latest news {query} {date_str}"
        elif any(time_word in query_lower for time_word in ["time", "date", "calendar", "schedule"]):
            refined_query = f"{query} {date_str} {time_str} {timezone_str}"
        else:
            refined_query = f"current {query} {date_str}"
            
        print(f"'{query}' -> '{refined_query}'")

def test_keyword_expansion():
    """Test expanded keyword detection for current information"""
    print("\n🔍 Testing expanded keyword detection...")
    
    expanded_keywords = [
        "stock", "price", "current", "today", "now", "latest", 
        "recent", "up-to-date", "real-time", "live", "market",
        "weather", "temperature", "news", "breaking", "time",
        "date", "moment", "presently", "currently", "right now",
        "this moment", "at present", "financial", "trading", "exchange",
        "calendar", "schedule", "event", "meeting", "appointment"
    ]
    
    test_queries = [
        "What time is my meeting?",
        "Do I have any appointments today?",
        "What events are scheduled for this week?",
        "What is the current price of Apple stock?",
        "Tell me today's weather forecast",
        "What are the latest breaking news headlines?",
        "What is the exchange rate for USD to EUR?",
        "Do I have any scheduled events tomorrow?"
    ]
    
    print("\n--- Keyword Detection ---")
    for query in test_queries:
        query_lower = query.lower()
        has_keyword = any(keyword in query_lower for keyword in expanded_keywords)
        # Additional pattern checks
        time_patterns = [
            r"what time", r"current time", r"time now", 
            r"what date", r"today's date", r"current date"
        ]
        has_time_pattern = any(re.search(pattern, query_lower) for pattern in time_patterns)
        
        print(f"'{query}' -> Keywords: {has_keyword}, Time patterns: {has_time_pattern}")

if __name__ == "__main__":
    print("🧪 Testing enhanced time/date search functionality...")
    test_time_date_patterns()
    test_current_time_injection()
    test_keyword_expansion()
    print("\n✅ All tests completed!")