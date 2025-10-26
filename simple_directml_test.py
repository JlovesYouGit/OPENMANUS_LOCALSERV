"""
Simple test for DirectML handler
"""

import sys
import os

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_directml_handler():
    """Test the DirectML handler directly"""
    print("🔧 Testing DirectML Handler Directly")
    print("=" * 40)
    
    try:
        # Test DirectML import
        try:
            import torch_directml
            print("✅ DirectML import successful")
            print(f"   Available: {torch_directml.is_available()}")
            if torch_directml.is_available():
                print(f"   Device count: {torch_directml.device_count()}")
                print(f"   Current device: {torch_directml.device()}")
        except Exception as e:
            print(f"❌ DirectML import failed: {e}")
            return False
        
        # Test handler import
        try:
            from app.directml_optimized_handler import DirectMLOptimizedHandler
            print("✅ DirectML handler import successful")
            
            # Create a simple config
            config = {
                "llm": {
                    "lightweight": {
                        "model_path": "./models/tinyllama",
                    }
                }
            }
            
            # Initialize handler
            handler = DirectMLOptimizedHandler(config)
            print(f"✅ Handler initialized with device: {handler.device}")
            
        except Exception as e:
            print(f"❌ Handler test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ General test error: {e}")
        return False

if __name__ == "__main__":
    success = test_directml_handler()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 DirectML setup is working correctly!")
    else:
        print("⚠️  DirectML setup has issues.")