@echo off
REM Startup script for OpenManus with RX580 optimizations

echo ========================================
echo OpenManus RX580 Startup Script
echo ========================================

REM Set DirectML environment variables
echo Setting DirectML environment variables...
set TORCH_DIRECTML_DEVICE=0
echo TORCH_DIRECTML_DEVICE=%TORCH_DIRECTML_DEVICE%

REM Set performance environment variables
echo Setting performance optimizations...
set HF_HOME=.cache\huggingface
set TOKENIZERS_PARALLELISM=false
set TF_ENABLE_ONEDNN_OPTS=0

REM Unset deprecated TRANSFORMERS_CACHE variable to avoid warnings
set TRANSFORMERS_CACHE=

REM Display GPU information
echo.
echo Checking GPU configuration...
python -c "import torch_directml; print('Device:', torch_directml.device_name(0)); print('Count:', torch_directml.device_count())"

echo.
echo Starting OpenManus...
echo ========================================

REM Start OpenManus
python start_app.py

pause