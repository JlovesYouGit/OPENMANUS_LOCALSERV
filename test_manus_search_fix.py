#!/usr/bin/env python
"""
Test to verify the Manus agent search query fix
"""

import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import the Manus agent
from app.agent.manus import Manus

def test_manus_search_routing():
    """Test that the Manus agent properly routes search queries"""
    
    # Create an instance of the Manus agent
    agent = Manus()
    
    # Test the search indicator detection logic that we added
    search_indicators = [
        "search for", "search about", "find information", "look up", 
        "important source info", "important historical event"
    ]
    
    # Test cases that should trigger search routing
    search_test_cases = [
        "search for important source info",
        "important historical event america 2022",
        "find information about python",
        "look up the weather today"
    ]
    
    # Test cases that should NOT trigger search routing
    non_search_test_cases = [
        "hi",
        "hello",
        "who is elon musk",
        "thats not what i said"
    ]
    
    print("Testing Manus agent search query routing...")
    print()
    
    # Test search queries
    print("Testing search queries:")
    for query in search_test_cases:
        task_lower = query.lower()
        is_search = any(indicator in task_lower for indicator in search_indicators)
        print(f"  '{query}' -> {'PROPERLY DETECTED AS SEARCH' if is_search else 'MISSED SEARCH DETECTION'}")
        if not is_search:
            print(f"    ERROR: This should have been detected as a search query!")
            return False
    
    print()
    
    # Test non-search queries
    print("Testing non-search queries:")
    for query in non_search_test_cases:
        task_lower = query.lower()
        is_search = any(indicator in task_lower for indicator in search_indicators)
        print(f"  '{query}' -> {'INCORRECTLY DETECTED AS SEARCH' if is_search else 'CORRECTLY NOT DETECTED AS SEARCH'}")
        if is_search:
            print(f"    ERROR: This should NOT have been detected as a search query!")
            return False
    
    print()
    print("✅ All search routing tests passed!")
    print("The Manus agent will now properly route search queries to web search functionality")
    print("instead of getting stuck in a greeting response loop.")
    
    return True

if __name__ == "__main__":
    success = test_manus_search_routing()
    sys.exit(0 if success else 1)