# 🔧 OpenManus Query Polling Timeout and GPU Memory Allocation Fixes

## 🎯 Issues Addressed

1. **Persistent Query Polling Timeout** - Frontend was experiencing indefinite polling timeouts
2. **GPU Memory Allocation Errors** - "Could not allocate tensor with 201326592 bytes. There is not enough GPU video memory available!"

## 🛠️ Fixes Implemented

### 1. **DirectML Handler GPU Memory Management** (`app/directml_optimized_handler.py`)

- **Enhanced Device Selection**: Added GPU memory checking before selecting DirectML device
- **Memory-Aware Fallback**: Implemented fallback to CPU when GPU VRAM is below 4GB threshold
- **KV Cache Offload Control**: Only enable GPU memory offloading when sufficient VRAM is available
- **Improved Error Handling**: Better handling of out-of-memory errors with graceful fallbacks

### 2. **Query Manager Timeout Handling** (`app/utils/query_manager.py`)

- **Dedicated Timeout Checker**: Added separate thread for periodic timeout checking every 30 seconds
- **Proactive Timeout Detection**: Queries now timeout after 5 minutes instead of hanging indefinitely
- **Error Result Storage**: Timeout errors are stored as results so frontend can retrieve them
- **Improved Worker Loop**: Better error handling and resource cleanup

### 3. **Web UI Endpoint Improvements** (`web_ui.py`)

- **Enhanced Error Reporting**: Better handling of timeout errors in query result endpoint
- **Consistent Response Format**: Unified error response format for timeout and other errors

### 4. **Frontend API Service Optimization** (`newweb/quantum-canvas-design/src/services/api.ts`)

- **Reduced Polling Frequency**: Increased polling interval from 2s to 3s to reduce server load
- **Limited Retries**: Reduced maximum retries from 15 to 10 to prevent indefinite polling
- **Increased Retry Delays**: Longer delays between retry attempts

## 📊 Technical Details

### GPU Memory Detection Logic
```python
# Check available GPU memory for DirectML
if hasattr(torch_directml, 'get_device_properties'):
    props = torch_directml.get_device_properties(dml_device)
    total_memory_gb = props.total_memory / (1024**3)
    
    # Only enable KV cache offloading if we have sufficient GPU memory
    if total_memory_gb >= 4:
        logger.info(f"Sufficient GPU memory ({total_memory_gb:.2f}GB) for KV cache offloading")
    else:
        logger.warning(f"Insufficient GPU memory ({total_memory_gb:.2f}GB), using CPU fallback")
        self.device = "cpu"
```

### Query Timeout Management
```python
def _timeout_checker_loop(self):
    """Loop to check for timed out queries"""
    while self.is_running:
        try:
            # Check for timed out queries every 30 seconds
            timed_out_queries = self.queue.check_timeouts()
            for query_id in timed_out_queries:
                # Store timeout error result
                self.store_query_result(query_id, {
                    "error": "Query processing timed out after 5 minutes"
                })
            time.sleep(30)
        except Exception as e:
            logger.error(f"Error in timeout checker loop: {e}")
            time.sleep(30)
```

## ✅ Benefits

1. **Prevents System Hangs**: Queries now timeout after 5 minutes instead of hanging indefinitely
2. **Better Resource Management**: GPU memory is checked before loading models
3. **Graceful Degradation**: Falls back to CPU when GPU memory is insufficient
4. **Improved User Experience**: Faster error reporting and reduced server load
5. **Robust Error Handling**: Proper handling of out-of-memory conditions

## 🧪 Testing

Run the test script to verify the fixes:
```bash
python test_gpu_memory_fix.py
```

## 📈 Expected Results

- Elimination of persistent "⚠️ Query polling timeout" errors
- Prevention of GPU memory allocation failures
- Improved system stability and responsiveness
- Better resource utilization across different hardware configurations