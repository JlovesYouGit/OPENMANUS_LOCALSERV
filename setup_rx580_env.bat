@echo off
REM Setup script for RX580 DirectML environment
REM This script sets up the proper environment variables for AMD GPU acceleration

echo ========================================
echo OpenManus RX580 DirectML Setup Script
echo ========================================

echo.
echo Setting up environment variables for AMD RX580 GPU...
echo.

REM Set DirectML device explicitly for AMD GPUs
set TORCH_DIRECTML_DEVICE=0
echo Set TORCH_DIRECTML_DEVICE=0

REM Disable oneDNN optimizations to avoid floating-point variations
set TF_ENABLE_ONEDNN_OPTS=0
echo Set TF_ENABLE_ONEDNN_OPTS=0

REM Disable tokenizers parallelism to avoid conflicts
set TOKENIZERS_PARALLELISM=false
echo Set TOKENIZERS_PARALLELISM=false

echo.
echo Environment variables set successfully!
echo.

echo Starting OpenManus server with RX580 optimizations...
echo.

cd /d N:\Openmanus\OpenManus
python web_ui.py --host 0.0.0.0 --port 5000

echo.
echo Script completed.
pause