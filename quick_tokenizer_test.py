#!/usr/bin/env python3
"""
Quick tokenizer test for OpenManus models.
This script tests if we can load the tokenizers quickly.
"""

import sys
import os

# Add the OpenManus directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_tokenizer(model_path, model_name):
    """Test tokenizer loading"""
    print(f"🔍 Testing {model_name} tokenizer...")
    try:
        from transformers import AutoTokenizer
        
        # Load tokenizer only
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        print(f"✅ {model_name} tokenizer loaded successfully!")
        print(f"   Vocabulary size: {len(tokenizer)}")
        return True
    except Exception as e:
        print(f"❌ Error loading {model_name} tokenizer: {e}")
        return False

def main():
    print("🔧 Quick Tokenizer Test")
    print("=" * 30)
    
    # Test TinyLlama tokenizer
    tinyllama_ok = test_tokenizer("./models/tinyllama", "TinyLlama")
    
    print("\n" + "-" * 30)
    
    # Test Phi-3 Mini tokenizer
    phi3_ok = test_tokenizer("./models/phi-3-mini", "Phi-3 Mini")
    
    print("\n" + "=" * 30)
    print("📋 Summary:")
    print(f"   TinyLlama tokenizer: {'✅' if tinyllama_ok else '❌'}")
    print(f"   Phi-3 Mini tokenizer: {'✅' if phi3_ok else '❌'}")
    
    if tinyllama_ok and phi3_ok:
        print("\n🎉 Both tokenizers loaded successfully!")
        print("This indicates that your models are properly downloaded.")
    else:
        print("\n⚠️ Some tokenizers failed to load.")

if __name__ == "__main__":
    main()