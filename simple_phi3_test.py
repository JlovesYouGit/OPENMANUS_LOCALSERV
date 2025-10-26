#!/usr/bin/env python
"""
Simple test to verify Phi-3 model files exist and can be loaded
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_phi3_files():
    """Test if Phi-3 model files exist"""
    model_path = "./models/phi-3-mini"
    
    print("🔍 Checking Phi-3 model files...")
    
    if not os.path.exists(model_path):
        print(f"❌ Model path does not exist: {model_path}")
        return False
    
    print(f"✅ Model path exists: {model_path}")
    
    # Check for key files
    key_files = [
        "config.json",
        "model-00001-of-00002.safetensors",
        "model-00002-of-00002.safetensors",
        "tokenizer.json"
    ]
    
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_name}: {file_size / (1024**2):.2f} MB")
        else:
            print(f"❌ {file_name}: Not found")
            return False
    
    # Calculate total size
    total_size = 0
    for file_name in key_files:
        file_path = os.path.join(model_path, file_name)
        if os.path.exists(file_path):
            total_size += os.path.getsize(file_path)
    
    print(f"📊 Total model size: {total_size / (1024**3):.2f} GB")
    
    if total_size > 8 * (1024**3):
        print("⚠️  Model is larger than 8GB VRAM, may need optimizations")
    else:
        print("✅ Model should fit in 8GB VRAM with optimizations")
    
    return True

if __name__ == "__main__":
    test_phi3_files()