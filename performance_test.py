#!/usr/bin/env python
"""
Performance test script for OpenManus
This script tests the performance improvements made to the OpenManus AI agent platform.
"""

import time
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.directml_optimized_handler import DirectMLOptimizedHandler
from app.config import config
from app.utils.performance_monitor import get_performance_report

async def run_performance_test():
    """Run performance tests to verify improvements"""
    print("🚀 Starting OpenManus Performance Test")
    print("=" * 50)
    
    # Create handler
    handler = DirectMLOptimizedHandler(config._load_config())
    
    # Test cases with different complexities
    test_cases = [
        ("Simple greeting", "lightweight", "Hello!"),
        ("Short question", "lightweight", "What is the capital of France?"),
        ("Medium question", "reasoning", "Explain quantum computing in simple terms."),
        ("Complex task", "reasoning", "Analyze the impact of climate change on global economies and propose solutions."),
    ]
    
    results = []
    
    for test_name, agent_type, query in test_cases:
        print(f"\n🧪 Testing: {test_name}")
        print(f"   Query: {query}")
        
        start_time = time.time()
        try:
            response = await handler.chat_with_agent(agent_type, query)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_length = len(response)
            
            results.append({
                "test": test_name,
                "agent_type": agent_type,
                "query": query,
                "response_time": response_time,
                "response_length": response_length,
                "success": True,
                "response": response[:100] + "..." if len(response) > 100 else response
            })
            
            print(f"   ✅ Success: {response_time:.3f}s")
            print(f"   Response length: {response_length} characters")
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            results.append({
                "test": test_name,
                "agent_type": agent_type,
                "query": query,
                "response_time": response_time,
                "response_length": 0,
                "success": False,
                "error": str(e)
            })
            
            print(f"   ❌ Failed: {response_time:.3f}s")
            print(f"   Error: {e}")
        
        # Add small delay between tests
        await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        total_response_time = sum(r["response_time"] for r in successful_tests)
        
        print(f"\n⏱️  Timing Metrics:")
        print(f"   Average response time: {avg_response_time:.3f}s")
        print(f"   Total test time: {total_response_time:.3f}s")
        
        # Breakdown by agent type
        lightweight_tests = [r for r in successful_tests if r["agent_type"] == "lightweight"]
        reasoning_tests = [r for r in successful_tests if r["agent_type"] == "reasoning"]
        
        if lightweight_tests:
            avg_lightweight = sum(r["response_time"] for r in lightweight_tests) / len(lightweight_tests)
            print(f"   Average lightweight agent time: {avg_lightweight:.3f}s")
        
        if reasoning_tests:
            avg_reasoning = sum(r["response_time"] for r in reasoning_tests) / len(reasoning_tests)
            print(f"   Average reasoning agent time: {avg_reasoning:.3f}s")
    
    # Get performance report
    print("\n📈 DETAILED PERFORMANCE REPORT:")
    try:
        report = get_performance_report()
        if "message" in report:
            print(f"   {report['message']}")
        else:
            print(f"   Total requests: {report.get('total_requests', 0)}")
            print(f"   Success rate: {report.get('success_rate', 0):.2%}")
            print(f"   Average response time: {report.get('avg_response_time', 0):.3f}s")
            print(f"   Requests per second: {report.get('requests_per_second', 0):.2f}")
            if report.get('total_tokens_generated', 0) > 0:
                print(f"   Tokens per second: {report.get('tokens_per_second', 0):.2f}")
            print(f"   Memory usage: {report.get('avg_memory_usage_mb', 0):.1f} MB")
    except Exception as e:
        print(f"   Error getting performance report: {e}")
    
    print("\n📋 INDIVIDUAL TEST RESULTS:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} {result['test']} ({result['agent_type']}): {result['response_time']:.3f}s")
        if not result["success"]:
            print(f"      Error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("✨ Performance test completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_performance_test())