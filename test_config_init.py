#!/usr/bin/env python
"""
Test script to check config initialization issues
"""

import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_step_by_step():
    """Test config initialization step by step"""
    print("🔍 Testing config initialization step by step...")
    
    try:
        print("1. Importing Config class...")
        from app.config import Config
        print("✅ Config class imported")
        
        print("2. Creating Config instance...")
        config = Config()
        print("✅ Config instance created")
        
        print("3. Checking local mode...")
        print(f"   Local mode: {config.is_local_mode}")
        
        print("4. Checking local model handler...")
        print(f"   Local model handler: {config.local_model_handler}")
        
        print("5. Testing manual initialization...")
        # Try to manually initialize the local model handler
        config._initialize_local_model_handler()
        print("✅ Manual initialization completed")
        print(f"   Final local model handler: {config.local_model_handler}")
        
        return True
    except Exception as e:
        print(f"❌ Config initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting config initialization test...")
    
    success = test_config_step_by_step()
    
    if success:
        print("\n🎉 Config initialization test passed!")
    else:
        print("\n❌ Config initialization test failed.")
    
    sys.exit(0 if success else 1)