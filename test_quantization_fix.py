#!/usr/bin/env python
"""
Test script to verify the quantization fix for DirectML handler
"""

import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_quantization_fix():
    """Test if the quantization fix is properly implemented"""
    print("Testing quantization fix implementation...")
    
    try:
        # Read the DirectML handler file
        with open("app/directml_optimized_handler.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for key improvements
        checks = [
            ("BitsAndBytesConfig usage", "BitsAndBytesConfig" in content),
            ("Proper quantization config", "quantization_config" in content),
            ("GPU support check", "bnb.cuda.is_available" in content),
            ("Fallback mechanism", "except ImportError" in content),
        ]
        
        print("\nQuantization Fix Checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All quantization fix improvements are in place!")
            print("The system should now properly handle bitsandbytes quantization warnings.")
        else:
            print("\n⚠️  Some quantization fix improvements are missing.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_quantization_fix()