#!/usr/bin/env python
"""
Test script to verify RX580 + DirectML setup
"""

import torch
import torch_directml
import time

def test_directml_setup():
    """Test DirectML setup with RX580"""
    print("🔍 Testing DirectML setup for RX580...")
    
    # Check if DirectML is available
    if not torch_directml.is_available():
        print("❌ DirectML is not available")
        return False
    
    print("✅ DirectML is available")
    
    # Check device count and names
    device_count = torch_directml.device_count()
    print(f"📊 Available DirectML devices: {device_count}")
    
    for i in range(device_count):
        device_name = torch_directml.device_name(i)
        print(f"   Device {i}: {device_name}")
    
    # Get the default device
    device = torch_directml.device()
    print(f"🎮 Default DirectML device: {device}")
    
    # Test basic tensor operations
    print("🧪 Testing basic tensor operations...")
    try:
        # Create tensors on DirectML device
        x = torch.randn(1000, 1000).to(device)
        y = torch.randn(1000, 1000).to(device)
        
        # Perform matrix multiplication
        start_time = time.time()
        z = torch.matmul(x, y)
        end_time = time.time()
        
        print(f"✅ Matrix multiplication successful on {device}")
        print(f"⏱️  Operation took {end_time - start_time:.4f} seconds")
        
        # Check result shape
        print(f"📐 Result shape: {z.shape}")
        
    except Exception as e:
        print(f"❌ Error during tensor operations: {e}")
        return False
    
    # Test memory allocation
    print("💾 Testing memory allocation...")
    try:
        # Try to allocate a larger tensor to test memory
        large_tensor = torch.randn(2000, 2000).to(device)
        print(f"✅ Large tensor allocation successful: {large_tensor.shape}")
        del large_tensor
    except Exception as e:
        print(f"⚠️  Large tensor allocation failed: {e}")
    
    print("🎉 DirectML setup test completed successfully!")
    return True

if __name__ == "__main__":
    test_directml_setup()