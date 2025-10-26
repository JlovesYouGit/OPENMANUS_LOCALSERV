#!/usr/bin/env python
"""
Test script to verify the logout feature has been added to the Settings page
"""

import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_settings_logout_feature():
    """Test that the logout feature has been added to the Settings component"""
    
    # Path to the Settings component file
    settings_file_path = Path("newweb/quantum-canvas-design/src/components/Settings.tsx")
    full_path = Path(__file__).parent / settings_file_path
    
    if not full_path.exists():
        print(f"❌ Settings file not found at {full_path}")
        return False
    
    # Read the file content
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key elements that indicate the logout feature has been added
    required_elements = [
        "handleLogout",
        "useAuth",
        "useNavigate",
        "logout()",
        "navigate",  # Navigate function call
        "LogOut",  # Import of the LogOut icon
        "Account",  # Account section header
        "Log Out",  # Logout button text
        "destructive"  # Button variant for logout
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print("❌ Missing required elements in Settings component:")
        for element in missing_elements:
            print(f"  - {element}")
        return False
    
    print("✅ All required elements for logout feature found in Settings component")
    print("✅ Logout feature has been successfully added to the Settings page")
    return True

def main():
    """Run the settings logout feature test"""
    print("Testing Settings page logout feature...\n")
    
    try:
        success = test_settings_logout_feature()
        if success:
            print("\n✅ Settings logout feature test passed!")
            return 0
        else:
            print("\n❌ Settings logout feature test failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())