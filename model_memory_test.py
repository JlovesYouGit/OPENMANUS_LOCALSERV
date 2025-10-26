#!/usr/bin/env python
"""
Test script to verify model memory management improvements
"""

import sys
import os
import asyncio
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_model_loading():
    """Test loading models with memory management"""
    print("🔍 Testing model loading with memory management...")
    
    try:
        # Import the config to get the model handler
        from app.config import config
        
        if not config.local_model_handler:
            print("❌ No local model handler available")
            return False
            
        print(f"✅ Using model handler: {type(config.local_model_handler)}")
        
        # Test loading TinyLlama first
        print("\n1. Testing TinyLlama loading...")
        start_time = time.time()
        success1 = await config.local_model_handler.load_model_on_demand("tinyllama")
        load_time1 = time.time() - start_time
        
        if success1:
            print(f"✅ TinyLlama loaded successfully in {load_time1:.2f}s")
        else:
            print("❌ Failed to load TinyLlama")
            return False
            
        # Test loading Phi-3 (this should unload TinyLlama first)
        print("\n2. Testing Phi-3 loading (should unload TinyLlama first)...")
        start_time = time.time()
        success2 = await config.local_model_handler.load_model_on_demand("phi3")
        load_time2 = time.time() - start_time
        
        if success2:
            print(f"✅ Phi-3 loaded successfully in {load_time2:.2f}s")
            # Check if TinyLlama was unloaded
            if hasattr(config.local_model_handler, 'model_loaded'):
                tinyllama_still_loaded = config.local_model_handler.model_loaded.get("tinyllama", False)
                if not tinyllama_still_loaded:
                    print("✅ TinyLlama was properly unloaded to free memory")
                else:
                    print("⚠️ TinyLlama is still loaded (may cause memory issues)")
        else:
            print("❌ Failed to load Phi-3")
            return False
            
        # Test switching back to TinyLlama
        print("\n3. Testing switching back to TinyLlama...")
        start_time = time.time()
        success3 = await config.local_model_handler.load_model_on_demand("tinyllama")
        load_time3 = time.time() - start_time
        
        if success3:
            print(f"✅ TinyLlama loaded again successfully in {load_time3:.2f}s")
        else:
            print("❌ Failed to reload TinyLlama")
            return False
            
        print("\n🎉 All model loading tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during model loading test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Starting model memory management test...")
    print("=" * 50)
    
    success = await test_model_loading()
    
    if success:
        print("\n🎉 Model memory management is working correctly!")
    else:
        print("\n❌ Model memory management test failed.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)