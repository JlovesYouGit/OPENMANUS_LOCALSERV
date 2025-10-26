# Configuration Guide

OpenManus is highly configurable to suit your needs. This guide covers all configuration options.

## Configuration File

OpenManus uses a TOML configuration file located at `config/config.toml`.

### Initial Setup

1. **Copy the example configuration:**
   ```bash
   cp config/config.example.toml config/config.toml
   ```

2. **Edit the configuration:**
   ```bash
   # Use your favorite editor
   nano config/config.toml
   # or
   vim config/config.toml
   ```

## LLM Configuration

### Basic LLM Settings

```toml
[llm]
model = "gpt-4o"                          # Model name
base_url = "https://api.openai.com/v1"   # API endpoint
api_key = "sk-..."                        # Your API key
max_tokens = 4096                         # Maximum tokens per request
temperature = 0.0                         # Randomness (0.0 = deterministic)
timeout = 60                              # Request timeout in seconds
```

### Supported Models

**OpenAI Models:**
- `gpt-4o` - Latest and most capable
- `gpt-4-turbo` - Fast and efficient
- `gpt-3.5-turbo` - Cost-effective option

**Other Providers:**
OpenManus supports OpenAI-compatible APIs:

```toml
# Azure OpenAI
[llm]
model = "gpt-4"
base_url = "https://your-resource.openai.azure.com/"
api_key = "your-azure-key"

# Anthropic Claude (via compatible proxy)
[llm]
model = "claude-3-opus"
base_url = "https://api.anthropic.com/v1"
api_key = "your-anthropic-key"

# Local LLM (via llama.cpp, ollama, etc.)
[llm]
model = "llama-2-7b"
base_url = "http://localhost:8000/v1"
api_key = "not-required"
```

### Vision Model Configuration

For tasks requiring image understanding:

```toml
[llm.vision]
model = "gpt-4o"                        # Vision-capable model
base_url = "https://api.openai.com/v1"
api_key = "sk-..."
max_tokens = 4096
temperature = 0.0
```

## Performance Configuration

### Query Management

```toml
[performance]
# Maximum concurrent queries
max_concurrent_queries = 5

# Enable query compression
enable_compression = true
compression_level = "high"  # Options: low, medium, high

# Message queue settings
queue_size = 100
priority_enabled = true

# Timeout settings
query_timeout = 120         # seconds
stream_timeout = 30         # seconds
```

### Caching

```toml
[cache]
# Enable response caching
enabled = true

# Cache directory
cache_dir = "context_cache"

# Cache TTL (time to live) in seconds
ttl = 3600

# Maximum cache size (MB)
max_size = 1024

# Cache compression
compress = true
```

### GPU Acceleration

```toml
[gpu]
# Enable GPU acceleration
enabled = true

# Device selection
device = "directml"  # Options: cuda, directml, mps, cpu

# Memory settings (MB)
max_memory = 4096
kv_cache_size = 2048

# Optimization level
optimization_level = "high"  # Options: low, medium, high
```

## Tool Configuration

### Browser Automation

```toml
[tools.browser]
# Enable browser automation
enabled = true

# Browser type
browser = "chromium"  # Options: chromium, firefox, webkit

# Headless mode
headless = true

# Timeout settings
page_timeout = 30000      # milliseconds
navigation_timeout = 30000

# Screenshot settings
screenshot_quality = 80
screenshot_format = "png"  # Options: png, jpeg
```

### Web Search

```toml
[tools.search]
# Enable web search
enabled = true

# Search providers (in priority order)
providers = ["duckduckgo", "google", "bing"]

# Number of results
max_results = 5

# Search timeout
timeout = 10  # seconds

# Filter settings
safe_search = true
language = "en"
region = "us"
```

### Code Execution

```toml
[tools.code]
# Enable code execution (⚠️ Security risk!)
enabled = false

# Allowed languages
allowed_languages = ["python", "javascript"]

# Timeout for code execution
timeout = 30  # seconds

# Resource limits
max_memory = 512  # MB
max_cpu_time = 10  # seconds

# Sandboxing
use_docker = true
docker_image = "python:3.12-slim"
```

### Data Analysis

```toml
[tools.data_analysis]
# Enable data analysis agent
enabled = false

# Plotting backend
backend = "matplotlib"  # Options: matplotlib, plotly

# Output directory
output_dir = "workspace"

# Maximum file size (MB)
max_file_size = 100
```

## Multi-Agent Configuration

### Run Flow Settings

```toml
[runflow]
# Enable multi-agent system
enabled = false

# Enable data analysis agent
use_data_analysis_agent = false

# Agent coordination
max_agents = 5
coordination_strategy = "sequential"  # Options: sequential, parallel

# Communication settings
inter_agent_timeout = 60  # seconds
```

### Agent-Specific Settings

```toml
[agents.data_analysis]
enabled = false
model = "gpt-4o"
tools = ["pandas", "matplotlib", "seaborn"]
max_iterations = 10

[agents.web_automation]
enabled = true
model = "gpt-4o"
tools = ["playwright", "selenium"]
max_iterations = 20
```

