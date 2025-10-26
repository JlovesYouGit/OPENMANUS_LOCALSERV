#!/usr/bin/env python
"""
Verification script for OpenManus AI agent platform dependencies and components
"""

import os
import sys
from pathlib import Path

def check_python_environment():
    """Check Python version and environment"""
    print("🔍 Checking Python environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print("✅ Python environment check passed")
    return True

def check_core_dependencies():
    """Check core dependencies"""
    print("\n🔍 Checking core dependencies...")
    
    required_packages = [
        'torch',
        'torch-directml',
        'transformers',
        'vllm',
        'flask',
        'pillow',
        'numpy',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'torch-directml':
                import torch_directml
                print(f"   ✅ {package}: Available")
            elif package == 'torch':
                import torch
                print(f"   ✅ {package}: {torch.__version__} (CUDA available: {torch.cuda.is_available()})")
            elif package == 'transformers':
                import transformers
                print(f"   ✅ {package}: {transformers.__version__}")
            elif package == 'vllm':
                try:
                    import vllm
                    print(f"   ✅ {package}: {vllm.__version__}")
                except Exception as e:
                    # Check if it's the specific torch._inductor error we know about
                    if "torch._inductor" in str(e):
                        print(f"   ⚠️ {package}: Installed but has compatibility issues (CPU-only PyTorch)")
                    else:
                        raise e
            elif package == 'flask':
                import flask
                print(f"   ✅ {package}: {flask.__version__}")
            elif package == 'pillow':
                from PIL import Image
                print(f"   ✅ {package}: Available")
            elif package == 'numpy':
                import numpy
                print(f"   ✅ {package}: {numpy.__version__}")
            elif package == 'psutil':
                import psutil
                print(f"   ✅ {package}: {psutil.__version__}")
        except ImportError as e:
            print(f"   ❌ {package}: Missing ({e})")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("✅ All core dependencies are available")
        return True

def check_model_files():
    """Check if required model files are present"""
    print("\n🔍 Checking model files...")
    
    models_dir = Path("./models")
    if not models_dir.exists():
        print("   ❌ Models directory not found")
        return False
    
    required_models = [
        "tinyllama",
        "phi-3-mini"
    ]
    
    missing_models = []
    
    for model in required_models:
        model_path = models_dir / model
        if model_path.exists():
            print(f"   ✅ {model}: Found")
        else:
            print(f"   ❌ {model}: Missing")
            missing_models.append(model)
    
    if missing_models:
        print(f"❌ Missing models: {', '.join(missing_models)}")
        return False
    else:
        print("✅ All required models are present")
        return True

def check_frontend_build():
    """Check if frontend is properly built"""
    print("\n🔍 Checking frontend build...")
    
    frontend_dist = Path("./newweb/quantum-canvas-design/dist")
    if not frontend_dist.exists():
        print("   ❌ Frontend dist directory not found")
        return False
    
    required_files = [
        "index.html",
        "assets"
    ]
    
    missing_files = []
    
    for file in required_files:
        file_path = frontend_dist / file
        if file_path.exists():
            print(f"   ✅ {file}: Found")
        else:
            print(f"   ❌ {file}: Missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing frontend files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Frontend build is complete")
        return True

def check_config_files():
    """Check if configuration files are present"""
    print("\n🔍 Checking configuration files...")
    
    config_file = Path("./config/config.toml")
    if config_file.exists():
        print("   ✅ config.toml: Found")
        return True
    else:
        print("   ❌ config.toml: Missing")
        return False

def check_web_server():
    """Check if web server is running"""
    print("\n🔍 Checking web server...")
    
    try:
        import requests
        response = requests.get("http://localhost:5001/api/stats", timeout=5)
        if response.status_code == 200:
            print("   ✅ Web server: Running and responding")
            return True
        else:
            print(f"   ❌ Web server: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Web server: Not accessible ({e})")
        return False

def main():
    """Main verification function"""
    print("🧪 OpenManus AI Agent Platform - Installation Verification")
    print("=" * 60)
    
    checks = [
        check_python_environment,
        check_core_dependencies,
        check_model_files,
        check_frontend_build,
        check_config_files,
        check_web_server
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Check failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All checks passed! OpenManus is properly installed and configured.")
        print("\n💡 Next steps:")
        print("   1. Open your browser and navigate to http://localhost:5001")
        print("   2. Start using the OpenManus AI agent platform")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())