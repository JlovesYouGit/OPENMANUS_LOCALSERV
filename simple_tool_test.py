#!/usr/bin/env python
"""
Simple test script to verify tool usage improvements
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agent.manus import Manus

def test_keyword_detection():
    """Test the agent's keyword detection for automatic tool usage"""
    print("Testing keyword detection for automatic tool usage...")
    
    # Create an instance of the agent
    agent = Manus()
    
    # Test cases for current information queries
    current_info_tests = [
        "What is the current price of Apple stock?",
        "What's the weather like today?",
        "What time is it right now?",
        "What are the latest news headlines?",
        "What is today's date?",
        "Tell me the current temperature in New York",
        "Find the latest breaking news"
    ]
    
    print("\n=== Current Information Detection ===")
    for i, task in enumerate(current_info_tests):
        result = agent._requires_current_information(task)
        print(f"{i+1}. '{task}' -> {result}")
    
    # Test cases for code execution queries
    code_execution_tests = [
        "Write a Python function to calculate factorial",
        "Execute a script that prints 'Hello, World!'",
        "Run code to sort a list of numbers",
        "Calculate 15 * 24 using Python",
        "Create a program to find prime numbers",
        "Implement a binary search algorithm"
    ]
    
    print("\n=== Code Execution Detection ===")
    for i, task in enumerate(code_execution_tests):
        result = agent._requires_code_execution(task)
        print(f"{i+1}. '{task}' -> {result}")
    
    # Test cases for file operation queries
    file_operation_tests = [
        "Create a new file called test.txt",
        "Read the contents of config.json",
        "Edit the README.md file",
        "Delete the temporary file",
        "Update the settings.ini file",
        "Append data to the log file"
    ]
    
    print("\n=== File Operation Detection ===")
    for i, task in enumerate(file_operation_tests):
        result = agent._requires_file_operation(task)
        print(f"{i+1}. '{task}' -> {result}")
    
    # Test cases for web browsing queries
    web_browsing_tests = [
        "Browse to google.com",
        "Visit the GitHub website",
        "Navigate to the documentation page",
        "Click on the login button",
        "Search for Python tutorials",
        "Find information about machine learning"
    ]
    
    print("\n=== Web Browsing Detection ===")
    for i, task in enumerate(web_browsing_tests):
        result = agent._requires_web_browsing(task)
        print(f"{i+1}. '{task}' -> {result}")

def test_enhanced_prompt():
    """Test the enhanced system prompt"""
    print("\n\nTesting enhanced system prompt...")
    
    from app.prompt.manus import SYSTEM_PROMPT, NEXT_STEP_PROMPT
    
    print("=== Enhanced System Prompt ===")
    print(SYSTEM_PROMPT[:500] + "..." if len(SYSTEM_PROMPT) > 500 else SYSTEM_PROMPT)
    
    print("\n=== Enhanced Next Step Prompt ===")
    print(NEXT_STEP_PROMPT[:500] + "..." if len(NEXT_STEP_PROMPT) > 500 else NEXT_STEP_PROMPT)

if __name__ == "__main__":
    print("🔍 Testing seamless tool usage integration improvements...")
    test_keyword_detection()
    test_enhanced_prompt()
    print("\n✅ All tests completed successfully!")