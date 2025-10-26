"""
DirectML Fixed Local Model Handler for OpenManus
This module manages local LLM inference with GPU acceleration using DirectML,
specifically fixed for AMD GPUs like RX580 on Windows systems.
"""

import os
import torch
import json
import hashlib
from PIL import Image
import numpy as np

# Try to import DirectML with error handling
try:
    import torch_directml
    DML_AVAILABLE = True
    print("✅ DirectML support available")
except ImportError:
    torch_directml = None
    DML_AVAILABLE = False
    print("⚠️ DirectML not available, falling back to CPU")

from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional
import asyncio
import logging
import gc
import psutil

# Performance monitoring
from app.utils.performance_monitor import start_request_timer, end_request_timer

logger = logging.getLogger(__name__)

# System optimizations
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Context cache directory
CONTEXT_CACHE_DIR = "./context_cache"
os.makedirs(CONTEXT_CACHE_DIR, exist_ok=True)

# Model loading optimization: Only pre-load lightweight model to conserve memory
MODEL_PRELOAD_STRATEGY = "lightweight_only"  # Options: "none", "lightweight_only", "both"

# KV Cache optimization for DirectML - Optimized for RX580 with 8GB VRAM
KV_CACHE_ENABLED = True
KV_CACHE_MAX_ENTRIES = 2000  # Increased from 1000 to better utilize 8GB VRAM

# CRITICAL FIX: Disable BitsAndBytes quantization for DirectML (AMD GPU incompatible)
MODEL_QUANTIZATION_ENABLED = False  # Disabled for DirectML compatibility
MODEL_QUANTIZATION_TYPE = None  # Options: "4bit", "8bit", None

# Hybrid loading strategy optimized for RX580 with 8GB VRAM
HYBRID_LOADING_STRATEGY = "selective_offload"  # Options: "selective_offload", "cpu_gpu_split", "full_gpu"

