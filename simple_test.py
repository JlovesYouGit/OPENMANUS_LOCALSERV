#!/usr/bin/env python
"""
Simple test to check if config can be imported without hanging
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_import():
    """Test importing config without hanging"""
    print("🔍 Testing simple config import...")
    
    start_time = time.time()
    
    try:
        # This should not hang
        from app.config import config
        end_time = time.time()
        
        print(f"✅ Config imported successfully in {end_time - start_time:.2f} seconds")
        print(f"   - is_local_mode: {config.is_local_mode}")
        print(f"   - local_model_handler: {type(config.local_model_handler)}")
        return True
    except Exception as e:
        end_time = time.time()
        print(f"❌ Config import failed after {end_time - start_time:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting simple config import test...")
    
    success = test_simple_import()
    
    if success:
        print("\n🎉 Simple import test passed!")
    else:
        print("\n❌ Simple import test failed.")
    
    sys.exit(0 if success else 1)