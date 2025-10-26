#!/usr/bin/env python3
"""
Quick setup check for OpenManus with local models.
"""

import os

def check_setup():
    """Check if the setup is complete"""
    print("🔍 OpenManus Local Model Setup Check")
    print("=" * 40)
    
    # Check model directories
    models = {
        "TinyLlama": "./models/tinyllama",
        "Phi-3 Mini": "./models/phi-3-mini"
    }
    
    all_good = True
    
    for model_name, model_path in models.items():
        if os.path.exists(model_path):
            print(f"✅ {model_name}: Found")
            # Check key files
            key_files = ["config.json", "tokenizer.json"]
            for kf in key_files:
                if os.path.exists(os.path.join(model_path, kf)):
                    print(f"   ✅ {kf}")
                else:
                    print(f"   ❌ {kf} missing")
                    all_good = False
        else:
            print(f"❌ {model_name}: Not found")
            all_good = False
    
    # Check config
    config_path = "./config/config.toml"
    if os.path.exists(config_path):
        print("✅ Configuration file: Found")
    else:
        print("❌ Configuration file: Not found")
        all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 Setup Complete! OpenManus is ready to use.")
        print("\nRun: python main.py --prompt \"Hello!\"")
    else:
        print("⚠️  Some issues found. Check the output above.")

if __name__ == "__main__":
    check_setup()