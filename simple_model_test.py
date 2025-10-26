#!/usr/bin/env python
"""
Simple test script to verify model paths
"""

import os

def test_model_paths():
    """Test if model paths exist"""
    print("Testing model paths...")
    
    # Test TinyLlama model path
    print("\n1. Testing TinyLlama model path...")
    model_path = "./models/tinyllama"
    if os.path.exists(model_path):
        print(f"✅ TinyLlama model path exists: {model_path}")
        files = os.listdir(model_path)
        print(f"Files in directory: {files[:5]}...")  # Show first 5 files
    else:
        print(f"❌ TinyLlama model path does not exist: {model_path}")
    
    # Test Phi-3 model path
    print("\n2. Testing Phi-3 model path...")
    model_path = "./models/phi-3-mini"
    if os.path.exists(model_path):
        print(f"✅ Phi-3 model path exists: {model_path}")
        files = os.listdir(model_path)
        print(f"Files in directory: {files[:5]}...")  # Show first 5 files
    else:
        print(f"❌ Phi-3 model path does not exist: {model_path}")

if __name__ == "__main__":
    test_model_paths()
