#!/usr/bin/env python
"""
Simple performance check script for OpenManus optimizations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Check if our optimizations are in place
print("🔍 Checking OpenManus Performance Optimizations...")

# Check DirectML handler optimizations
try:
    from app.directml_optimized_handler import (
        MODEL_PRELOAD_STRATEGY, 
        KV_CACHE_ENABLED, 
        KV_CACHE_MAX_ENTRIES
    )
    print("✅ DirectML handler optimizations found")
    print(f"   - Model preload strategy: {MODEL_PRELOAD_STRATEGY}")
    print(f"   - KV Cache enabled: {KV_CACHE_ENABLED}")
    print(f"   - KV Cache max entries: {KV_CACHE_MAX_ENTRIES}")
except ImportError as e:
    print(f"❌ DirectML handler optimizations not found: {e}")

# Check performance monitor
try:
    from app.utils.performance_monitor import performance_monitor
    print("✅ Performance monitoring system found")
except ImportError as e:
    print(f"❌ Performance monitoring system not found: {e}")

# Check web UI optimizations
try:
    with open("web_ui.py", "r") as f:
        content = f.read()
        
        # Check for chat history caching
        if "chat_history_cache" in content:
            print("✅ Chat history caching optimization found")
        else:
            print("❌ Chat history caching optimization not found")
            
        # Check for streamlined processing
        if "len(response) > 50" in content:
            print("✅ Selective response refinement optimization found")
        else:
            print("❌ Selective response refinement optimization not found")
            
        # Check for async history saving
        if "threading.Thread(target=save_chat_history" in content:
            print("✅ Asynchronous history saving optimization found")
        else:
            print("❌ Asynchronous history saving optimization not found")
            
except Exception as e:
    print(f"❌ Error checking web UI optimizations: {e}")

print("\n✨ Performance optimization check completed!")