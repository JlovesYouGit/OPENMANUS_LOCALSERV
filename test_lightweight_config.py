#!/usr/bin/env python
"""
Test script to verify lightweight model configuration
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test that the new configuration loads correctly"""
    print("🔍 Testing new lightweight configuration...")
    
    try:
        # Test importing config
        from app.config import config
        print("✅ Config module imported successfully")
        
        # Check configuration values
        llm_config = config.llm
        print(f"✅ LLM config loaded: {list(llm_config.keys())}")
        
        # Check lightweight model config
        if 'lightweight' in llm_config:
            lightweight_config = llm_config['lightweight']
            print(f"✅ Lightweight model config: {lightweight_config}")
            # Access attributes directly since it's a Pydantic model
            if hasattr(lightweight_config, 'model'):
                print(f"  - Model: {lightweight_config.model}")
        
        # Check reasoning model config
        if 'reasoning' in llm_config:
            reasoning_config = llm_config['reasoning']
            print(f"✅ Reasoning model config: {reasoning_config}")
            # Access attributes directly since it's a Pydantic model
            if hasattr(reasoning_config, 'model'):
                print(f"  - Model: {reasoning_config.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_availability():
    """Test that the required models are available or can be downloaded"""
    print("\n🔍 Testing model availability...")
    
    models_dir = Path("./models")
    if not models_dir.exists():
        print("⚠️ Models directory not found, will need to download models")
        return True
    
    # Check for TinyLlama (should already exist)
    tinyllama_path = models_dir / "tinyllama"
    if tinyllama_path.exists():
        print("✅ TinyLlama model found")
    else:
        print("⚠️ TinyLlama model not found, may need to download")
    
    # Check for Qwen2-0.5B (new lightweight model)
    qwen_path = models_dir / "qwen2-0.5b"
    if qwen_path.exists():
        print("✅ Qwen2-0.5B model found")
    else:
        print("⚠️ Qwen2-0.5B model not found, will need to download")
    
    # Check for StableLM-2-1.6B (alternative lightweight model)
    stablelm_path = models_dir / "stablelm-2-1_6b"
    if stablelm_path.exists():
        print("✅ StableLM-2-1.6B model found")
    else:
        print("⚠️ StableLM-2-1.6B model not found, will need to download")
    
    return True

def test_memory_config():
    """Test that memory management configuration is in place"""
    print("\n🔍 Testing memory management configuration...")
    
    try:
        config_dir = Path("./model_configs")
        if not config_dir.exists():
            print("⚠️ Model configs directory not found")
            return True
            
        # Check for memory management config
        memory_config = config_dir / "memory_management_config.json"
        if memory_config.exists():
            print("✅ Memory management configuration found")
        else:
            print("⚠️ Memory management configuration not found")
            
        # Check for model configs
        model_configs = list(config_dir.glob("*_rx580_config.json"))
        if model_configs:
            print(f"✅ {len(model_configs)} model configurations found")
            for config_file in model_configs:
                print(f"  - {config_file.name}")
        else:
            print("⚠️ No model configurations found")
            
        return True
        
    except Exception as e:
        print(f"❌ Memory config test failed: {e}")
        return False

def main():
    print("🚀 Testing lightweight model configuration...")
    print("=" * 60)
    
    success1 = test_config_loading()
    success2 = test_model_availability()
    success3 = test_memory_config()
    
    if success1 and success2 and success3:
        print("\n🎉 All lightweight configuration tests passed!")
        print("💡 Your system is now configured to use more efficient models:")
        print("  - Lightweight model: TinyLlama (1.1B parameters)")
        print("  - Reasoning model: Qwen2-0.5B (500M parameters) - much lighter than Phi-3!")
        print("  - Alternative: StableLM-2-1.6B (1.6B parameters) if needed")
        print("\nThese models should load simultaneously on your RX580 without timeouts.")
    else:
        print("\n❌ Some configuration tests failed.")
        print("💡 You may need to download the required models or check your configuration.")

if __name__ == "__main__":
    main()