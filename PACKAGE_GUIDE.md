# Python Package Distribution Guide

This guide explains how to distribute and publish OpenManus as a Python package.

## Package Structure

OpenManus follows modern Python packaging standards with both `setup.py` (for backwards compatibility) and `pyproject.toml` (recommended for modern tooling).

```
OPENMANUS_LOCALSERV/
├── pyproject.toml          # Modern package configuration
├── setup.py                # Legacy package configuration
├── requirements.txt        # Runtime dependencies
├── README.md              # Package description
├── LICENSE                # MIT License
├── MANIFEST.in            # Additional files to include
├── app/                   # Main package code
│   ├── __init__.py
│   ├── agent/
│   ├── tool/
│   └── ...
└── tests/                 # Test suite
```

## Building the Package

### Method 1: Using build (Recommended)

Install build tools:
```bash
pip install build twine
```

Build the package:
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/openmanus-0.1.0.tar.gz` (source distribution)
- `dist/openmanus-0.1.0-py3-none-any.whl` (wheel distribution)

### Method 2: Using setuptools

```bash
# Source distribution
python setup.py sdist

# Wheel distribution
python setup.py bdist_wheel
```

## Testing the Package Locally

Before publishing, test the package installation:

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from wheel
pip install dist/openmanus-0.1.0-py3-none-any.whl

# Or install in editable mode for development
pip install -e .

# Test the installation
openmanus --help
python -c "import app; print('Import successful!')"
```

## Publishing to PyPI

### Prerequisites

1. **Create PyPI Account**
   - Register at https://pypi.org/account/register/
   - Verify your email address

2. **Create API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create a token with "Entire account" scope
   - Save the token securely

3. **Configure credentials**

   Option A: Using `.pypirc` file:
   ```bash
   # Create/edit ~/.pypirc
   cat > ~/.pypirc << EOF
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-<your-token-here>

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-<your-test-token-here>
   EOF

   chmod 600 ~/.pypirc
   ```

   Option B: Using environment variables:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-<your-token-here>
   ```

### Step 1: Test on TestPyPI (Recommended)

TestPyPI is a separate instance for testing package publishing.

1. **Register on TestPyPI**: https://test.pypi.org/account/register/

2. **Upload to TestPyPI**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

3. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ openmanus
   ```

### Step 2: Publish to PyPI

Once tested successfully:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll see output like:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading openmanus-0.1.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 58.2/58.2 kB
Uploading openmanus-0.1.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 52.1/52.1 kB

View at: https://pypi.org/project/openmanus/0.1.0/
```

## Installing the Published Package

After publishing, users can install with:

```bash
# Install latest version
pip install openmanus

# Install specific version
pip install openmanus==0.1.0

# Install with optional dependencies
pip install openmanus[dev]      # Development tools
pip install openmanus[test]     # Testing tools
pip install openmanus[docs]     # Documentation tools
pip install openmanus[all]      # All optional dependencies
```

## Version Management

### Semantic Versioning

OpenManus follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (1.x.x): Incompatible API changes
- **MINOR** version (x.1.x): Add functionality (backwards-compatible)
- **PATCH** version (x.x.1): Bug fixes (backwards-compatible)

### Updating Version

Update version in multiple places:

1. **pyproject.toml**:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. **setup.py**:
   ```python
   setup(
       version="0.2.0",
       ...
   )
   ```

3. **Create a git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

## Creating a Release

### GitHub Release

1. Go to repository: https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV
2. Click "Releases" → "Draft a new release"
3. Choose tag: v0.1.0
4. Release title: "OpenManus v0.1.0"
5. Description: Summarize changes, features, and fixes
6. Attach distribution files from `dist/`
7. Click "Publish release"

### Automated Releases with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add `PYPI_API_TOKEN` to repository secrets:
1. Settings → Secrets and variables → Actions
2. New repository secret
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI token

## Package Metadata

### README for PyPI

The README.md is displayed on the PyPI project page. Ensure it includes:
- Clear description
- Installation instructions
- Quick start example
- Link to documentation
- License information

### Classifiers

Classifiers help users find your package. Current classifiers:

```python
classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
```

See all classifiers: https://pypi.org/classifiers/

### Keywords

Help with package discovery:

```python
keywords=[
    "ai", "agent", "llm", "automation", "tools",
    "multi-agent", "openai", "assistant", "chatbot"
]
```

## Maintenance

### Updating the Package

1. Make code changes
2. Update version number
3. Update CHANGELOG.md
4. Rebuild package: `python -m build`
5. Upload: `twine upload dist/*`

### Yanking a Release

If a release has critical issues:

```bash
# Yank a release (keeps it available but warns users)
twine upload --repository pypi --skip-existing dist/*
# Then on PyPI web interface: Manage → Options → Yank
```

### Deleting a Release

⚠️ **Warning**: Cannot delete releases from PyPI! You can only yank them.

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning**
3. **Maintain a CHANGELOG**
4. **Tag releases in git**
5. **Include comprehensive README**
6. **Keep dependencies up to date**
7. **Test package installation in clean environment**
8. **Document breaking changes**
9. **Use GitHub Releases for release notes**
10. **Automate with CI/CD when possible**

## Troubleshooting

### Common Issues

**Issue**: `Package name already exists`
```
Solution: Choose a unique package name or use organization prefix
```

**Issue**: `Invalid distribution filename`
```
Solution: Ensure version follows PEP 440 (e.g., 0.1.0, not 0.1.0a)
```

**Issue**: `Upload failed: 403 Forbidden`
```
Solution: Check API token permissions and expiration
```

**Issue**: `File already exists`
```
Solution: Increment version number; cannot overwrite existing versions
```

**Issue**: `README not rendering on PyPI`
```
Solution: Ensure README.md is valid Markdown and specified in setup.py
```

## Resources

- **PyPI**: https://pypi.org/project/openmanus/
- **Python Packaging Guide**: https://packaging.python.org/
- **PEP 517**: https://www.python.org/dev/peps/pep-0517/
- **PEP 518**: https://www.python.org/dev/peps/pep-0518/
- **Twine Documentation**: https://twine.readthedocs.io/

## Support

For packaging issues:
- Check [Python Packaging Guide](https://packaging.python.org/)
- Ask on [Python Packaging Discourse](https://discuss.python.org/c/packaging/)
- Open an issue: https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues

---

**Ready to publish?** Follow the checklist above and start sharing OpenManus with the world! 🚀
