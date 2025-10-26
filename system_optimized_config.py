"""
System-Optimized Configuration for OpenManus
This module provides system-specific optimizations based on hardware detection.
"""

import os
import torch
import psutil
import platform

def get_system_info():
    """Get detailed system information for optimization"""
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(logical=False),
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "available_memory_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    
    # Check for AMD GPU (limited support)
    try:
        import subprocess
        result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], 
                              capture_output=True, text=True, timeout=10)
        if "Radeon" in result.stdout:
            info["amd_gpu"] = True
        else:
            info["amd_gpu"] = False
    except:
        info["amd_gpu"] = False
    
    return info

def optimize_for_system():
    """Apply system-specific optimizations"""
    system_info = get_system_info()
    
    # CPU Thread Optimization
    if system_info["cpu_count"]:
        # Limit threads to physical cores to prevent oversubscription
        optimal_threads = system_info["cpu_count"]
        torch.set_num_threads(optimal_threads)
        os.environ["OMP_NUM_THREADS"] = str(optimal_threads)
        os.environ["MKL_NUM_THREADS"] = str(optimal_threads)
        os.environ["NUMEXPR_NUM_THREADS"] = str(optimal_threads)
    
    # Memory Optimization
    if system_info["total_memory_gb"] < 16:
        # Enable memory-efficient settings for lower RAM systems
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
    
    # Set environment variables for better performance
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disable oneDNN for consistent results
    os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Prevent tokenizer parallelism issues
    
    # For AMD systems, ensure we're using CPU
    if system_info["amd_gpu"] and not system_info["cuda_available"]:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU usage
    
    return system_info

def get_model_loading_config():
    """Get optimized model loading configuration based on system specs"""
    system_info = get_system_info()
    
    config = {
        "torch_dtype": torch.float32,  # Use float32 for CPU compatibility
        "low_cpu_mem_usage": True,
        "use_cache": True,
    }
    
    # For systems with limited available memory
    if system_info["available_memory_gb"] < 2:
        config["torch_dtype"] = torch.float32
        config["low_cpu_mem_usage"] = True
        config["use_cache"] = True
    
    return config

if __name__ == "__main__":
    system_info = optimize_for_system()
    print("🔧 System Optimization Report")
    print("=" * 40)
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    print("\n⚡ Applied Optimizations:")
    print(f"   CPU threads limited to: {torch.get_num_threads()}")
    print(f"   Memory optimizations: {'Enabled' if system_info['available_memory_gb'] < 2 else 'Standard'}")
    print(f"   Environment variables set for optimal performance")