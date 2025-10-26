#!/usr/bin/env python3
"""
Model verification script for OpenManus.
This script verifies that the local models are properly downloaded and can be loaded.
"""

import sys
import os
import time

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def verify_model_files(model_path, model_name):
    """Verify that model files exist"""
    print(f"🔍 Verifying {model_name} files...")
    
    if not os.path.exists(model_path):
        print(f"❌ Model directory not found: {model_path}")
        return False
    
    required_files = ["config.json", "tokenizer_config.json"]
    optional_files = ["model.safetensors", "pytorch_model.bin"]
    
    for file in required_files:
        file_path = os.path.join(model_path, file)
        if not os.path.exists(file_path):
            print(f"❌ Required file missing: {file_path}")
            return False
        print(f"✅ Found required file: {file}")
    
    # Check for at least one model file
    model_file_found = False
    for file in optional_files:
        file_path = os.path.join(model_path, file)
        if os.path.exists(file_path):
            print(f"✅ Found model file: {file}")
            model_file_found = True
            break
    
    if not model_file_found:
        print(f"❌ No model files found in {model_path}")
        return False
    
    print(f"✅ {model_name} files verified successfully!")
    return True

def test_tokenizer_loading(model_path, model_name):
    """Test tokenizer loading"""
    print(f"\n🔍 Testing {model_name} tokenizer loading...")
    try:
        start_time = time.time()
        from transformers import AutoTokenizer
        
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        print(f"✅ {model_name} tokenizer loaded successfully in {time.time() - start_time:.2f}s")
        print(f"   Vocabulary size: {len(tokenizer)}")
        return True
    except Exception as e:
        print(f"❌ Error loading {model_name} tokenizer: {e}")
        return False

def main():
    print("🔧 OpenManus Model Verification")
    print("=" * 50)
    
    # Verify TinyLlama
    tinyllama_path = "./models/tinyllama"
    tinyllama_ok = verify_model_files(tinyllama_path, "TinyLlama")
    
    if tinyllama_ok:
        tinyllama_tokenizer_ok = test_tokenizer_loading(tinyllama_path, "TinyLlama")
    else:
        tinyllama_tokenizer_ok = False
    
    print("\n" + "=" * 50)
    
    # Verify Phi-3 Mini
    phi3_path = "./models/phi-3-mini"
    phi3_ok = verify_model_files(phi3_path, "Phi-3 Mini")
    
    if phi3_ok:
        phi3_tokenizer_ok = test_tokenizer_loading(phi3_path, "Phi-3 Mini")
    else:
        phi3_tokenizer_ok = False
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   TinyLlama files: {'✅' if tinyllama_ok else '❌'}")
    print(f"   TinyLlama tokenizer: {'✅' if tinyllama_tokenizer_ok else '❌'}")
    print(f"   Phi-3 Mini files: {'✅' if phi3_ok else '❌'}")
    print(f"   Phi-3 Mini tokenizer: {'✅' if phi3_tokenizer_ok else '❌'}")
    
    if tinyllama_ok and tinyllama_tokenizer_ok and phi3_ok and phi3_tokenizer_ok:
        print("\n🎉 All models are properly downloaded and can be loaded!")
        return True
    else:
        print("\n⚠️ Some issues were found with the models.")
        return False

if __name__ == "__main__":
    main()