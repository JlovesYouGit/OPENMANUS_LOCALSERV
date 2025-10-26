"""
System Optimization Script for OpenManus
This script sets environment variables and optimizations for better performance.
"""

import os
import torch
import psutil

def optimize_system():
    """Apply system-wide optimizations"""
    print("⚡ Applying system optimizations...")
    
    # Set environment variables for better performance
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    os.environ["OMP_NUM_THREADS"] = str(psutil.cpu_count(logical=False) or 4)
    os.environ["MKL_NUM_THREADS"] = str(psutil.cpu_count(logical=False) or 4)
    
    # CPU thread optimization
    if not torch.cuda.is_available():
        optimal_threads = min(psutil.cpu_count(logical=False) or 4, 6)
        torch.set_num_threads(optimal_threads)
        print(f"   CPU threads limited to: {optimal_threads}")
    
    # Memory optimization for low-memory systems
    available_memory_gb = psutil.virtual_memory().available / (1024**3)
    if available_memory_gb < 2:
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
        print(f"   Low memory mode enabled: {available_memory_gb:.2f}GB available")
    
    print("✅ System optimizations applied!")

def create_optimized_env_file():
    """Create a .env file with optimized settings"""
    env_content = """# OpenManus System Optimizations
TOKENIZERS_PARALLELISM=false
TF_ENABLE_ONEDNN_OPTS=0
OMP_NUM_THREADS={cpu_count}
MKL_NUM_THREADS={cpu_count}
""".format(cpu_count=psutil.cpu_count(logical=False) or 4)
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("📝 Created .env file with optimized settings")

if __name__ == "__main__":
    print("🔧 OpenManus System Optimizer")
    print("=" * 40)
    
    optimize_system()
    create_optimized_env_file()
    
    print("\n💡 To use these optimizations:")
    print("   1. Restart your terminal/command prompt")
    print("   2. Run OpenManus as usual")
    print("   3. Enjoy improved performance!")