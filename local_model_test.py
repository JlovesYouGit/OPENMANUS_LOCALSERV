import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Set cache directory to local folder
os.environ['HF_HOME'] = './huggingface_cache'

print("🌟 Loading TinyLlama 1.1B model (super lightweight - only ~500MB!)...")
try:
    # Load the ultra-lightweight TinyLlama model
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    print("📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models", token=False)
    
    print("📥 Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        cache_dir="./models",
        token=False,  # Don't use authentication
        dtype=torch.float16,  # Use float16 to save memory
        low_cpu_mem_usage=True
    )
    
    print("✅ Model loaded successfully! Size: ~500MB")
    
    # Test the model
    messages = [
        {"role": "user", "content": "Who are you?"},
    ]
    
    print("💬 Tokenizing input...")
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    
    print("🤖 Generating response...")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=50, temperature=0.7, do_sample=True)
    
    print("📄 Decoding response...")
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
    print("💬 Response:", response)
    
    print("🎉 TinyLlama model is ready for use in OpenManus!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 This might be due to network issues or model access restrictions.")
    print("💡 Let's try an alternative approach with a local GGUF model...")
    
    # Suggest using the GGUF version for even better performance
    print("\n🔧 For even better performance, consider using the GGUF version:")
    print("   - Model size: 483MB to 1.17GB (depending on quantization)")
    print("   - Install: pip install llama-cpp-python")
    print("   - Download: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    print("   - This version runs efficiently on CPU with minimal RAM!")