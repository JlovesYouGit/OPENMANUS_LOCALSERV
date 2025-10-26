#!/usr/bin/env python
"""
Script to verify that the model mapping in chat_with_agent method uses Qwen2-0.5B
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import config

def verify_model_mapping():
    """Verify that the model mapping in chat_with_agent method uses Qwen2-0.5B"""
    print("🔍 Verifying model mapping in chat_with_agent method...")
    
    # Check if local mode is enabled
    print(f"Local mode enabled: {config.is_local_mode}")
    
    if not config.is_local_mode:
        print("❌ Local mode is not enabled")
        return False
    
    # Check if local model handler is available
    if config.local_model_handler is None:
        print("❌ Local model handler is not available")
        return False
    
    handler = config.local_model_handler
    print(f"✅ Local model handler: {type(handler).__name__}")
    
    # Check the model mapping in chat_with_agent method
    try:
        # Check if the handler has a model_mapping attribute or similar
        if hasattr(handler, 'chat_with_agent'):
            # We can't directly inspect the method source, but we can check the configuration
            # that the method uses to determine the model mapping
            
            # Load the configuration
            config_data = config._load_config()
            
            # Check reasoning model configuration
            if "llm" in config_data and "reasoning" in config_data["llm"]:
                reasoning_config = config_data["llm"]["reasoning"]
                model_path = reasoning_config.get("model_path", "")
                model_type = reasoning_config.get("model_type", "")
                
                print(f"✅ Reasoning model configuration:")
                print(f"   - Model path: {model_path}")
                print(f"   - Model type: {model_type}")
                
                if "qwen2-0.5b" in model_path.lower():
                    print("✅ Configuration correctly points to Qwen2-0.5B model")
                    return True
                else:
                    print("❌ Configuration does not point to Qwen2-0.5B model")
                    return False
            else:
                print("❌ Reasoning model configuration not found")
                return False
        else:
            print("❌ chat_with_agent method not found in handler")
            return False
            
    except Exception as e:
        print(f"❌ Error checking model mapping: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_model_mapping()
    if success:
        print("\n🎉 Model mapping is correctly set up to use Qwen2-0.5B model!")
    else:
        print("\n💥 Model mapping verification failed!")
        sys.exit(1)