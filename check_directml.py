#!/usr/bin/env python
"""
Check DirectML status and GPU memory
"""

try:
    import torch_directml
    print("DirectML Available:", torch_directml.is_available())
    if torch_directml.is_available():
        device = torch_directml.device()
        print("DirectML Device:", device)
        
        # Try to get device properties
        try:
            if hasattr(torch_directml, 'get_device_properties'):
                props = torch_directml.get_device_properties(device)
                print("Device Properties:", props)
                if hasattr(props, 'total_memory'):
                    total_gb = props.total_memory / (1024**3)
                    print(f"Total GPU Memory: {total_gb:.2f} GB")
            else:
                print("Device properties not available")
        except Exception as e:
            print("Error getting device properties:", e)
    else:
        print("DirectML not available")
except ImportError:
    print("DirectML not installed")
except Exception as e:
    print("Error:", e)