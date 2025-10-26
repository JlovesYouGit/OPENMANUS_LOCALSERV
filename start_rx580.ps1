# Startup script for OpenManus with RX580 optimizations

Write-Host "========================================"
Write-Host "OpenManus RX580 Startup Script"
Write-Host "========================================"

# Set DirectML environment variables
Write-Host "Setting DirectML environment variables..."
$env:TORCH_DIRECTML_DEVICE = "0"
Write-Host "TORCH_DIRECTML_DEVICE=$env:TORCH_DIRECTML_DEVICE"

# Set performance environment variables
Write-Host "Setting performance optimizations..."
$env:HF_HOME = ".cache\huggingface"
$env:TOKENIZERS_PARALLELISM = "false"
$env:TF_ENABLE_ONEDNN_OPTS = "0"

# Unset deprecated TRANSFORMERS_CACHE variable to avoid warnings
$env:TRANSFORMERS_CACHE = $null

# Display GPU information
Write-Host ""
Write-Host "Checking GPU configuration..."
python -c "import torch_directml; print('Device:', torch_directml.device_name(0)); print('Count:', torch_directml.device_count())"

Write-Host ""
Write-Host "Starting OpenManus..."
Write-Host "========================================"

# Start OpenManus
python start_app.py