#!/usr/bin/env python3
"""
TinyLlama inference test for OpenManus.
This script tests basic inference with the TinyLlama model.
"""

import sys
import os
import torch

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_tinyllama_inference():
    """Test TinyLlama inference"""
    print("⚡ Testing TinyLlama inference...")
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_path = "./models/tinyllama"
        print(f"Loading model from: {model_path}")
        
        # Load tokenizer
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        print("✅ Tokenizer loaded")
        
        # Load model with minimal configuration
        print("Loading model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            dtype=torch.float32,  # Use float32 for CPU compatibility
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        print("✅ Model loaded")
        
        # Test simple inference
        print("Testing inference...")
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device)
        
        print("Generating response...")
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:], 
            skip_special_tokens=True
        )
        
        print(f"✅ Inference successful!")
        print(f"Response: {response.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Error during TinyLlama inference: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 TinyLlama Inference Test")
    print("=" * 30)
    
    success = test_tinyllama_inference()
    
    if success:
        print("\n🎉 TinyLlama inference test passed!")
        print("Your local model setup is working correctly.")
    else:
        print("\n⚠️ TinyLlama inference test failed.")
        print("There may be issues with model loading or inference.")

if __name__ == "__main__":
    main()