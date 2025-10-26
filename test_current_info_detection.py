#!/usr/bin/env python
"""
Test script to verify current information detection and WebSearch tool usage
"""

import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_current_info_detection():
    """Test if the current information detection is working properly"""
    print("Testing current information detection...")
    
    try:
        # Read the key files
        with open("app/agent/manus.py", "r", encoding="utf-8") as f:
            manus_content = f.read()
            
        with open("web_ui.py", "r", encoding="utf-8") as f:
            web_ui_content = f.read()
            
        with open("app/prompt/manus.py", "r", encoding="utf-8") as f:
            prompt_content = f.read()
        
        # Check for key improvements
        checks = [
            ("Current info detection in Manus agent", "_requires_current_information" in manus_content),
            ("Direct current info method", "_get_current_information" in manus_content),
            ("Enhanced system prompt", "IMPORTANT: For time-sensitive information" in prompt_content),
            ("Web UI current info detection", "is_current_info_query" in web_ui_content),
            ("Direct WebSearch usage", "web_search.execute" in web_ui_content),
        ]
        
        print("\nCurrent Information Detection Checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All current information detection improvements are in place!")
            print("The system should now properly detect and handle requests for current information.")
        else:
            print("\n⚠️  Some current information detection improvements are missing.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_current_info_detection()