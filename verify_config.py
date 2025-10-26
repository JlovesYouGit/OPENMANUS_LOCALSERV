#!/usr/bin/env python
"""
Script to verify that the configuration is correctly set up to use Qwen2-0.5B model
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import config

def verify_configuration():
    """Verify that the configuration is set up to use Qwen2-0.5B model"""
    print("🔍 Verifying configuration...")
    
    # Check if local mode is enabled
    print(f"Local mode enabled: {config.is_local_mode}")
    
    if not config.is_local_mode:
        print("❌ Local mode is not enabled")
        return False
    
    # Check if local model handler is available
    if config.local_model_handler is None:
        print("❌ Local model handler is not available")
        return False
    
    print(f"✅ Local model handler: {type(config.local_model_handler).__name__}")
    
    # Check the configuration
    try:
        # Load the configuration
        config_data = config._load_config()
        
        # Check if LLM configuration exists
        if "llm" not in config_data:
            print("❌ LLM configuration not found")
            return False
            
        llm_config = config_data["llm"]
        print(f"✅ LLM configuration found with keys: {list(llm_config.keys())}")
        
        # Check reasoning model configuration
        if "reasoning" not in llm_config:
            print("❌ Reasoning model configuration not found")
            return False
            
        reasoning_config = llm_config["reasoning"]
        print(f"✅ Reasoning model configuration: {reasoning_config}")
        
        # Check if the model path is set to Qwen2-0.5B
        model_path = reasoning_config.get("model_path", "")
        if "qwen2-0.5b" in model_path.lower():
            print("✅ Reasoning model path is correctly set to Qwen2-0.5B")
            return True
        else:
            print(f"⚠️ Reasoning model path is set to: {model_path}")
            print("⚠️ Expected path to contain 'qwen2-0.5b'")
            return False
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_configuration()
    if success:
        print("\n🎉 Configuration is correctly set up to use Qwen2-0.5B model!")
    else:
        print("\n💥 Configuration verification failed!")
        sys.exit(1)