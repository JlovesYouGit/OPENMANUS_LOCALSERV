#!/usr/bin/env python
"""
Test script to check config initialization process
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_initialization():
    """Test config initialization step by step"""
    print("🔍 Testing config initialization...")
    
    start_time = time.time()
    
    try:
        print("1. Starting config import...")
        import_start = time.time()
        from app.config import Config
        import_end = time.time()
        print(f"✅ Config class imported in {import_end - import_start:.2f} seconds")
    except Exception as e:
        print(f"❌ Config class import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("2. Creating config instance...")
        instance_start = time.time()
        config = Config()
        instance_end = time.time()
        print(f"✅ Config instance created in {instance_end - instance_start:.2f} seconds")
        print(f"   - is_local_mode: {config.is_local_mode}")
        print(f"   - local_model_handler: {config.local_model_handler}")
    except Exception as e:
        print(f"❌ Config instance creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    total_time = time.time() - start_time
    print(f"✅ Config initialization completed in {total_time:.2f} seconds")
    return True

if __name__ == "__main__":
    print("🚀 Starting config initialization test...")
    
    success = test_config_initialization()
    
    if success:
        print("\n🎉 Config initialization test passed!")
    else:
        print("\n❌ Config initialization test failed.")
    
    sys.exit(0 if success else 1)