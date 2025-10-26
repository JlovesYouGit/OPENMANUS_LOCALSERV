#!/usr/bin/env python
"""
Test script to verify seamless tool usage integration
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agent.manus import Manus
from app.tool.web_search import WebSearch
from app.tool.python_execute import PythonExecute

async def test_current_information_detection():
    """Test the agent's ability to detect and handle current information requests"""
    print("Testing current information detection...")
    
    agent = await Manus.create()
    
    # Test cases for current information queries
    test_cases = [
        "What is the current price of Apple stock?",
        "What's the weather like today?",
        "What time is it right now?",
        "What are the latest news headlines?",
        "What is today's date?"
    ]
    
    for i, task in enumerate(test_cases):
        print(f"\nTest {i+1}: {task}")
        result = agent._requires_current_information(task)
        print(f"Requires current information: {result}")
        
        if result:
            print("Using WebSearch tool directly...")
            response = await agent._get_current_information(task)
            print(f"Response: {response[:200]}...")  # Show first 200 characters

async def test_code_execution_detection():
    """Test the agent's ability to detect and handle code execution requests"""
    print("\nTesting code execution detection...")
    
    agent = await Manus.create()
    
    # Test cases for code execution queries
    test_cases = [
        "Write a Python function to calculate factorial",
        "Execute a script that prints 'Hello, World!'",
        "Run code to sort a list of numbers",
        "Calculate 15 * 24 using Python"
    ]
    
    for i, task in enumerate(test_cases):
        print(f"\nTest {i+1}: {task}")
        result = agent._requires_code_execution(task)
        print(f"Requires code execution: {result}")
        
        if result:
            print("Using PythonExecute tool directly...")
            response = await agent._get_code_execution(task)
            print(f"Response: {response}")

async def test_web_search_tool():
    """Test the WebSearch tool directly"""
    print("\nTesting WebSearch tool...")
    
    web_search = WebSearch()
    
    # Test a current information query
    response = await web_search.execute(
        query="current Apple stock price",
        num_results=3,
        fetch_content=True
    )
    
    if not response.error and response.results:
        result = response.results[0]
        content = result.raw_content or result.description
        print(f"Search result: {content[:300]}...")  # Show first 300 characters
        print(f"Source: {result.url}")
    else:
        print(f"Search failed: {response.error or 'No results found'}")

async def test_python_execute_tool():
    """Test the PythonExecute tool directly"""
    print("\nTesting PythonExecute tool...")
    
    python_tool = PythonExecute()
    
    # Test executing a simple Python script
    code = """
print("Testing Python execution tool")
x = 10
y = 20
result = x + y
print(f"The sum of {x} and {y} is {result}")
"""
    
    response = await python_tool.execute(code=code, timeout=30)
    
    if response.get("success", False):
        print(f"Execution result: {response.get('observation', 'No output')}")
    else:
        print(f"Execution failed: {response.get('observation', 'Unknown error')}")

async def main():
    """Run all tests"""
    print("🔍 Testing seamless tool usage integration...")
    
    try:
        await test_current_information_detection()
        await test_code_execution_detection()
        await test_web_search_tool()
        await test_python_execute_tool()
        
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())