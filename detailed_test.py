#!/usr/bin/env python
"""
Detailed test script to identify where the startup process hangs
"""

import sys
import os
import traceback
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_step_by_step():
    """Test each step of the initialization process"""
    print("🔍 Testing step by step...")
    
    try:
        print("1. Importing Flask...")
        from flask import Flask
        print("✅ Flask imported successfully")
    except Exception as e:
        print(f"❌ Flask import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("2. Importing config module...")
        import app.config
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config module import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("3. Accessing config instance...")
        from app.config import config
        print("✅ Config instance accessed successfully")
    except Exception as e:
        print(f"❌ Config instance access failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("4. Checking config initialization status...")
        print(f"   - is_local_mode: {config.is_local_mode}")
        print(f"   - _initialized: {config._initialized}")
        print("✅ Config status check completed")
    except Exception as e:
        print(f"❌ Config status check failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("5. Checking local model handler...")
        print(f"   - local_model_handler: {config.local_model_handler}")
        print("✅ Local model handler check completed")
    except Exception as e:
        print(f"❌ Local model handler check failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("6. Testing query manager import...")
        from app.utils.query_manager import query_manager
        print("✅ Query manager imported successfully")
    except Exception as e:
        print(f"❌ Query manager import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting detailed OpenManus diagnostics...")
    
    start_time = time.time()
    success = test_step_by_step()
    end_time = time.time()
    
    print(f"\n⏱️  Test completed in {end_time - start_time:.2f} seconds")
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    sys.exit(0 if success else 1)