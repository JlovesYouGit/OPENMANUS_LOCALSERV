#!/usr/bin/env python
"""
Simple test to check if search engines are working
"""

def test_duckduckgo():
    """Test DuckDuckGo search"""
    print("Testing DuckDuckGo search...")
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text("Apple stock price", max_results=3)
        print(f"DuckDuckGo returned {len(list(results))} results")
        for result in results:
            print(f"  - {result}")
        return True
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
        return False

def test_google():
    """Test Google search"""
    print("Testing Google search...")
    try:
        from googlesearch import search
        results = search("Apple stock price", num_results=3, advanced=True)
        results_list = list(results)
        print(f"Google returned {len(results_list)} results")
        for result in results_list:
            print(f"  - {result}")
        return True
    except Exception as e:
        print(f"Google search failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing search engines...")
    ddg_works = test_duckduckgo()
    google_works = test_google()
    
    if ddg_works or google_works:
        print("✅ At least one search engine is working")
    else:
        print("❌ Both search engines failed")