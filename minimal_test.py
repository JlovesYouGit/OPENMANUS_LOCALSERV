#!/usr/bin/env python
"""
Minimal test to identify where the hang occurs
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Step 1: Starting minimal test...")

try:
    print("Step 2: Importing basic modules...")
    import torch
    print("✅ PyTorch imported")
except Exception as e:
    print(f"❌ PyTorch import failed: {e}")

try:
    print("Step 3: Importing torch_directml...")
    import torch_directml
    print("✅ torch_directml imported")
    print(f"DirectML available: {torch_directml.is_available()}")
    if torch_directml.is_available():
        print(f"DirectML device: {torch_directml.device()}")
except Exception as e:
    print(f"❌ torch_directml import failed: {e}")

try:
    print("Step 4: Importing transformers...")
    from transformers import AutoTokenizer, AutoModelForCausalLM
    print("✅ transformers imported")
except Exception as e:
    print(f"❌ transformers import failed: {e}")

print("Step 5: Test completed!")