#!/usr/bin/env python
"""
Simple verification script for DirectML memory optimization fixes
"""

import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def verify_directml_fix():
    """Verify that the DirectML memory optimization fixes are in place"""
    print("Verifying DirectML memory optimization fixes...")
    
    try:
        # Import the handler
        from app.directml_optimized_handler import DirectMLOptimizedHandler
        from app.config import config
        
        # Read the file to check if our fixes are present
        with open("app/directml_optimized_handler.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for key optimizations
        checks = [
            ("8-bit quantization attempt", "load_in_8bit" in content),
            ("Eager attention implementation", "attn_implementation" in content),
            ("Memory cleanup", "_cleanup_memory" in content),
            ("Low CPU memory usage", "low_cpu_mem_usage" in content),
        ]
        
        print("\nDirectML Memory Optimization Checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All DirectML memory optimization fixes are in place!")
            print("The Phi-3 model should now load successfully with reduced memory usage.")
        else:
            print("\n⚠️  Some DirectML memory optimization fixes are missing.")
            print("The model may still encounter memory allocation issues.")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_directml_fix()