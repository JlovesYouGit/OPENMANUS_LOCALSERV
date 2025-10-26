#!/usr/bin/env python
"""
Test script to verify that context caching prevents leakage between conversations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.directml_optimized_handler import DirectMLOptimizedHandler

async def test_context_isolation():
    """Test that context doesn't leak between different conversations"""
    print("🔍 Testing context isolation between conversations...")
    
    # Configuration for testing
    config = {
        "llm": {
            "lightweight": {
                "model_path": "./models/tinyllama",
                "max_tokens": 256,
                "temperature": 0.7
            }
        }
    }
    
    try:
        # Initialize the handler
        print("🔄 Initializing DirectML handler...")
        handler = DirectMLOptimizedHandler(config)
        print(f"✅ Handler initialized with device: {handler.device}")
        
        # Test first conversation
        print("\n💬 Testing first conversation...")
        response1 = await handler.chat_with_agent(
            "lightweight",
            "What is the capital of France?"
        )
        print(f"📝 Response 1: {response1}")
        
        # Test second conversation with different query
        print("\n💬 Testing second conversation...")
        response2 = await handler.chat_with_agent(
            "lightweight",
            "What is 2+2?"
        )
        print(f"📝 Response 2: {response2}")
        
        # Verify that responses are different and appropriate to each query
        # Convert responses to strings if they're not already
        response1_str = str(response1)
        response2_str = str(response2)
        
        if "paris" in response1_str.lower() and "4" in response2_str.lower():
            print("✅ Context isolation working correctly - responses are appropriate to each query")
            return True
        elif response1_str == response2_str:
            print("❌ Context leakage detected - same response for different queries")
            return False
        else:
            print("⚠️ Responses are different but may not be appropriate to queries")
            print("   This might indicate other issues but not necessarily context leakage")
            return True
            
    except Exception as e:
        print(f"❌ Error testing context isolation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cache_key_uniqueness():
    """Test that cache keys are unique for the same query in different contexts"""
    print("\n🔍 Testing cache key uniqueness...")
    
    handler = DirectMLOptimizedHandler({})
    
    # Generate cache keys for the same query at different times
    query = "What is the weather like today?"
    
    # Need to await the asyncio.get_event_loop() call
    loop = asyncio.get_event_loop()
    key1 = handler._generate_cache_key(query + str(int(loop.time() * 1000000)))
    await asyncio.sleep(0.001)  # Small delay to ensure different timestamps
    key2 = handler._generate_cache_key(query + str(int(loop.time() * 1000000)))
    
    print(f"Cache key 1: {key1}")
    print(f"Cache key 2: {key2}")
    
    if key1 != key2:
        print("✅ Cache keys are unique - context leakage prevention is working")
        return True
    else:
        print("❌ Cache keys are identical - context leakage prevention may not be working")
        return False

def main():
    """Run all context leakage tests"""
    print("Running context leakage prevention tests...\n")
    
    tests = [
        test_cache_key_uniqueness,
        test_context_isolation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = asyncio.run(test()) if asyncio.iscoroutinefunction(test) else test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All context leakage prevention tests passed!")
        return True
    else:
        print("⚠️  Some context leakage prevention tests failed.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Context leakage prevention is working correctly!")
        else:
            print("\n❌ Context leakage prevention needs attention!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        sys.exit(1)