#!/usr/bin/env python
"""
Test script to verify model loading
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model_loading():
    """Test loading of both models"""
    print("Testing model loading...")
    
    # Test TinyLlama model
    print("\n1. Testing TinyLlama model...")
    try:
        model_path = "./models/tinyllama"
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}")
            tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            print("✅ TinyLlama model loaded successfully!")
            
            # Test basic inference
            prompt = "Hello, how are you?"
            inputs = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=50, temperature=0.7)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Sample response: {response}")
        else:
            print(f"❌ Model path {model_path} does not exist")
    except Exception as e:
        print(f"❌ Error loading TinyLlama model: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Phi-3 model
    print("\n2. Testing Phi-3 model...")
    try:
        model_path = "./models/phi-3-mini"
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}")
            tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            print("✅ Phi-3 model loaded successfully!")
            
            # Test basic inference
            prompt = "Hello, how are you?"
            inputs = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=50, temperature=0.7)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Sample response: {response}")
        else:
            print(f"❌ Model path {model_path} does not exist")
    except Exception as e:
        print(f"❌ Error loading Phi-3 model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_loading()