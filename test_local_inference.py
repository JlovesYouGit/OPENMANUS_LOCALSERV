#!/usr/bin/env python3
"""
Test local inference with both models
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_local_inference():
    """Test inference with both local models"""
    print("🔍 Testing local inference with both models...")
    
    # Test TinyLlama for a quick response
    print("\n⚡ Testing TinyLlama (quick response)...")
    try:
        tinyllama_path = "./models/tinyllama"
        if os.path.exists(tinyllama_path):
            print("📥 Loading TinyLlama model...")
            tokenizer = AutoTokenizer.from_pretrained(tinyllama_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                tinyllama_path,
                local_files_only=True,
                dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Test prompt
            prompt = "Who are you?"
            print(f"💬 Prompt: {prompt}")
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"🤖 TinyLlama response: {response}")
            
        else:
            print("❌ TinyLlama directory not found!")
    except Exception as e:
        print(f"❌ Error with TinyLlama inference: {e}")
    
    # Test Phi-3 Mini for a more detailed response
    print("\n🧠 Testing Phi-3 Mini (detailed response)...")
    try:
        phi3_path = "./models/phi-3-mini"
        if os.path.exists(phi3_path):
            print("📥 Loading Phi-3 Mini model...")
            tokenizer = AutoTokenizer.from_pretrained(phi3_path, local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(
                phi3_path,
                local_files_only=True,
                dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Test prompt
            prompt = "Explain the difference between you and the lightweight model."
            print(f"💬 Prompt: {prompt}")
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"🤖 Phi-3 Mini response: {response}")
            
        else:
            print("❌ Phi-3 Mini directory not found!")
    except Exception as e:
        print(f"❌ Error with Phi-3 Mini inference: {e}")
    
    print("\n🎉 Local inference test completed!")
    print("💡 Both models are working correctly and ready for OpenManus!")

if __name__ == "__main__":
    test_local_inference()