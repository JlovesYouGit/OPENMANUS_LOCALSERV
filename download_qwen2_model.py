#!/usr/bin/env python
"""
Simple script to download the Qwen2-0.5B model
"""

import os
import sys
from pathlib import Path

def download_qwen2_0_5b():
    """Download Qwen2-0.5B model"""
    print("📥 Downloading Qwen2-0.5B model...")
    
    try:
        # Create models directory if it doesn't exist
        models_dir = Path("./models")
        models_dir.mkdir(exist_ok=True)
        
        # Check if model already exists
        qwen_path = models_dir / "qwen2-0.5b"
        if qwen_path.exists():
            print("✅ Qwen2-0.5B model already exists")
            return True
        
        # Use huggingface_hub to download Qwen2-0.5B
        try:
            from huggingface_hub import snapshot_download
            print("Starting download of Qwen2-0.5B from Hugging Face...")
            snapshot_download(
                repo_id="Qwen/Qwen2-0.5B-Instruct",
                local_dir="./models/qwen2-0.5b",
                local_dir_use_symlinks=False
            )
            print("✅ Qwen2-0.5B downloaded successfully using huggingface_hub")
            return True
        except Exception as e:
            print(f"❌ Failed to download Qwen2-0.5B: {e}")
            
            # Provide manual download instructions
            print("\n❌ Automatic download failed. Please download manually:")
            print("   1. Visit: https://huggingface.co/Qwen/Qwen2-0.5B-Instruct")
            print("   2. Download all files to: ./models/qwen2-0.5b/")
            print("   3. Or run: git clone https://huggingface.co/Qwen/Qwen2-0.5B-Instruct ./models/qwen2-0.5b")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading Qwen2-0.5B: {e}")
        return False

def main():
    print("🚀 Starting Qwen2-0.5B download...")
    print("=" * 50)
    
    success = download_qwen2_0_5b()
    
    if success:
        print("\n🎉 Qwen2-0.5B download completed!")
        print("💡 Your system is now ready to use this lightweight model.")
        print("   - Model size: ~500M parameters (much lighter than Phi-3)")
        print("   - Should load quickly on your RX580")
        print("   - Optimized for simultaneous loading with TinyLlama")
    else:
        print("\n❌ Qwen2-0.5B download failed.")
        print("💡 You may need to check your internet connection or try again later.")
        print("💡 Alternative: Download manually from https://huggingface.co/Qwen/Qwen2-0.5B-Instruct")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)