## Security Configuration

### API Key Management

```toml
[security]
# API key validation
validate_keys = true

# Rate limiting
rate_limit_enabled = true
requests_per_minute = 60

# Automatic redaction
auto_redact = true
redact_patterns = ["api[_-]?key", "password", "secret", "token"]
```

### Data Protection

```toml
[security.data]
# Encrypt sensitive data
encrypt_storage = true

# Automatic cleanup
auto_cleanup = true
cleanup_interval = 3600  # seconds

# Backup sensitive files
backup_enabled = true
backup_dir = ".sensitive_backup"
```

## Logging Configuration

```toml
[logging]
# Log level
level = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log file
file = "logs/openmanus.log"

# Log rotation
rotation = "100 MB"
retention = "1 week"

# Log format
format = "{time} | {level} | {message}"

# Console output
console_enabled = true
console_colorize = true
```

## Web UI Configuration

```toml
[webui]
# Server settings
host = "0.0.0.0"
port = 5000
debug = false

# CORS settings
cors_enabled = true
allowed_origins = ["http://localhost:3000"]

# Session settings
session_timeout = 3600  # seconds
max_message_length = 10000  # characters

# Theme
theme = "dark"  # Options: light, dark, auto
```

## Advanced Configuration

### Model-Specific Settings

```toml
[models.gpt4o]
temperature = 0.0
top_p = 1.0
frequency_penalty = 0.0
presence_penalty = 0.0
max_tokens = 4096

[models.gpt35turbo]
temperature = 0.3
top_p = 0.9
max_tokens = 2048
```

### Custom Tool Configuration

```toml
[custom_tools.my_tool]
enabled = true
endpoint = "https://api.example.com"
api_key_env = "MY_TOOL_API_KEY"
timeout = 30
retry_attempts = 3
```

## Environment Variables

You can override configuration with environment variables:

```bash
# LLM configuration
export OPENMANUS_LLM_MODEL="gpt-4o"
export OPENMANUS_LLM_API_KEY="sk-..."
export OPENMANUS_LLM_BASE_URL="https://api.openai.com/v1"

# Performance settings
export OPENMANUS_MAX_CONCURRENT_QUERIES=5
export OPENMANUS_ENABLE_COMPRESSION=true

# Tool settings
export OPENMANUS_BROWSER_ENABLED=true
export OPENMANUS_SEARCH_ENABLED=true
```

Format: `OPENMANUS_<SECTION>_<KEY>` (uppercase, underscores)

## Configuration Validation

Verify your configuration:

```bash
python verify_config.py
```

This checks:
- ✅ File syntax validity
- ✅ Required fields present
- ✅ API key format
- ✅ Value ranges
- ✅ File permissions

## Configuration Templates

### Minimal Configuration

For basic usage:

```toml
[llm]
model = "gpt-3.5-turbo"
api_key = "sk-..."

[tools.browser]
enabled = false

[tools.search]
enabled = true
```

### Production Configuration

For deployment:

```toml
[llm]
model = "gpt-4o"
api_key = "sk-..."
timeout = 120

[performance]
max_concurrent_queries = 10
enable_compression = true

[cache]
enabled = true
ttl = 7200

[security]
validate_keys = true
rate_limit_enabled = true
auto_redact = true

[logging]
level = "INFO"
rotation = "100 MB"
retention = "1 month"
```

### Development Configuration

For testing:

```toml
[llm]
model = "gpt-3.5-turbo"
api_key = "sk-..."

[performance]
max_concurrent_queries = 3

[logging]
level = "DEBUG"
console_enabled = true

[webui]
debug = true
```

## Best Practices

1. **Never commit API keys** - Use environment variables or .env file
2. **Start with conservative settings** - Increase limits gradually
3. **Enable caching** - Significantly improves performance
4. **Use appropriate models** - Balance cost vs capability
5. **Monitor logs** - Watch for errors and performance issues
6. **Regular backups** - Backup configuration files
7. **Document changes** - Comment custom settings
8. **Test thoroughly** - Validate after configuration changes

## Troubleshooting

### Common Issues

**Issue: Configuration not loading**
```bash
# Check file syntax
python -c "import tomli; tomli.load(open('config/config.toml', 'rb'))"
```

**Issue: API key not recognized**
```bash
# Verify environment variable
echo $OPENMANUS_LLM_API_KEY

# Check config file
grep api_key config/config.toml
```

**Issue: Performance degradation**
```toml
# Adjust these settings:
[performance]
max_concurrent_queries = 3  # Reduce if overloaded
enable_compression = true    # Enable for better throughput
```

## Next Steps

- [Quick Start](Quick-Start) - Run your first task
- [Performance Optimization](Performance-Optimization) - Tune for speed
- [Security Best Practices](Security-Best-Practices) - Secure your setup

---

**Need help?** Check the [FAQ](FAQ) or [open an issue](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
