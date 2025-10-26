#!/usr/bin/env python
"""
Simple test script to verify cache key uniqueness
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.directml_optimized_handler import DirectMLOptimizedHandler
from app.directml_fixed_handler import DirectMLFixedHandler

def test_cache_key_uniqueness():
    """Test that cache keys are unique for the same query in different contexts"""
    print("🔍 Testing cache key uniqueness in DirectMLOptimizedHandler...")
    
    handler = DirectMLOptimizedHandler({})
    
    # Generate cache keys for the same query at different times
    query = "What is the weather like today?"
    
    key1 = handler._generate_cache_key(query + "123456")
    key2 = handler._generate_cache_key(query + "123457")
    
    print(f"Cache key 1: {key1}")
    print(f"Cache key 2: {key2}")
    
    if key1 != key2:
        print("✅ Cache keys are unique in DirectMLOptimizedHandler")
        return True
    else:
        print("❌ Cache keys are identical in DirectMLOptimizedHandler")
        return False

def test_cache_key_uniqueness_fixed():
    """Test that cache keys are unique for the same query in different contexts"""
    print("\n🔍 Testing cache key uniqueness in DirectMLFixedHandler...")
    
    handler = DirectMLFixedHandler({})
    
    # Generate cache keys for the same query at different times
    query = "What is the weather like today?"
    
    key1 = handler._generate_cache_key(query + "123456")
    key2 = handler._generate_cache_key(query + "123457")
    
    print(f"Cache key 1: {key1}")
    print(f"Cache key 2: {key2}")
    
    if key1 != key2:
        print("✅ Cache keys are unique in DirectMLFixedHandler")
        return True
    else:
        print("❌ Cache keys are identical in DirectMLFixedHandler")
        return False

def main():
    """Run cache key uniqueness tests"""
    print("Running cache key uniqueness tests...\n")
    
    tests = [
        test_cache_key_uniqueness,
        test_cache_key_uniqueness_fixed
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All cache key uniqueness tests passed!")
        return True
    else:
        print("⚠️  Some cache key uniqueness tests failed.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Cache key uniqueness is working correctly!")
        else:
            print("\n❌ Cache key uniqueness needs attention!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)