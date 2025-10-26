#!/usr/bin/env python
"""
Test script to check web UI startup issues
"""

import sys
import os
import traceback

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing the main modules to identify any issues"""
    print("🔍 Testing imports...")
    
    try:
        print("Importing Flask...")
        from flask import Flask
        print("✅ Flask imported successfully")
    except Exception as e:
        print(f"❌ Flask import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("Importing config...")
        from app.config import config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("Importing query manager...")
        from app.utils.query_manager import query_manager
        print("✅ Query manager imported successfully")
    except Exception as e:
        print(f"❌ Query manager import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("Importing Manus agent...")
        from app.agent.manus import Manus
        print("✅ Manus agent imported successfully")
    except Exception as e:
        print(f"❌ Manus agent import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_config_initialization():
    """Test config initialization"""
    print("\n🔍 Testing config initialization...")
    
    try:
        from app.config import config
        print(f"✅ Config instance created: {config}")
        print(f"✅ Local mode: {config.is_local_mode}")
        print(f"✅ Local model handler: {config.local_model_handler}")
        return True
    except Exception as e:
        print(f"❌ Config initialization failed: {e}")
        traceback.print_exc()
        return False

def test_web_ui_import():
    """Test importing the web UI"""
    print("\n🔍 Testing web UI import...")
    
    try:
        import web_ui
        print("✅ Web UI imported successfully")
        return True
    except Exception as e:
        print(f"❌ Web UI import failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting OpenManus startup diagnostics...")
    
    success = True
    success &= test_imports()
    success &= test_config_initialization()
    success &= test_web_ui_import()
    
    if success:
        print("\n🎉 All tests passed! The system should start correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    sys.exit(0 if success else 1)