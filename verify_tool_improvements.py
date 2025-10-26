#!/usr/bin/env python
"""
Simple verification script for tool usage improvements
"""

# Test the enhanced agent functionality
from app.agent.manus import Manus

def test_improvements():
    print("🔍 Verifying seamless tool usage improvements...")
    
    # Create agent instance
    agent = Manus()
    
    # Test current information detection
    test_query = "What is the current price of Apple stock?"
    is_current = agent._requires_current_information(test_query)
    print(f"Current info detection for '{test_query}': {is_current}")
    
    # Test code execution detection
    test_query = "Write a Python function to calculate factorial"
    is_code = agent._requires_code_execution(test_query)
    print(f"Code execution detection for '{test_query}': {is_code}")
    
    # Test enhanced prompts
    from app.prompt.manus import SYSTEM_PROMPT, NEXT_STEP_PROMPT
    
    print("\n=== Enhanced Prompts ===")
    print("System prompt contains 'proactively determine':", "proactively determine" in SYSTEM_PROMPT)
    print("Next step prompt contains 'proactively select':", "proactively select" in NEXT_STEP_PROMPT)
    
    print("\n✅ Verification complete!")

if __name__ == "__main__":
    test_improvements()