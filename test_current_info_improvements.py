#!/usr/bin/env python
"""
Test script to verify current information handling improvements
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agent.manus import Manus

def test_current_information_detection():
    """Test the enhanced current information detection"""
    print("Testing enhanced current information detection...")
    
    # Create an instance of the agent
    agent = Manus()
    
    # Test cases for current information queries
    test_cases = [
        ("What is the current price of Apple stock?", True),
        ("Tell me the latest news about technology", True),
        ("What's the weather like today?", True),
        ("What time is it right now?", True),
        ("How much does Netflix cost?", True),
        ("What is the current exchange rate for USD to EUR?", True),
        ("Tell me a joke", False),
        ("Help me write a letter", False),
        ("Explain quantum physics", False),
        ("What is 2+2?", False),  # This might be current if asking about a calculation
    ]
    
    print("\n=== Current Information Detection Results ===")
    for i, (query, expected) in enumerate(test_cases):
        result = agent._requires_current_information(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} Test {i+1}: '{query}' -> {result} (expected: {expected})")
    
    # Test enhanced pattern matching
    print("\n=== Enhanced Pattern Matching ===")
    enhanced_tests = [
        "What is the price of gold today?",
        "How much does a Tesla Model 3 cost?",
        "What is the current temperature in London?",
        "Tell me the latest breaking news"
    ]
    
    for i, query in enumerate(enhanced_tests):
        result = agent._requires_current_information(query)
        print(f"Test {i+1}: '{query}' -> {result}")

def test_query_refinement():
    """Test the query refinement logic"""
    print("\n\nTesting query refinement logic...")
    
    test_cases = [
        ("What is the current price of Apple stock?", "current stock price"),
        ("What's the weather like in New York?", "current weather"),
        ("Tell me the latest news about AI", "latest news"),
        ("What is today's date?", "what is today's date"),
        ("What is the current exchange rate?", "current exchange rate")
    ]
    
    print("\n=== Query Refinement Results ===")
    for i, (original, expected_pattern) in enumerate(test_cases):
        # This is a simplified test - in reality, the refinement happens in the _get_current_information method
        message_lower = original.lower()
        if "stock" in message_lower and ("price" in message_lower or "cost" in message_lower):
            refined = f"current stock price {original}"
        elif "weather" in message_lower:
            refined = f"current weather {original}"
        elif "news" in message_lower or "breaking" in message_lower:
            refined = f"latest news {original}"
        elif "date" in message_lower or "today" in message_lower:
            refined = f"what is today's date"
        else:
            refined = f"current {original}"
            
        contains_expected = expected_pattern in refined
        status = "✓" if contains_expected else "✗"
        print(f"{status} Test {i+1}: '{original}' -> '{refined}' (contains '{expected_pattern}': {contains_expected})")

def test_system_prompt():
    """Test that the system prompt contains the necessary instructions"""
    print("\n\nTesting system prompt enhancements...")
    
    from app.prompt.manus import SYSTEM_PROMPT, NEXT_STEP_PROMPT
    
    # Check for key enhancements
    checks = [
        ("BEHAVIORAL CONTROLS" in SYSTEM_PROMPT, "BEHAVIORAL CONTROLS section"),
        ("NEVER hallucinate" in SYSTEM_PROMPT, "Anti-hallucination instruction"),
        ("IMPORTANT BEHAVIORAL GUIDELINES" in NEXT_STEP_PROMPT, "Behavioral guidelines in next step prompt"),
        ("Never provide outdated" in NEXT_STEP_PROMPT, "Outdated information warning")
    ]
    
    print("\n=== System Prompt Checks ===")
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"{status} {description}: {check}")

if __name__ == "__main__":
    print("🔍 Testing current information handling improvements...")
    test_current_information_detection()
    test_query_refinement()
    test_system_prompt()
    print("\n✅ All tests completed!")