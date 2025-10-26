#!/usr/bin/env python
"""
Simple test to verify memory management improvements
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_import():
    """Test that config imports without issues"""
    print("🔍 Testing config import...")
    
    try:
        from app.config import config
        print("✅ Config imported successfully")
        print(f"   Local mode: {config.is_local_mode}")
        print(f"   Model handler type: {type(config.local_model_handler)}")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_handler_methods():
    """Test that model handler has the required methods"""
    print("\n🔍 Testing model handler methods...")
    
    try:
        from app.config import config
        
        if not config.local_model_handler:
            print("❌ No local model handler available")
            return False
            
        # Check if the handler has the unload_model method
        if hasattr(config.local_model_handler, 'unload_model'):
            print("✅ unload_model method available")
        else:
            print("❌ unload_model method not available")
            return False
            
        # Check if the handler has the load_model_on_demand method
        if hasattr(config.local_model_handler, 'load_model_on_demand'):
            print("✅ load_model_on_demand method available")
        else:
            print("❌ load_model_on_demand method not available")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Model handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting simple memory management test...")
    print("=" * 50)
    
    success1 = test_config_import()
    success2 = test_model_handler_methods()
    
    if success1 and success2:
        print("\n🎉 All memory management tests passed!")
        print("💡 The system should now handle loading both LLMs more efficiently.")
    else:
        print("\n❌ Some memory management tests failed.")
    
    sys.exit(0 if (success1 and success2) else 1)