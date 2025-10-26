#!/usr/bin/env python
"""
Test script for the quality filter system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.output_filter import filter_model_output
from app.utils.query_analyzer import analyze_user_query

def test_quality_filter():
    """Test the quality filter system"""
    print("Testing Quality Filter System")
    
    # Test cases with different query-response pairs
    test_cases = [
        # Case 1: High overlap, should pass
        {
            "query": "What is the weather like today?",
            "response": "The weather today is sunny with a high of 75°F and low of 55°F. It's a beautiful day!",
            "expected_block": False
        },
        # Case 2: Low overlap but natural response, should pass with relaxed threshold
        {
            "query": "Tell me about artificial intelligence",
            "response": "Artificial intelligence is a fascinating field that involves creating systems that can perform tasks typically requiring human intelligence. It has many applications in modern technology.",
            "expected_block": False
        },
        # Case 3: Hallucinated content, should be blocked
        {
            "query": "How do I install Python?",
            "response": "You can download Python from stackoverflow.com and follow the installation guide there.",
            "expected_block": True
        },
        # Case 4: Normal conversation, should pass
        {
            "query": "Hello, how are you?",
            "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
            "expected_block": False
        }
    ]
    
    print(f"Running {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        response = test_case["response"]
        expected_block = test_case["expected_block"]
        
        print(f"Test Case {i}:")
        print(f"  Query: {query}")
        print(f"  Response: {response}")
        
        # Analyze the query
        analysis = analyze_user_query(query)
        print(f"  Query Type: {analysis.query_type.value}")
        print(f"  Confidence: {analysis.confidence:.2f}")
        
        # Filter the response
        should_block, filtered_response, metadata = filter_model_output(query, response)
        
        print(f"  Should Block: {should_block} (expected: {expected_block})")
        print(f"  Overlap Score: {metadata.get('overlap_score', 0):.2f}")
        print(f"  Is Hallucinated: {metadata.get('is_hallucinated', False)}")
        
        # Check if result matches expectation
        if should_block == expected_block:
            print(f"  Result: ✅ PASS")
        else:
            print(f"  Result: ❌ FAIL")
        
        if should_block:
            print(f"  Filtered Response: {filtered_response}")
        
        print()

if __name__ == "__main__":
    test_quality_filter()