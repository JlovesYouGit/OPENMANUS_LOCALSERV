from llama_cpp import Llama
import os

def test_gguf_model():
    """
    Test the downloaded GGUF model
    """
    print("🧪 Testing TinyLlama GGUF model...")
    
    # Check if model exists
    model_path = "./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print("❌ Model not found. Please run download_gguf_model.py first!")
        return
    
    print("✅ Model found! Loading...")
    
    try:
        # Load the model
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context length
            n_threads=4,  # Number of CPU threads
            n_gpu_layers=0,  # Use CPU only (0 GPU layers)
        )
        
        print("✅ Model loaded successfully!")
        
        # Test prompt
        prompt = "Who are you?"
        
        print(f"💬 Testing with prompt: {prompt}")
        
        # Generate response
        output = llm(
            prompt,
            max_tokens=100,
            temperature=0.7,
            stop=["</s>"],
            echo=False
        )
        
        print("🤖 Response:")
        print(output['choices'][0]['text'])
        
        print("🎉 GGUF model test completed successfully!")
        print("✨ This model is perfect for OpenManus:")
        print("   • Lightweight (~670MB)")
        print("   • Fast inference on CPU")
        print("   • No GPU required")
        print("   • Low memory usage")
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")

if __name__ == "__main__":
    test_gguf_model()