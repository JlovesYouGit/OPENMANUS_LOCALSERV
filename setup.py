"""
OpenManus Setup Configuration

This file maintains backwards compatibility with older pip versions.
For modern Python packaging, see pyproject.toml
"""
from setuptools import find_packages, setup


def read_readme():
    """Read README file for long description."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A versatile AI agent system that can solve various tasks using multiple tools"


def read_requirements():
    """Read requirements from requirements.txt."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []


setup(
    name="openmanus",
    version="0.1.0",
    author="OpenManus Team",
    author_email="mannaandpoem@gmail.com",
    description="A versatile AI agent system that can solve various tasks using multiple tools",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV",
    project_urls={
        "Documentation": "https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/wiki",
        "Source": "https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV",
        "Issues": "https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues",
        "Changelog": "https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/releases",
    },
    packages=find_packages(exclude=["tests", "tests.*", "a2a-samples", "a2a-samples.*", "examples", "examples.*"]),
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-asyncio>=0.25.3",
            "black>=24.0.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
        "test": [
            "pytest>=8.3.5",
            "pytest-asyncio>=0.25.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.5.0",
            "mkdocstrings[python]>=0.24.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "openmanus=main:main",
            "openmanus-web=web_ui:main",
            "openmanus-mcp=run_mcp:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.toml", "*.yaml", "*.yml", "*.json", "*.md"],
    },
    keywords=[
        "ai", "agent", "llm", "automation", "tools", "multi-agent",
        "openai", "assistant", "chatbot", "machine-learning"
    ],
    zip_safe=False,
)
