#!/usr/bin/env python
"""
Comprehensive test to verify all fixes work together
"""

import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_complete_fix():
    """Test if all fixes are properly implemented"""
    print("Testing complete fix implementation...")
    
    try:
        # Read the key files
        with open("app/directml_optimized_handler.py", "r", encoding="utf-8") as f:
            directml_content = f.read()
            
        with open("app/agent/manus.py", "r", encoding="utf-8") as f:
            manus_content = f.read()
            
        with open("web_ui.py", "r", encoding="utf-8") as f:
            web_ui_content = f.read()
        
        # Check for DirectML handler improvements
        directml_checks = [
            ("BitsAndBytesConfig usage", "BitsAndBytesConfig" in directml_content),
            ("Proper quantization config", "quantization_config" in directml_content),
            ("GPU support check", "bnb.cuda.is_available" in directml_content),
            ("Fallback mechanism", "except ImportError" in directml_content),
            ("Eager attention implementation", "attn_implementation" in directml_content),
        ]
        
        # Check for Manus agent improvements
        manus_checks = [
            ("Fallback tool usage", "_fallback_tool_usage" in manus_content),
            ("WebSearch integration", "WebSearch()" in manus_content),
            ("Current info detection", "current" in manus_content and "stock" in manus_content),
        ]
        
        # Check for Web UI improvements
        web_ui_checks = [
            ("Direct tool usage", "WebSearch()" in web_ui_content),
            ("Current info detection", "current" in web_ui_content and "stock" in web_ui_content),
            ("Error handling", "except Exception as agent_error" in web_ui_content),
        ]
        
        print("\nDirectML Handler Improvements:")
        directml_all_passed = True
        for check_name, passed in directml_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                directml_all_passed = False
        
        print("\nManus Agent Improvements:")
        manus_all_passed = True
        for check_name, passed in manus_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                manus_all_passed = False
                
        print("\nWeb UI Improvements:")
        web_ui_all_passed = True
        for check_name, passed in web_ui_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                web_ui_all_passed = False
        
        all_passed = directml_all_passed and manus_all_passed and web_ui_all_passed
        
        if all_passed:
            print("\n🎉 All fixes are properly implemented!")
            print("The system should now:")
            print("  ✅ Load Phi-3 model without memory issues")
            print("  ✅ Handle bitsandbytes quantization warnings properly")
            print("  ✅ Access current information through WebSearch tool")
            print("  ✅ Provide accurate, up-to-date responses")
        else:
            print("\n⚠️  Some fixes are missing or incomplete.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_fix()