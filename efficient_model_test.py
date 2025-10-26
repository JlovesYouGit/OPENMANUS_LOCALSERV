#!/usr/bin/env python3
"""
Efficient test script for local models.
This script tests if the local models can be loaded and used efficiently.
"""

import sys
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_tinyllama():
    """Test TinyLlama model"""
    print("⚡ Testing TinyLlama model...")
    try:
        model_path = "./models/tinyllama"
        print(f"Loading model from: {model_path}")
        
        start_time = time.time()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        print(f"✅ Tokenizer loaded in {time.time() - start_time:.2f}s")
        
        # Load model
        model_load_start = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        print(f"✅ Model loaded in {time.time() - model_load_start:.2f}s")
        print(f"Total loading time: {time.time() - start_time:.2f}s")
        
        # Test inference
        inference_start = time.time()
        messages = [{"role": "user", "content": "What is 2+2?"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:], 
            skip_special_tokens=True
        )
        
        print(f"Inference time: {time.time() - inference_start:.2f}s")
        print(f"TinyLlama response: {response.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing TinyLlama: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phi3_mini():
    """Test Phi-3 Mini model"""
    print("\n🧠 Testing Phi-3 Mini model...")
    try:
        model_path = "./models/phi-3-mini"
        print(f"Loading model from: {model_path}")
        
        start_time = time.time()
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        print(f"✅ Tokenizer loaded in {time.time() - start_time:.2f}s")
        
        # Load model
        model_load_start = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        print(f"✅ Model loaded in {time.time() - model_load_start:.2f}s")
        print(f"Total loading time: {time.time() - start_time:.2f}s")
        
        # Test inference
        inference_start = time.time()
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:], 
            skip_special_tokens=True
        )
        
        print(f"Inference time: {time.time() - inference_start:.2f}s")
        print(f"Phi-3 Mini response: {response.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Phi-3 Mini: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Efficient Local Model Test")
    print("=" * 50)
    
    print("Testing TinyLlama first (smaller model)...")
    success1 = test_tinyllama()
    
    if success1:
        print("\n" + "=" * 50)
        print("Testing Phi-3 Mini (larger model)...")
        success2 = test_phi3_mini()
        
        if success1 and success2:
            print("\n🎉 All models are working correctly!")
        else:
            print("\n⚠️ Some models failed to load or respond.")
    else:
        print("\n⚠️ TinyLlama failed to load, skipping Phi-3 Mini test.")