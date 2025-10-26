#!/usr/bin/env python
"""
Efficient model loading script for RX580 with memory management
"""

import asyncio
import gc
import torch
from pathlib import Path

class ModelLoader:
    def __init__(self):
        self.loaded_models = {}
        self.model_configs = self._load_configs()
    
    def _load_configs(self):
        """Load model configurations optimized for RX580"""
        config_dir = Path("./model_configs")
        configs = {}
        
        for config_file in config_dir.glob("*_rx580_config.json"):
            model_name = config_file.stem.replace("_rx580_config", "")
            with open(config_file, 'r') as f:
                configs[model_name] = json.load(f)
        
        return configs
    
    async def load_model(self, model_name, model_path):
        """Load a model with RX580 optimizations"""
        print(f"📥 Loading {model_name} with RX580 optimizations...")
        
        # Unload other models if memory is constrained
        if len(self.loaded_models) > 0:
            await self._unload_least_recently_used()
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Load with optimized configuration
            config = self.model_configs.get(model_name, {})
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            # Load model with optimizations
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                **config
            )
            
            # Move to appropriate device
            if torch.cuda.is_available():
                model = model.to("cuda")
            elif hasattr(torch, 'directml') and torch.directml.is_available():
                model = model.to(torch.directml.device())
            else:
                model = model.to("cpu")
            
            self.loaded_models[model_name] = {
                "model": model,
                "tokenizer": tokenizer,
                "last_used": asyncio.get_event_loop().time()
            }
            
            print(f"✅ {model_name} loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading {model_name}: {e}")
            return False
    
    async def _unload_least_recently_used(self):
        """Unload the least recently used model to free memory"""
        if not self.loaded_models:
            return
        
        # Find the least recently used model
        lru_model = min(self.loaded_models.items(), 
                       key=lambda x: x[1]["last_used"])
        model_name = lru_model[0]
        
        print(f"🔄 Unloading {model_name} to free memory...")
        await self.unload_model(model_name)
    
    async def unload_model(self, model_name):
        """Unload a model to free memory"""
        if model_name in self.loaded_models:
            model_info = self.loaded_models.pop(model_name)
            del model_info["model"]
            del model_info["tokenizer"]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"⏏️ {model_name} unloaded successfully")
    
    async def get_model(self, model_name):
        """Get a loaded model, loading it if necessary"""
        if model_name in self.loaded_models:
            # Update last used time
            self.loaded_models[model_name]["last_used"] = asyncio.get_event_loop().time()
            return self.loaded_models[model_name]
        
        # Model not loaded, need to load it
        model_path = f"./models/{model_name}"
        if await self.load_model(model_name, model_path):
            return self.loaded_models[model_name]
        
        return None

# Example usage
async def main():
    loader = ModelLoader()
    
    # Load lightweight model first
    await loader.get_model("tinyllama")
    
    # Load reasoning model (this will unload tinyllama if needed)
    await loader.get_model("qwen2-0.5b")
    
    print("✅ Models loaded efficiently with memory management")

if __name__ == "__main__":
    asyncio.run(main())
