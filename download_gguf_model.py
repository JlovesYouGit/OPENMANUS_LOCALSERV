import os
import requests
from pathlib import Path

def download_gguf_model():
    """
    Download the TinyLlama 1.1B GGUF model (Q4_K_M quantization)
    Size: ~670MB - Perfect for local use under 4GB requirement!
    """
    print("🌟 Downloading TinyLlama 1.1B GGUF model (Q4_K_M quantization)...")
    print("📏 Model size: ~670MB (perfectly fits under your 4GB requirement!)")
    
    # Create models directory
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    
    # Model URL (Q4_K_M quantization - good balance of size and quality)
    model_url = "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    model_path = models_dir / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    
    # Check if model already exists
    if model_path.exists():
        print("✅ Model already downloaded!")
        return str(model_path)
    
    print("📥 Downloading model... This may take a few minutes...")
    
    try:
        # Download with progress
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        print(f"\r📥 Download progress: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ Model downloaded successfully to: {model_path}")
        print("✨ This model is perfect for local use:")
        print("   • Size: ~670MB (well under your 4GB limit)")
        print("   • Runs efficiently on CPU")
        print("   • No GPU required")
        print("   • Low RAM usage")
        return str(model_path)
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("💡 Alternative: You can manually download from:")
        print("   https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
        return None

if __name__ == "__main__":
    model_path = download_gguf_model()
    if model_path:
        print(f"\n🎯 Model ready at: {model_path}")
        print("🚀 You can now use this lightweight model in OpenManus!")