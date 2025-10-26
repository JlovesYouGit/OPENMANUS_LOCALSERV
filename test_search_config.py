#!/usr/bin/env python
"""
Test script to verify search configuration is working correctly
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.config import config

def test_search_config():
    """Test if search configuration is loaded correctly"""
    print("🔍 Testing search configuration...")
    
    # Check if search config is available
    search_config = config.search_config
    if search_config is None:
        print("❌ Search configuration is not loaded")
        return False
    
    print("✅ Search configuration is loaded")
    print(f"  Engine: {search_config.engine}")
    print(f"  Fallback engines: {search_config.fallback_engines}")
    print(f"  Retry delay: {search_config.retry_delay}")
    print(f"  Max retries: {search_config.max_retries}")
    print(f"  Language: {search_config.lang}")
    print(f"  Country: {search_config.country}")
    
    return True

def test_web_search_tool():
    """Test if web search tool can be instantiated and used"""
    print("\n🔍 Testing web search tool...")
    
    try:
        from app.tool.web_search import WebSearch
        web_search = WebSearch()
        print("✅ WebSearch tool instantiated successfully")
        
        # Check search engine order
        engine_order = web_search._get_engine_order()
        print(f"  Search engine order: {engine_order}")
        
        return True
    except Exception as e:
        print(f"❌ WebSearch tool failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing search configuration and web search tool...")
    
    config_ok = test_search_config()
    tool_ok = test_web_search_tool()
    
    if config_ok and tool_ok:
        print("\n✅ All tests passed! Search configuration is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")