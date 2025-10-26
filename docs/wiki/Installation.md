# Installation Guide

This guide provides detailed instructions for installing OpenManus on various platforms.

## System Requirements

### Minimum Requirements
- **Python**: 3.12 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for installation
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Recommended for GPU Acceleration
- **GPU**: DirectML-compatible GPU (AMD/NVIDIA) for Windows
- **VRAM**: 4GB+ for local model inference
- **RAM**: 16GB+ for optimal performance

## Installation Methods

We provide two installation methods. **Method 2 (using uv)** is recommended for faster installation and better dependency management.

### Method 1: Using conda

**Step 1: Install Conda**

If you don't have Conda installed, download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).

**Step 2: Create a New Environment**

```bash
conda create -n open_manus python=3.12
conda activate open_manus
```

**Step 3: Clone the Repository**

```bash
git clone https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV.git
cd OPENMANUS_LOCALSERV
```

**Step 4: Install Dependencies**

```bash
pip install -r requirements.txt
```

### Method 2: Using uv (Recommended) ⭐

**Step 1: Install uv**

uv is a fast Python package installer and resolver written in Rust.

**On Unix/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Clone the Repository**

```bash
git clone https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV.git
cd OPENMANUS_LOCALSERV
```

**Step 3: Create Virtual Environment**

```bash
uv venv --python 3.12
```

**Step 4: Activate Virtual Environment**

**On Unix/macOS:**
```bash
source .venv/bin/activate
```

**On Windows:**
```cmd
.venv\Scripts\activate
```

**Step 5: Install Dependencies**

```bash
uv pip install -r requirements.txt
```

## Optional Components

### Browser Automation (Playwright)

For browser automation features, install Playwright:

```bash
playwright install
```

This will download the necessary browser binaries (Chromium, Firefox, WebKit).

### GPU Acceleration (DirectML)

For Windows users with AMD GPUs, DirectML acceleration is automatically configured when available. See [DirectML Setup](DirectML-Setup) for detailed configuration.

## Package Installation

To install OpenManus as a Python package:

```bash
pip install -e .
```

This allows you to use the `openmanus` command from anywhere:

```bash
openmanus
```

## Verification

Verify your installation:

```bash
python verify_installation.py
```

This script checks:
- ✅ Python version compatibility
- ✅ Required dependencies
- ✅ Configuration files
- ✅ Model availability
- ✅ GPU acceleration status

## Docker Installation (Alternative)

If you prefer containerized deployment:

```bash
# Build the Docker image
docker build -t openmanus .

# Run the container
docker run -p 5000:5000 -v $(pwd)/config:/app/config openmanus
```

## Troubleshooting

### Common Issues

**Issue: Python version mismatch**
```
Solution: Ensure Python 3.12+ is installed
python --version
```

**Issue: Dependency conflicts**
```
Solution: Use a clean virtual environment
conda create -n open_manus_clean python=3.12
```

**Issue: Playwright installation fails**
```
Solution: Install system dependencies
# Ubuntu/Debian
sudo apt-get install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1
```

**Issue: GPU not detected**
```
Solution: Check DirectML installation
python check_directml.py
```

### Getting Help

- Check the [Troubleshooting Guide](Troubleshooting)
- Search [GitHub Issues](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
- Ask in [Discussions](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/discussions)

## Next Steps

- [Configuration](Configuration) - Set up API keys and preferences
- [Quick Start](Quick-Start) - Run your first task
- [Web UI Guide](Web-UI-Guide) - Use the web interface

---

**Updated**: 2024-01-26 | [Report Issues](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