class DirectMLFixedHandler:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DirectML fixed handler with configuration.
        
        Args:
            config: Configuration dictionary containing model paths and settings
        """
        self.config = config
        self.models = {}
        self.tokenizers = {}
        self.model_loaded = {}  # Track which models are loaded
        self.device = self._get_optimal_device()
        self.context_cache = {}  # In-memory cache for quick access
        self.model_loading_lock = {}  # Track model loading status to prevent concurrent loading
        self.model_ready = {}  # Track if models are fully ready
        
        # CPU optimization
        if self.device == "cpu":
            # Limit threads to prevent oversubscription
            optimal_threads = min(psutil.cpu_count(logical=False) or 4, 6)
            torch.set_num_threads(optimal_threads)
            logger.info(f"CPU optimization: Using {optimal_threads} threads")
        
        logger.info(f"Initializing DirectML Fixed Handler with device: {self.device}")
        
        # Pre-load models based on strategy for faster response times
        self._preload_models()
        
        # Initialize KV cache for DirectML optimization
        self.kv_cache = {} if KV_CACHE_ENABLED else None
        self.kv_cache_size = 0
        
    def _preload_models(self):
        """Pre-load models based on strategy for faster response times"""
        try:
            if MODEL_PRELOAD_STRATEGY == "lightweight_only":
                logger.info("Pre-loading lightweight model (TinyLlama) for faster responses...")
                # Use a background thread to load models without blocking initialization
                import threading
                def load_models_bg():
                    try:
                        asyncio.run(self.load_model_on_demand("tinyllama"))
                        self.model_ready["tinyllama"] = True
                        logger.info("✅ Lightweight model pre-loaded successfully")
                    except Exception as e:
                        logger.error(f"❌ Error pre-loading lightweight model: {e}")
                        self.model_ready["tinyllama"] = False
                
                thread = threading.Thread(target=load_models_bg, daemon=True)
                thread.start()
            elif MODEL_PRELOAD_STRATEGY == "both":
                logger.info("Pre-loading both models for fastest responses...")
                # Use a background thread to load models without blocking initialization
                import threading
                def load_models_bg():
                    try:
                        asyncio.run(self.load_model_on_demand("tinyllama"))
                        self.model_ready["tinyllama"] = True
                        asyncio.run(self.load_model_on_demand("qwen2-0.5b"))  # Updated to use Qwen2-0.5B
                        self.model_ready["qwen2-0.5b"] = True
                        logger.info("✅ Both models pre-loaded successfully")
                    except Exception as e:
                        logger.error(f"❌ Error pre-loading models: {e}")
                        self.model_ready["tinyllama"] = False
                        self.model_ready["qwen2-0.5b"] = False  # Updated to use Qwen2-0.5B
                
                thread = threading.Thread(target=load_models_bg, daemon=True)
                thread.start()
            else:
                logger.info("No model pre-loading strategy configured")
        except Exception as e:
            logger.warning(f"Model pre-loading failed: {e}")
    
    def _get_optimal_device(self):
        """Get the optimal device for inference"""
        # Check for DirectML support
        if DML_AVAILABLE and torch_directml and torch_directml.is_available():
            dml_device = torch_directml.device()
            logger.info(f"DirectML device available: {dml_device}")
            
            # Check available GPU memory for DirectML
            try:
                # Get GPU memory info if possible
                if hasattr(torch_directml, 'get_device_properties'):
                    props = torch_directml.get_device_properties(dml_device)
                    total_memory = props.total_memory
                    # Convert to GB
                    total_memory_gb = total_memory / (1024**3)
                    logger.info(f"DirectML GPU total memory: {total_memory_gb:.2f}GB")
                    
                    # If less than 4GB VRAM, consider CPU fallback
                    if total_memory_gb < 4:
                        logger.warning(f"Low GPU memory ({total_memory_gb:.2f}GB), considering CPU fallback")
                        # For very low memory, use CPU
                        if total_memory_gb < 2:
                            logger.info("Switching to CPU due to very low GPU memory")
                            return "cpu"
            except Exception as e:
                logger.warning(f"Could not get DirectML device properties: {e}")
            
            return dml_device
        elif torch.cuda.is_available():
            logger.info("CUDA device available")
            return "cuda"
        else:
            logger.info("Using CPU for inference")
            return "cpu"
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate a cache key for the given text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _save_context_to_image(self, context_data: Dict[str, Any], cache_key: str) -> Optional[str]:
        """Save context data as a quantized image for efficient storage"""
        try:
            # Convert context data to a numpy array
            # For simplicity, we'll serialize the data and convert to bytes
            serialized = json.dumps(context_data).encode('utf-8')
            
            # Convert to numpy array
            byte_array = np.frombuffer(serialized, dtype=np.uint8)
            
            # Reshape to a 2D array (we'll make it roughly square)
            size = int(np.ceil(np.sqrt(len(byte_array))))
            padded = np.pad(byte_array, (0, size*size - len(byte_array)), mode='constant')
            image_array = padded.reshape((size, size))
            
            # Create image from array
            image = Image.fromarray(image_array, mode='L')  # Grayscale
            
            # Save image
            cache_file = os.path.join(CONTEXT_CACHE_DIR, f"{cache_key}.png")
            image.save(cache_file, format='PNG')
            
            logger.info(f"Saved context to image: {cache_file}")
            return cache_file
        except Exception as e:
            logger.error(f"Error saving context to image: {e}")
            return None
    
    def _load_context_from_image(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load context data from a quantized image"""
        try:
            cache_file = os.path.join(CONTEXT_CACHE_DIR, f"{cache_key}.png")
            if not os.path.exists(cache_file):
                return None
            
            # Load image
            image = Image.open(cache_file)
            image_array = np.array(image)
            
            # Flatten array and remove padding
            flat_array = image_array.flatten()
            # Remove padding (zeros at the end)
            data_bytes = flat_array[flat_array != 0]
            
            # Convert back to string and parse JSON
            serialized = data_bytes.tobytes().decode('utf-8')
            context_data = json.loads(serialized)
            
            logger.info(f"Loaded context from image: {cache_file}")
            return context_data
        except Exception as e:
            logger.error(f"Error loading context from image: {e}")
            return None
    
    async def load_model_on_demand(self, model_name: str) -> bool:
        """
        Load a model on demand with memory optimizations for DirectML.
        """
        # If model is already loaded, return True
        if model_name in self.models and self.model_loaded.get(model_name, False):
            logger.info(f"🔄 {model_name} model already loaded")
            return True
        
        # For memory-constrained environments like RX580, unload other models first
        # This prevents out-of-memory errors when loading multiple large models
        if model_name == "phi3":
            # If we're loading the large Phi-3 model, unload TinyLlama first if it's loaded
            if "tinyllama" in self.models and self.model_loaded.get("tinyllama", False):
                logger.info("Unloading TinyLlama to free memory for Phi-3...")
                self.unload_model("tinyllama")
        elif model_name == "tinyllama":
            # If we're loading TinyLlama and Phi-3 is loaded, consider unloading it
            # Only if we're in a memory-constrained environment
            if "phi3" in self.models and self.model_loaded.get("phi3", False):
                # Check available memory
                try:
                    if hasattr(torch_directml, 'get_device_properties'):
                        dml_device = torch_directml.device()
                        props = torch_directml.get_device_properties(dml_device)
                        total_memory_gb = props.total_memory / (1024**3)
                        # If less than 6GB total memory, unload Phi-3 when loading TinyLlama
                        if total_memory_gb < 6:
                            logger.info("Unloading Phi-3 to free memory for TinyLlama...")
                            self.unload_model("phi3")
                except Exception as e:
                    logger.warning(f"Could not check GPU memory: {e}")
        elif model_name == "qwen2-0.5b":
            # If we're loading Qwen2-0.5B and Phi-3 is loaded, consider unloading it
            # Only if we're in a memory-constrained environment
            if "phi3" in self.models and self.model_loaded.get("phi3", False):
                # Check available memory
                try:
                    if hasattr(torch_directml, 'get_device_properties'):
                        dml_device = torch_directml.device()
                        props = torch_directml.get_device_properties(dml_device)
                        total_memory_gb = props.total_memory / (1024**3)
                        # If less than 6GB total memory, unload Phi-3 when loading Qwen2-0.5B
                        if total_memory_gb < 6:
                            logger.info("Unloading Phi-3 to free memory for Qwen2-0.5B...")
                            self.unload_model("phi3")
                except Exception as e:
                    logger.warning(f"Could not check GPU memory: {e}")
        
        # Check if model is currently being loaded by another thread
        if model_name in self.model_loading_lock and self.model_loading_lock[model_name]:
            # Wait for model to finish loading
            import time
            logger.info(f"⏳ {model_name} model is currently loading, waiting...")
            while model_name in self.model_loading_lock and self.model_loading_lock[model_name]:
                time.sleep(0.1)  # Wait 100ms
            # Check if loading was successful
            if model_name in self.models and self.model_loaded.get(model_name, False):
                logger.info(f"✅ {model_name} model loaded by another thread")
                return True
            else:
                logger.error(f"❌ {model_name} model failed to load in another thread")
                return False
        
        # Mark model as loading
        self.model_loading_lock[model_name] = True
        
        try:
            model_path = self._resolve_model_path(model_name)
            if not model_path:
                raise ValueError(f"Model path not found for {model_name}")
            
            logger.info(f"📥 Loading {model_name} model from: {model_path}")
            
            # Clear memory before loading
            self._cleanup_memory()
            
            # Load tokenizer
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            # Load model with optimizations for DirectML compatibility
            model_kwargs = {
                "local_files_only": True,
                "low_cpu_mem_usage": True,
                "torch_dtype": torch.float32,  # Use float32 for DirectML compatibility
                "use_safetensors": True,
                "attn_implementation": "eager",  # Use eager attention to avoid einsum issues
                "ignore_mismatched_sizes": True,  # For Phi-3 compatibility
            }
            
            # CRITICAL FIX: Disable BitsAndBytes quantization for DirectML (AMD GPU incompatible)
            # DO NOT add bnb_4bit or bnb_8bit parameters here
            
            # Device-specific optimizations
            if DML_AVAILABLE and torch_directml and "dml" in str(self.device):
                # For DirectML, use specific optimizations
                model_kwargs["torch_dtype"] = torch.float32
                model_kwargs["low_cpu_mem_usage"] = True
                # Additional DirectML-specific options
                model_kwargs["trust_remote_code"] = True
                # Add Phi-3 specific workaround for rotary embeddings
                model_kwargs["ignore_mismatched_sizes"] = True
                
                # Check available GPU memory and apply hybrid loading strategy
                try:
                    if hasattr(torch_directml, 'get_device_properties'):
                        dml_device = torch_directml.device()
                        props = torch_directml.get_device_properties(dml_device)
                        total_memory = props.total_memory
                        total_memory_gb = total_memory / (1024**3)
                        
                        logger.info(f"GPU memory available: {total_memory_gb:.2f}GB")
                        
                        # Apply hybrid loading strategy based on available memory
                        # For RX580 (8GB), be more conservative with memory usage
                        if HYBRID_LOADING_STRATEGY == "selective_offload":
                            # Selective offloading - keep smaller layers on GPU, offload larger ones
                            # For 8GB RX580, use selective offloading for Phi-3 but be more aggressive
                            if total_memory_gb < 8:  # Apply to all RX580 cards
                                logger.info("Applying selective offloading strategy for RX580")
                                model_kwargs["device_map"] = "auto"  # Let transformers decide optimal placement
                                # Add memory constraints for safer loading
                                model_kwargs["max_memory"] = {0: "6GB", "cpu": "10GB"}  # Reserve some memory
                        elif HYBRID_LOADING_STRATEGY == "cpu_gpu_split":
                            # Split model between CPU and GPU
                            if total_memory_gb < 6:
                                logger.info("Applying CPU/GPU split strategy for low memory environment")
                                model_kwargs["device_map"] = {
                                    "": "cpu"  # Load everything on CPU for extremely low memory
                                }
                        # For full_gpu strategy, we don't modify device_map and let it load entirely on GPU
                        
                        # Only enable KV cache offloading if we have sufficient GPU memory
                        if total_memory_gb >= 4:
                            logger.info(f"Sufficient GPU memory ({total_memory_gb:.2f}GB) for KV cache offloading")
                        else:
                            logger.warning(f"Insufficient GPU memory ({total_memory_gb:.2f}GB) for KV cache offloading, using CPU fallback")
                            # Fall back to CPU for this model if memory is extremely low
                            if total_memory_gb < 2:
                                self.device = "cpu"
                except Exception as e:
                    logger.warning(f"Could not check GPU memory, defaulting to current device: {e}")
            elif self.device == "cuda":
                # For CUDA, use float16 for better performance
                model_kwargs["torch_dtype"] = torch.float16
            else:
                # For CPU, optimize for memory usage
                model_kwargs["torch_dtype"] = torch.float32
                available_memory_gb = psutil.virtual_memory().available / (1024**3)
                if available_memory_gb < 2:
                    logger.info(f"Low memory mode: {available_memory_gb:.2f}GB available")
                    # Reduce model loading parameters for low memory
                    model_kwargs["low_cpu_mem_usage"] = True
            
            logger.info(f"Loading model with kwargs: {model_kwargs}")
            
            # Try to load model with memory optimization for DirectML
            try:
                self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    **model_kwargs
                )
                
                # CRITICAL FIX: Proper device handling to avoid meta tensor errors
                # Use to_empty() instead of to() when moving from meta device
                if "device_map" not in model_kwargs:
                    # Check if model is on meta device and handle appropriately
                    try:
                        # Try normal device transfer first
                        self.models[model_name] = self.models[model_name].to(self.device)
                    except NotImplementedError as e:
                        if "meta tensor" in str(e):
                            # Handle meta tensor transfer properly
                            logger.info("Handling meta tensor transfer for DirectML compatibility")
                            # Create empty tensors on target device
                            self.models[model_name] = self.models[model_name].to_empty(device=self.device)
                        else:
                            raise e
                
                self.model_loaded[model_name] = True
                self.model_ready[model_name] = True
                logger.info(f"✅ {model_name} model loaded successfully on {self.device}!")
                return True
            except RuntimeError as e:
                if "out of memory" in str(e).lower() or "not enough memory" in str(e).lower():
                    logger.error(f"❌ Memory error loading {model_name} model: {e}")
                    # Try with even more conservative settings
                    logger.info("Trying with more conservative memory settings...")
                    model_kwargs["low_cpu_mem_usage"] = True
                    model_kwargs["torch_dtype"] = torch.float32
                    
                    # Clear memory again
                    self._cleanup_memory()
                    
                    # Try loading again
                    self.models[model_name] = AutoModelForCausalLM.from_pretrained(
                        model_path,
                        **model_kwargs
                    )
                    
                    # Proper device handling for fallback
                    if "device_map" not in model_kwargs:
                        try:
                            self.models[model_name] = self.models[model_name].to(self.device)
                        except NotImplementedError as e:
                            if "meta tensor" in str(e):
                                logger.info("Handling meta tensor transfer for fallback loading")
                                self.models[model_name] = self.models[model_name].to_empty(device=self.device)
                            else:
                                raise e
                    
                    self.model_loaded[model_name] = True
                    self.model_ready[model_name] = True
                    logger.info(f"✅ {model_name} model loaded successfully on {self.device} with conservative settings!")
                    return True
                else:
                    raise e
                
        except Exception as e:
            logger.error(f"❌ Error loading {model_name} model: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.model_loaded[model_name] = False
            self.model_ready[model_name] = False
            return False
        finally:
            # Mark model as no longer loading
            self.model_loading_lock[model_name] = False
    
    def _cleanup_memory(self):
        """Clean up memory before loading models"""
        gc.collect()
        # Only try to clean up CUDA memory if torch is available and imported
        if torch is not None and hasattr(torch, 'cuda') and torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    def _resolve_model_path(self, model_name: str) -> Optional[str]:
        """Resolve the model path based on configuration and conventions."""
        config_[REDACTED] if model_name == "tinyllama" else "reasoning" if model_name == "qwen2-0.5b" else model_name
        model_config = self.config.get("llm", {}).get(config_key, {})
        model_path = model_config.get("model_path")

        if model_path and os.path.exists(model_path):
            return model_path
        
        # Fallback to conventional paths
        if model_name == "tinyllama":
            default_path = "./models/tinyllama"
        elif model_name == "qwen2-0.5b":  # Updated to handle Qwen2-0.5B
            default_path = "./models/qwen2-0.5b"
        else:
            default_path = f"./models/{model_name}"
        
        if os.path.exists(default_path):
            return default_path
            
        logger.warning(f"Could not resolve model path for {model_name}. Checked config key '{config_key}' and default path '{default_path}'.")
        return None
    
    def unload_model(self, model_name: str):
        """Unload a model to free memory"""
        if model_name in self.models:
            del self.models[model_name]
            del self.tokenizers[model_name]
            self.model_loaded[model_name] = False
            self._cleanup_memory()
            logger.info(f"⏏️ Unloaded {model_name} model to free memory")
    
    def cache_context(self, key: str, context_data: Dict[str, Any]):
        """Cache context data with both in-memory and image-based storage"""
        try:
            # Save to in-memory cache
            self.context_cache[key] = context_data
            
            # Save to image-based cache for persistence
            self._save_context_to_image(context_data, key)
            
            logger.info(f"Cached context with key: {key}")
        except Exception as e:
            logger.error(f"Error caching context: {e}")
    
    def get_cached_context(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached context data"""
        try:
            # Check in-memory cache first
            if key in self.context_cache:
                logger.info(f"Retrieved context from memory cache: {key}")
                return self.context_cache[key]
            
            # Check image-based cache
            context_data = self._load_context_from_image(key)
            if context_data:
                # Also save to in-memory cache for faster access next time
                self.context_cache[key] = context_data
                logger.info(f"Retrieved context from image cache: {key}")
                return context_data
            
            return None
        except Exception as e:
            logger.error(f"Error retrieving cached context: {e}")
            return None
    
    async def generate_response(self, model_type: str, messages: List[Dict[str, str]], 
                         max_tokens: int = 100, temperature: float = 0.7) -> str:
        """
        Generate a response using the specified local model.
        
        Args:
            model_type: Type of model to use ("tinyllama" or "phi3")
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        # Start performance monitoring
        start_time = start_request_timer()
        tokens_generated = 0
        try:
            # Load model if not already loaded - wait for it to be ready
            if model_type not in self.models or not self.model_loaded.get(model_type, False):
                logger.info(f"🔄 Loading {model_type} model on demand...")
                # Wait for model to be loaded (with timeout)
                import time
                timeout = 60  # 60 second timeout
                start_wait = time.time()
                
                # Trigger model loading if not already triggered
                if model_type not in self.model_loading_lock or not self.model_loading_lock.get(model_type, False):
                    await self.load_model_on_demand(model_type)
                
                # Wait for model to be ready
                while (model_type not in self.models or not self.model_loaded.get(model_type, False)) and \
                      (time.time() - start_wait) < timeout:
                    time.sleep(0.5)  # Check every 500ms
                    logger.info(f"⏳ Waiting for {model_type} model to load...")
                
                # Check if model loaded successfully
                if model_type not in self.models or not self.model_loaded.get(model_type, False):
                    raise ValueError(f"Failed to load {model_type} model within timeout period")
            
            if model_type not in self.models:
                raise ValueError(f"Model {model_type} could not be loaded")
            
            tokenizer = self.tokenizers[model_type]
            model = self.models[model_type]
            
            return self._generate_response_transformers(model_type, tokenizer, model, messages,
                                                        max_tokens, temperature, start_time, tokens_generated)
        except Exception as e:
            logger.error(f"❌ Error generating response with {model_type}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Traceback: {error_traceback}")
            
            # Record failed performance metrics
            end_request_timer(start_time, 0, model_type, 0, False)
            
            return f"Error generating response with {model_type}: {str(e)}\nTraceback:\n{error_traceback}"     

    def _generate_response_transformers(self, model_type: str, tokenizer, model, messages: List[Dict[str, str]],
                                       max_tokens: int, temperature: float, start_time, tokens_generated) -> str:
        """Generate response using standard transformers with DirectML optimizations"""
        try:
            # Format inputs for transformers
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
            )
            
            # Move to appropriate device
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Log input shapes for debugging
            for k, v in inputs.items():
                logger.info(f"Input {k} shape: {v.shape}")
            
            # Generate with transformers using DirectML-compatible parameters
            with torch.no_grad():
                generate_kwargs = {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "do_sample": True,
                    "pad_token_id": tokenizer.eos_token_id,
                    # DirectML-specific parameters for better compatibility
                    "use_cache": True,  # Enable KV cache for better performance
                    # Add parameters to improve reasoning
                    "top_p": 0.9,  # Nucleus sampling for better diversity
                    "top_k": 50,   # Top-k sampling
                    "repetition_penalty": 1.2,  # Increased penalty for repetition
                    # Avoid parameters that might trigger einsum operations
                }
                
                # Add attention mask if available
                if "attention_mask" in inputs:
                    generate_kwargs["attention_mask"] = inputs["attention_mask"]
                
                # Add input_ids from inputs
                if "input_ids" in inputs:
                    generate_kwargs["input_ids"] = inputs["input_ids"]
                
                outputs = model.generate(**generate_kwargs)
            
            # Decode response
            response_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            tokens_generated = len(response_tokens)
            
            # Record performance metrics
            end_request_timer(start_time, tokens_generated, model_type, 
                            inputs["input_ids"].shape[-1] if "input_ids" in inputs else 0, True)
            
            return response.strip()
        except Exception as e:
            logger.error(f"❌ Error in transformers generation: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Traceback: {error_traceback}")
            # Record failed performance metrics
            end_request_timer(start_time, 0, model_type, 0, False)
            raise
    
    async def chat_with_agent(self, agent_type: str, user_input: str, 
                             context: Optional[str] = None) -> str:
        """
        Chat with a specific agent type.
        
        Args:
            agent_type: Type of agent ("lightweight" or "reasoning")
            user_input: User's message
            context: Additional context for the conversation
            
        Returns:
            Agent's response
        """
        # Map agent types to model types
        model_mapping = {
            "lightweight": "tinyllama",
            "reasoning": "qwen2-0.5b"  # Updated to use Qwen2-0.5B instead of phi3
        }
        
        model_type = model_mapping.get(agent_type)
        if not model_type:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Load model on demand
        await self.load_model_on_demand(model_type)
        
        # Get model configuration - use the agent_type as key, not model_type
        # Increase token limits for better reasoning
        model_config = self.config.get("llm", {}).get(agent_type, {})
        max_tokens = model_config.get("max_tokens", 500)  # Increased from 100 to 500
        temperature = model_config.get("temperature", 0.7)
        
        # Prepare messages with enhanced structure for better reasoning
        messages = []
        
        # Add system instructions for better reasoning
        system_instruction = """
You are OpenManus, an advanced AI assistant with exceptional reasoning capabilities. 
Please follow these guidelines:
1. Think step by step when solving complex problems
2. Analyze tasks carefully before deciding on actions
3. If you need current information, use the web_search tool
4. For coding tasks, use the python_execute tool
5. For file operations, use the str_replace_editor tool
6. Always verify facts that might be time-sensitive
7. Be concise but thorough in your explanations
8. If you're unsure about something, admit it rather than making things up
9. When deciding to use tools, first analyze why they're needed
10. After using tools, integrate the results into your reasoning
11. Respond naturally and conversationally without being overly constrained
12. Feel free to express creativity and personality in your responses

"""
        
        if context:
            # Combine system instruction with provided context
            full_system_content = system_instruction + context
            messages.append({"role": "system", "content": full_system_content})
        else:
            # Use system instruction alone
            messages.append({"role": "system", "content": system_instruction.strip()})
        
        messages.append({"role": "user", "content": user_input})
        
        # Generate a unique cache key that includes timestamp to prevent context leakage
        # This prevents cached responses from previous conversations from being reused
        import time
        unique_suffix = str(int(time.time() * 1000000))  # Microsecond precision
        context_key = self._generate_cache_key(user_input + unique_suffix)
        context_data = {
            "messages": messages,
            "model_type": model_type,
            "agent_type": agent_type,
            "timestamp": str(asyncio.get_event_loop().time()) if asyncio.get_event_loop() else "unknown"
        }
        self.cache_context(context_key, context_data)
        
        # Generate response
        # Use asyncio.to_thread to run the synchronous generate_response in a separate thread
        response = await asyncio.to_thread(
            self.generate_response,
            model_type, messages, max_tokens, temperature
        )
        
        # Optionally unload model to free memory
        # self.unload_model(model_type)
        
        return response
    
    async def coordinate_agents(self, task: str) -> Dict[str, str]:
        """
        Coordinate both agents to work on a task.
        
        Args:
            task: Task description
            
        Returns:
            Dictionary with responses from both agents
        """
        logger.info(f"🤖 Coordinating agents for task: {task}")
        
        # Get lightweight agent's quick response
        lightweight_response = await self.chat_with_agent(
            "lightweight", 
            f"Quickly analyze this task: {task}"
        )
        
        # Get reasoning agent's detailed response
        reasoning_response = await self.chat_with_agent(
            "reasoning",
            f"Provide a detailed analysis of this task: {task}",
            f"Quick analysis from lightweight agent: {lightweight_response}"
        )
        
        return {
            "lightweight_agent": lightweight_response,
            "reasoning_agent": reasoning_response
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        info = {}
        for model_name in self.models.keys():
            info[model_name] = {
                "status": "loaded",
                "device": str(self.device),
                "path": self.config.get("llm", {}).get(model_name, {}).get("model_path", "unknown")
            }
        return info

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        "llm": {
            "lightweight": {
                "model_path": "./models/tinyllama",
                "max_tokens": 1024,
                "temperature": 0.5
            },
            "reasoning": {
                "model_path": "./models/qwen2-0.5b",  # Updated to use Qwen2-0.5B
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
    }
    
    # Initialize and test
    handler = DirectMLFixedHandler(config)
    print("DirectML Fixed Handler initialized!")