#!/usr/bin/env python
"""
Simple test to check if the Manus agent can access current information
"""

import asyncio
import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.agent.manus import Manus

async def test_current_info():
    """Test if the Manus agent can access current information"""
    print("Testing Manus agent's ability to access current information...")
    
    try:
        # Create a Manus agent instance
        agent = await Manus.create()
        print("✅ Manus agent created successfully!")
        
        # Test asking for current date
        print("\nTesting current date query...")
        response = await agent.complex_task("What is today's date?")
        print(f"Agent response: {response}")
        
        # Test asking for current stock information
        print("\nTesting current stock information query...")
        response = await agent.complex_task("What is the current price of Apple stock?")
        print(f"Agent response: {response}")
        
        # Clean up
        await agent.cleanup()
        print("✅ Agent cleaned up successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_current_info())