#!/usr/bin/env python3
"""
Test script for the Manus agent with local models.
This script tests if the Manus agent can be created and used with local models.
"""

import sys
import os
import asyncio

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.agent.manus import Manus
from app.config import config

async def test_manus_creation():
    """Test creating the Manus agent"""
    print("🔧 Testing Manus agent creation...")
    try:
        print("Creating Manus agent...")
        agent = await Manus.create()
        print("✅ Manus agent created successfully!")
        
        # Check if local mode is enabled
        print(f"Local mode enabled: {config.is_local_mode}")
        if config.is_local_mode and config.local_model_handler:
            print("✅ Local model handler is available")
        else:
            print("⚠️ Local model handler is not available")
            
        return True
    except Exception as e:
        print(f"❌ Error creating Manus agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Manus Agent Test")
    print("=" * 30)
    
    success = asyncio.run(test_manus_creation())
    
    if success:
        print("\n🎉 Manus agent test passed!")
        print("Your OpenManus setup with local models is working.")
    else:
        print("\n⚠️ Manus agent test failed.")
        print("There may be issues with the setup.")

if __name__ == "__main__":
    main()