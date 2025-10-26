#!/usr/bin/env python
"""
Test script to verify DirectML memory optimization fixes
"""

import asyncio
import sys
from pathlib import Path

# Add the OpenManus directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.directml_optimized_handler import DirectMLOptimizedHandler
from app.config import config

async def test_directml_model_loading():
    """Test DirectML model loading with memory optimizations"""
    print("Testing DirectML model loading with memory optimizations...")
    
    try:
        # Create a DirectML handler instance
        handler = DirectMLOptimizedHandler(config._load_config())
        print("✅ DirectML handler created successfully!")
        
        # Test loading the Phi-3 model
        print("\nTesting Phi-3 model loading...")
        success = await handler.load_model_on_demand("phi3")
        
        if success:
            print("✅ Phi-3 model loaded successfully!")
            
            # Test generating a simple response
            print("\nTesting response generation...")
            response = handler.generate_response(
                model_type="phi3",
                messages=[{"role": "user", "content": "What is 2+2?"}],
                max_tokens=50,
                temperature=0.7
            )
            print(f"Response: {response}")
            
            # Clean up
            handler.unload_model("phi3")
            print("✅ Model unloaded successfully!")
            
            return True
        else:
            print("❌ Failed to load Phi-3 model")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_directml_model_loading())