"""
DirectML Optimized Local Model Handler for OpenManus
This module manages local LLM inference with GPU acceleration using DirectML.
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
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
import gc
import psutil
import time

# Performance monitoring
from app.utils.performance_monitor import start_request_timer, end_request_timer

logger = logging.getLogger(__name__)

# System optimizations
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Context cache directory
CONTEXT_CACHE_DIR = "./context_cache"
os.makedirs(CONTEXT_CACHE_DIR, exist_ok=True)

# "Load line" logging for conversational markers (con loop)
LOAD_LINE_DIR = "./context_cache/load_lines"
os.makedirs(LOAD_LINE_DIR, exist_ok=True)

# Model loading optimization: Pre-load lightweight model for faster responses
MODEL_PRELOAD_STRATEGY = "lightweight_only"  # Options: "none", "lightweight_only", "both"

# KV Cache optimization for DirectML - Optimized for RX580 with 8GB VRAM
KV_CACHE_ENABLED = True
KV_CACHE_MAX_ENTRIES = 2000  # Increased from 1000 to better utilize 8GB VRAM

# Model quantization settings for memory optimization
MODEL_QUANTIZATION_ENABLED = True
MODEL_QUANTIZATION_TYPE = "4bit"  # Options: "4bit", "8bit", None

# Hybrid loading strategy for memory-constrained environments
HYBRID_LOADING_STRATEGY = "selective_offload"  # Options: "selective_offload", "cpu_gpu_split", "full_gpu"

class DirectMLOptimizedHandler:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DirectML optimized handler with configuration.

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

        logger.info(f"Initializing DirectML Optimized Handler with device: {self.device}")

        # Pre-load models based on strategy for faster response times
        self._preload_models()

        # Initialize KV cache for DirectML optimization
        self.kv_cache = {} if KV_CACHE_ENABLED else None
        self.kv_cache_size = 0

        # Optional "mesh loader" (activation/weight-link interpreter)
        # This is a lightweight instrumentation layer that can attach forward hooks
        # to collect a deterministic activation sequence during generation.
        mesh_cfg = (self.config.get("llm", {}) or {}).get("mesh_loader", {}) or {}
        self.mesh_enabled: bool = bool(mesh_cfg.get("enabled", False))
        self.mesh_step: int = int(mesh_cfg.get("sequence_step", 5))
        self.mesh_rotation_degrees: float = float(mesh_cfg.get("rotation_degrees", 5.0))
        self.mesh_max_events: int = int(mesh_cfg.get("max_events", 2000))
        self._mesh_state: Dict[Tuple[str, int], Dict[str, Any]] = {}

        # Conversational loop (con loop) / load-line marker logging
        self._con_loop_state: Dict[str, Any] = {
            "session_id": str(int(time.time() * 1000000)),
            "task": None,
            "task_category": None,
            "marker_index": 0,
            "sequence": [3, 4, 2, 1],  # reverse sequence requested
            "photonic_seq_id": 0,
        }

        # Dual-sequence spike + A2A-B directional guiding (optional)
        guide_cfg = (self.config.get("llm", {}) or {}).get("a2ab_guiding", {}) or {}
        self.a2ab_enabled: bool = bool(guide_cfg.get("enabled", False))
        self.a2ab_spike_step: int = int(guide_cfg.get("spike_step", 5))
        self.a2ab_max_spikes: int = int(guide_cfg.get("max_spikes", 64))
        self.a2ab_inject_system: bool = bool(guide_cfg.get("inject_system", True))

        # 4-linear lining cube router (optional)
        cube_cfg = (self.config.get("llm", {}) or {}).get("cube_router", {}) or {}
        self.cube_router_enabled: bool = bool(cube_cfg.get("enabled", False))
        self.cube_router_threshold: float = float(cube_cfg.get("threshold", 10.0))
        # Profiles map to generation overrides
        self.cube_profiles: Dict[str, Dict[str, Any]] = cube_cfg.get(
            "profiles",
            {
                "balanced": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "repetition_penalty": 1.2},
                "precise": {"temperature": 0.3, "top_p": 0.85, "top_k": 40, "repetition_penalty": 1.25},
                "creative": {"temperature": 0.95, "top_p": 0.95, "top_k": 80, "repetition_penalty": 1.1},
                "safe": {"temperature": 0.5, "top_p": 0.8, "top_k": 40, "repetition_penalty": 0.1},
            },
        )
        self._active_profile: Optional[str] = None

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
                        asyncio.run(self.load_model_on_demand("phi3"))
                        self.model_ready["phi3"] = True
                        logger.info("✅ Both models pre-loaded successfully")
                    except Exception as e:
                        logger.error(f"❌ Error pre-loading models: {e}")
                        self.model_ready["tinyllama"] = False
                        self.model_ready["phi3"] = False

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

    def _determine_task_category_from_model(self, model_name: str, model_path: Optional[str] = None) -> str:
        """Determine a default task category based on which model is loaded."""
        name = (model_name or "").lower()
        path = (model_path or "").lower()
        # Simple deterministic categorization
        if "phi" in name or "phi" in path or "reason" in name or "reason" in path:
            return "reasoning"
        if "tiny" in name or "llama" in name or "light" in name or "chat" in name:
            return "lightweight"
        return "general"

    def _preset_task_from_model(self, model_name: str, model_path: Optional[str] = None) -> None:
        """Set initial task/category from model initialization sequence."""
        cat = self._determine_task_category_from_model(model_name, model_path)
        self._con_loop_state["task_category"] = cat
        # Only preset task if it isn't already set by user prompt
        if not self._con_loop_state.get("task"):
            self._con_loop_state["task"] = f"preset:{cat}"

    async def load_model_on_demand(self, model_name: str) -> bool:
        """
        Load a model on demand with memory optimizations for DirectML.
        """
        # If model is already loaded, return True
        if model_name in self.models and self.model_loaded.get(model_name, False):
            logger.info(f"🔄 {model_name} model already loaded")
            return True

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

            # Model initializing sequence: preset task category determined by model
            self._preset_task_from_model(model_name, model_path)

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
                "torch_dtype": torch.float32,
                "use_safetensors": True,
                "attn_implementation": "eager",  # Use eager attention to avoid einsum issues
                "ignore_mismatched_sizes": True,  # For Phi-3 compatibility
            }

            # Apply quantization if enabled
            if MODEL_QUANTIZATION_ENABLED and MODEL_QUANTIZATION_TYPE:
                if MODEL_QUANTIZATION_TYPE == "4bit":
                    # 4-bit quantization for maximum memory savings
                    model_kwargs["load_in_4bit"] = True
                    model_kwargs["bnb_4bit_use_double_quant"] = True
                    model_kwargs["bnb_4bit_quant_type"] = "nf4"
                    model_kwargs["bnb_4bit_compute_dtype"] = torch.float32
                elif MODEL_QUANTIZATION_TYPE == "8bit":
                    # 8-bit quantization for balanced performance/memory
                    model_kwargs["load_in_8bit"] = True

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
                        if HYBRID_LOADING_STRATEGY == "selective_offload":
                            # Selective offloading - keep smaller layers on GPU, offload larger ones
                            if total_memory_gb < 6:
                                logger.info("Applying selective offloading strategy for low memory environment")
                                model_kwargs["device_map"] = "auto"  # Let transformers decide optimal placement
                        elif HYBRID_LOADING_STRATEGY == "cpu_gpu_split":
                            # Split model between CPU and GPU
                            if total_memory_gb < 4:
                                logger.info("Applying CPU/GPU split strategy for very low memory environment")
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

                # Move model to device if not already handled by device_map
                if "device_map" not in model_kwargs:
                    self.models[model_name] = self.models[model_name].to(self.device)

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

                    # Move model to device if not already handled by device_map
                    if "device_map" not in model_kwargs:
                        self.models[model_name] = self.models[model_name].to(self.device)

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
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def _resolve_model_path(self, model_name: str) -> Optional[str]:
        """Resolve the model path based on configuration and conventions."""
        # Config keys in this project are "lightweight" and "reasoning"
        config_key = "lightweight" if model_name == "tinyllama" else "reasoning" if model_name == "phi3" else model_name
        model_config = self.config.get("llm", {}).get(config_key, {})
        model_path = model_config.get("model_path")

        if model_path and os.path.exists(model_path):
            return model_path

        # Fallback to conventional paths
        if model_name == "tinyllama":
            default_path = "./models/tinyllama"
        elif model_name == "phi3":
            default_path = "./models/phi-3-mini"
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

    def _determine_task_from_initial_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Determine task label from the initial user prompt (simple deterministic heuristic)."""
        for m in messages:
            if m.get("role") == "user":
                txt = (m.get("content") or "").strip()
                if txt:
                    # First line / up to 120 chars
                    return txt.splitlines()[0][:120]
        return "unknown"

    def _load_line_log_marker(self, marker: Dict[str, Any]) -> None:
        """Append marker to a per-session load-line file."""
        try:
            session_id = self._con_loop_state.get("session_id", "unknown")
            path = os.path.join(LOAD_LINE_DIR, f"load_line_{session_id}.jsonl")
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(marker, ensure_ascii=False) + "\n")
        except Exception:
            # Never break inference due to logging
            return

    def _con_loop_log_messages(self, messages: List[Dict[str, str]], routing_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Log conversational markers via the "load line" using the reverse sequence 3-4-2-1.
        Also advances a photonic sequence id per section pass.

        Returns compact metadata that can be injected into the model context and used for rerouting.
        """
        if not messages:
            return {}

        # Determine task once from the initial prompt
        if not self._con_loop_state.get("task"):
            self._con_loop_state["task"] = self._determine_task_from_initial_prompt(messages)

        seq = self._con_loop_state["sequence"]
        idx = int(self._con_loop_state.get("marker_index", 0))
        lane = seq[idx % len(seq)]
        self._con_loop_state["marker_index"] = idx + 1

        # Photonic section sequencing: advance by lane value to create a deterministic id
        self._con_loop_state["photonic_seq_id"] = int(self._con_loop_state.get("photonic_seq_id", 0)) + int(lane)
        photonic_seq_id = int(self._con_loop_state["photonic_seq_id"])

        # Use the last message as the conversational marker
        last = messages[-1]
        marker = {
            "ts": int(time.time() * 1000),
            "session_id": self._con_loop_state.get("session_id"),
            "task": self._con_loop_state.get("task"),
            "lane": lane,
            "photonic_seq_id": photonic_seq_id,
            "role": last.get("role"),
            "marker_len": len((last.get("content") or "")),
            "routing_hint": routing_hint,
        }
        self._load_line_log_marker(marker)

        # Return metadata for in-process rerouting decisions
        return {
            "con_loop": {
                "task": marker["task"],
                "lane": lane,
                "session_id": marker["session_id"],
                "photonic_seq_id": photonic_seq_id,
            }
        }

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

            # Con loop marker logging before model process (load line 3-4-2-1)
            # Also provides rerouting metadata.
            con_loop_meta = self._con_loop_log_messages(messages, routing_hint=model_type)

            return self._generate_response_transformers(model_type, tokenizer, model, messages,
                                                        max_tokens, temperature, start_time, tokens_generated, con_loop_meta)
        except Exception as e:
            logger.error(f"❌ Error generating response with {model_type}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Traceback: {error_traceback}")

            # Record failed performance metrics
            end_request_timer(start_time, 0, model_type, 0, False)

            return f"Error generating response with {model_type}: {str(e)}\nTraceback:\n{error_traceback}"

    def _cube_compute_point(self, con_loop_meta: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """Compute a deterministic 3D point from user metadata passage sequence."""
        base = (con_loop_meta or {}).get("con_loop", {}) if isinstance(con_loop_meta, dict) else {}
        lane = float(base.get("lane", 0))
        psid = float(base.get("photonic_seq_id", 0))
        # Simple cube embedding
        x = lane
        y = psid % 16.0
        z = (psid // 16.0) % 16.0
        return {"x": x, "y": y, "z": z}

    def _cube_linear_lining(self, p: Dict[str, float]) -> List[Dict[str, Any]]:
        """4 linear linings that strap on top of mesh: axis-aligned rays in a cube."""
        x, y, z = float(p["x"]), float(p["y"]), float(p["z"])
        return [
            {"id": "L0", "from": {"x": x, "y": y, "z": z}, "to": {"x": x + 1.0, "y": y, "z": z}},
            {"id": "L1", "from": {"x": x, "y": y, "z": z}, "to": {"x": x, "y": y + 1.0, "z": z}},
            {"id": "L2", "from": {"x": x, "y": y, "z": z}, "to": {"x": x, "y": y, "z": z + 1.0}},
            {"id": "L3", "from": {"x": x, "y": y, "z": z}, "to": {"x": x + 1.0, "y": y + 1.0, "z": z + 1.0}},
        ]

    def _cube_select_profile(self, p: Dict[str, float], linings: List[Dict[str, Any]]) -> str:
        """Geometric detection -> choose a profile key."""
        # Simple metric: L1 norm from origin + diagonal presence
        x, y, z = float(p["x"]), float(p["y"]), float(p["z"])
        metric = abs(x) + abs(y) + abs(z)
        if metric >= self.cube_router_threshold:
            return "precise"
        # Use lane-derived bias
        if x in (3.0, 4.0):
            return "balanced"
        if x == 2.0:
            return "creative"
        if x == 1.0:
            return "safe"
        return "balanced"

    def _a2ab_compute_spikes(self, input_ids: torch.Tensor) -> List[Dict[str, Any]]:
        """
        Compute a lightweight "spike" representation from the token stream.

        This is intentionally simple and deterministic: it creates two sequences
        (dual sequence loads) derived from positions and token IDs and emits
        a small set of spike events that can be used as a directional guide.
        """
        try:
            if input_ids is None or not isinstance(input_ids, torch.Tensor) or input_ids.numel() == 0:
                return []

            ids = input_ids.detach()
            if ids.is_cuda:
                ids = ids.cpu()
            ids = ids.view(-1).to(torch.int64)

            # Dual sequences: A uses even positions, B uses odd positions
            pos = torch.arange(ids.numel(), dtype=torch.int64)
            a = ids[pos % 2 == 0]
            b = ids[pos % 2 == 1]

            # Create spikes on a coarse stride to limit overhead
            spikes: List[Dict[str, Any]] = []
            stride = max(self.a2ab_spike_step, 1)

            def emit(seq_name: str, t: torch.Tensor):
                if t.numel() == 0:
                    return
                # pick some sample points
                for i in range(0, t.numel(), stride):
                    if len(spikes) >= self.a2ab_max_spikes:
                        return
                    v = int(t[i].item())
                    spikes.append(
                        {
                            "seq": (len(spikes) + 1) * stride,
                            "lane": seq_name,
                            "token_mod": v % 997,  # stable small feature
                        }
                    )

            emit("A", a)
            emit("B", b)
            return spikes
        except Exception:
            return []

    def _a2ab_directional_guide(self, spikes: List[Dict[str, Any]], mesh_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build an A2A-B directional guidance payload from spikes + thought events."""
        # Keep it compact; the goal is a deterministic, non-invasive guide.
        return {
            "a2aB": {
                "spikes": spikes[: self.a2ab_max_spikes],
                "thought_events": mesh_events[: min(len(mesh_events), 64)],
                "policy": {
                    "bidirectional": True,
                    "guiding_algorithm": "dual_sequence_spike_gate_v1",
                },
            }
        }

    def _mesh_make_signature(self, tensor: torch.Tensor) -> Dict[str, Any]:
        """Create a compact, deterministic signature for a tensor (no raw data)."""
        try:
            t = tensor.detach()
            if t.is_cuda:
                t = t.cpu()
            # float() to stabilize across dtypes
            t = t.float()
            # small summary stats
            return {
                "shape": list(t.shape),
                "mean": float(t.mean().item()) if t.numel() else 0.0,
                "std": float(t.std(unbiased=False).item()) if t.numel() else 0.0,
                "min": float(t.min().item()) if t.numel() else 0.0,
                "max": float(t.max().item()) if t.numel() else 0.0,
            }
        except Exception as e:
            return {"error": str(e)}

    def _mesh_attach(self, model_type: str, model) -> None:
        """Attach forward hooks to collect an activation sequence."""
        if not self.mesh_enabled:
            return

        key = (model_type, id(model))
        if key in self._mesh_state and self._mesh_state[key].get("attached"):
            return

        state: Dict[str, Any] = {
            "attached": True,
            "seq": 0,
            "events": [],
            "handles": [],
        }

        # Prefer transformer blocks if present (common naming: model.layers, model.h, transformer.h)
        candidates = []
        for attr_path in ("model.layers", "model.h", "transformer.h", "gpt_neox.layers"):
            obj = model
            ok = True
            for part in attr_path.split("."):
                if not hasattr(obj, part):
                    ok = False
                    break
                obj = getattr(obj, part)
            if ok and isinstance(obj, (torch.nn.ModuleList, list, tuple)):
                candidates = list(obj)
                break

        # Fallback: hook a small number of top-level child modules
        if not candidates:
            candidates = [m for _, m in list(model.named_children())[:32]]

        def make_hook(layer_name: str):
            def hook(_module, _inp, out):
                if len(state["events"]) >= self.mesh_max_events:
                    return
                try:
                    t = out[0] if isinstance(out, (tuple, list)) else out
                    if isinstance(t, torch.Tensor):
                        state["seq"] += self.mesh_step
                        state["events"].append(
                            {
                                "seq": state["seq"],
                                "layer": layer_name,
                                "signature": self._mesh_make_signature(t),
                            }
                        )
                except Exception:
                    # Never allow instrumentation to break inference
                    return

            return hook

        for i, layer in enumerate(candidates):
            if not isinstance(layer, torch.nn.Module):
                continue
            layer_name = f"layer_{i}"
            try:
                handle = layer.register_forward_hook(make_hook(layer_name))
                state["handles"].append(handle)
            except Exception:
                continue

        self._mesh_state[key] = state

    def _mesh_detach(self, model_type: str, model) -> None:
        """Detach hooks and clear handles."""
        key = (model_type, id(model))
        state = self._mesh_state.get(key)
        if not state:
            return
        for h in state.get("handles", []):
            try:
                h.remove()
            except Exception:
                pass
        state["handles"] = []
        state["attached"] = False

    def _mesh_get_events(self, model_type: str, model) -> List[Dict[str, Any]]:
        key = (model_type, id(model))
        state = self._mesh_state.get(key) or {}
        return list(state.get("events", []))

    def _generate_response_transformers(self, model_type: str, tokenizer, model, messages: List[Dict[str, str]],
                                       max_tokens: int, temperature: float, start_time, tokens_generated,
                                       con_loop_meta: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using standard transformers with DirectML optimizations"""
        try:
            # Inject photonic/load-line metadata into the model context BEFORE tokenization
            # ("send to model before conversation is sent via mesh")
            cube_meta: Optional[Dict[str, Any]] = None
            if self.cube_router_enabled:
                p = self._cube_compute_point(con_loop_meta)
                linings = self._cube_linear_lining(p)
                profile = self._cube_select_profile(p, linings)
                self._active_profile = profile
                cube_meta = {
                    "cube_router": {
                        "point": p,
                        "linings": linings,
                        "profile": profile,
                    }
                }

            if con_loop_meta and isinstance(con_loop_meta, dict) and con_loop_meta.get("con_loop"):
                meta_blob = {
                    "photonic_initializers": con_loop_meta.get("con_loop"),
                    "task_category": self._con_loop_state.get("task_category"),
                    "note": "load-line section metadata for rerouting",
                }
                if cube_meta:
                    meta_blob.update(cube_meta)
                meta_msg = {
                    "role": "system",
                    "content": "[PHOTONIC_METADATA] " + json.dumps(meta_blob, ensure_ascii=False),
                }
                # Prepend so it is processed before existing system/user messages
                messages = [meta_msg] + list(messages)

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

            # Dual sequence spikes (must be computed before model process)
            spikes: List[Dict[str, Any]] = []
            if self.a2ab_enabled and "input_ids" in inputs:
                spikes = self._a2ab_compute_spikes(inputs["input_ids"])

            # Log input shapes for debugging
            for k, v in inputs.items():
                logger.info(f"Input {k} shape: {v.shape}")

            # Attach mesh loader (activation sequence) prior to generation
            self._mesh_attach(model_type, model)

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

                # Apply profile overrides selected by cube router
                if self.cube_router_enabled and self._active_profile:
                    overrides = self.cube_profiles.get(self._active_profile, {})
                    for k in ("temperature", "top_p", "top_k", "repetition_penalty"):
                        if k in overrides:
                            generate_kwargs[k] = overrides[k]

                # Add attention mask if available
                if "attention_mask" in inputs:
                    generate_kwargs["attention_mask"] = inputs["attention_mask"]

                outputs = model.generate(**inputs, **generate_kwargs)

            # Capture mesh events for this run (deterministic ordering by hook call)
            mesh_events = self._mesh_get_events(model_type, model)
            if self.mesh_enabled and mesh_events:
                logger.info(f"Mesh loader captured {len(mesh_events)} activation events for {model_type}")

            # A2A-B directional guiding payload (treat mesh events as thought process)
            a2ab_payload: Optional[Dict[str, Any]] = None
            if self.a2ab_enabled:
                a2ab_payload = self._a2ab_directional_guide(spikes, mesh_events)

            # Detach mesh hooks after generation to avoid overhead/leaks
            self._mesh_detach(model_type, model)

            # Decode response
            response_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
            response = tokenizer.decode(response_tokens, skip_special_tokens=True)
            tokens_generated = len(response_tokens)

            # Record performance metrics
            end_request_timer(start_time, tokens_generated, model_type,
                            inputs["input_ids"].shape[-1] if "input_ids" in inputs else 0, True)

            # If enabled, optionally prepend a small interpreter header (non-invasive)
            header: Dict[str, Any] = {}
            if self.mesh_enabled and mesh_events:
                header["mesh_loader"] = {
                    "rotation_degrees": self.mesh_rotation_degrees,
                    "sequence_step": self.mesh_step,
                    "events": mesh_events[: min(len(mesh_events), 64)],
                }

            if self.a2ab_enabled and a2ab_payload:
                header.update(a2ab_payload)

            if con_loop_meta:
                header.update(con_loop_meta)

            if self.cube_router_enabled and self._active_profile:
                header["cube_router"] = {"profile": self._active_profile}

            if header:
                return (json.dumps(header, ensure_ascii=False) + "\n" + response).strip()

            return response.strip()
        except Exception as e:
            # Ensure hooks are detached on error
            try:
                self._mesh_detach(model_type, model)
            except Exception:
                pass
            logger.error(f"❌ Error in transformers generation: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Traceback: {error_traceback}")
            # Record failed performance metrics
            end_request_timer(start_time, 0, model_type, 0, False)
            raise

    async def chat_with_agent(self, agent_type: str, user_input: str,
                             context: Optional[str] = None):
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
            "reasoning": "phi3"
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

    async def coordinate_agents(self, task: str):
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
                "model_path": "./models/phi-3-mini",
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
    }

    # Initialize and test
    handler = DirectMLOptimizedHandler(config)
    print("DirectML Optimized Handler initialized!")
