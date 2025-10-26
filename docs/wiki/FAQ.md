# Frequently Asked Questions (FAQ)

## General Questions

### What is OpenManus?

OpenManus is an open-source AI agent system that can solve various tasks using multiple tools. It's inspired by the Manus concept and designed to be accessible without requiring invite codes.

### Is OpenManus free to use?

Yes! OpenManus is open-source under the MIT License. However, you'll need API keys for LLM services (like OpenAI), which may have associated costs.

### What can OpenManus do?

OpenManus can:
- 🔍 Search the web for information
- 💻 Write and execute code
- 📊 Analyze data and create visualizations
- 🌐 Automate browser tasks
- 📝 Generate documents and reports
- 🤖 Coordinate multiple AI agents
- And much more!

### How is OpenManus different from ChatGPT?

While ChatGPT is primarily conversational, OpenManus:
- Can use external tools and APIs
- Performs automated web browsing
- Executes code locally
- Coordinates multiple specialized agents
- Offers more customization and control

## Installation & Setup

### What are the system requirements?

**Minimum:**
- Python 3.12+
- 4GB RAM
- 2GB disk space
- Internet connection

**Recommended:**
- Python 3.12+
- 8GB+ RAM
- 5GB disk space
- GPU for local model inference (optional)

### Which Python version should I use?

Python 3.12 or higher is required. Python 3.13 is also supported.

### Do I need a GPU?

No, a GPU is optional. It's beneficial if you want to:
- Run local LLMs
- Use DirectML acceleration (Windows AMD GPUs)
- Improve performance with vision models

### Installation failed. What should I do?

1. **Verify Python version**: `python --version`
2. **Use a clean virtual environment**
3. **Update pip**: `pip install --upgrade pip`
4. **Try uv installer** (faster): See [Installation Guide](Installation)
5. **Check error logs** for specific issues
6. **Search GitHub issues** for similar problems

### Can I run OpenManus on Windows/Mac/Linux?

Yes! OpenManus supports:
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora, etc.)

## Configuration

### Where do I get API keys?

**OpenAI:**
1. Sign up at https://platform.openai.com/
2. Go to API Keys section
3. Create a new key
4. Add to `config/config.toml`

**Other providers:**
- Azure OpenAI: https://azure.microsoft.com/en-us/products/ai-services/openai-service
- Anthropic: https://www.anthropic.com/
- Local models: No API key needed

### How much does it cost to run OpenManus?

OpenManus itself is free, but you'll pay for:

**API Usage (OpenAI GPT-4o example):**
- Input: ~$5 per 1M tokens
- Output: ~$15 per 1M tokens
- Average task: $0.01 - $0.10

**Cost-saving tips:**
- Use GPT-3.5-turbo for simpler tasks
- Enable caching to reduce API calls
- Set token limits appropriately
- Use local models when possible

### Can I use local models instead of OpenAI?

Yes! OpenManus supports:
- llama.cpp servers
- Ollama
- vLLM
- Any OpenAI-compatible API

Configure in `config/config.toml`:
```toml
[llm]
model = "llama-2-7b"
base_url = "http://localhost:8000/v1"
api_key = "not-required"
```

### My API key isn't working

Check these common issues:
1. ✅ Key format correct (starts with `sk-` for OpenAI)
2. ✅ No extra spaces or quotes
3. ✅ Key not expired or revoked
4. ✅ Sufficient credits in account
5. ✅ Correct API endpoint URL
6. ✅ File permissions for config.toml

### How do I switch between different models?

Edit `config/config.toml`:

```toml
[llm]
model = "gpt-4o"  # Change this line
```

Or use environment variable:
```bash
export OPENMANUS_LLM_MODEL="gpt-3.5-turbo"
```

## Usage

### How do I run OpenManus?

**Terminal interface:**
```bash
python main.py
```

**Web interface:**
```bash
python web_ui.py
```

**MCP tools:**
```bash
python run_mcp.py
```

### The response is too slow

Try these optimizations:

1. **Enable caching:**
   ```toml
   [cache]
   enabled = true
   ```

2. **Reduce concurrent queries:**
   ```toml
   [performance]
   max_concurrent_queries = 3
   ```

3. **Use faster model:**
   ```toml
   [llm]
   model = "gpt-3.5-turbo"
   ```

4. **Enable compression:**
   ```toml
   [performance]
   enable_compression = true
   ```

See [Performance Optimization](Performance-Optimization) for more tips.

### Can I run multiple instances?

Yes, but be careful with:
- API rate limits
- Port conflicts (use different ports)
- Shared cache/log directories
- Concurrent API costs

### How do I stop OpenManus?

**Terminal interface:**
- Press `Ctrl+C`

**Web interface:**
- Press `Ctrl+C` in terminal
- Or close browser and terminal

**Background process:**
```bash
# Find process
ps aux | grep openmanus

# Kill process
kill <PID>
```

## Features

### Does OpenManus have web search?

Yes! Enable in configuration:

```toml
[tools.search]
enabled = true
providers = ["duckduckgo", "google"]
```

Supported search engines:
- DuckDuckGo (default, no API key needed)
- Google (requires API key)
- Bing (requires API key)
- Baidu

### Can it browse websites?

Yes! Using Playwright:

```bash
# Install browser
playwright install

# Enable in config
[tools.browser]
enabled = true
```

### Does it support code execution?

Yes, but it's disabled by default for security:

```toml
[tools.code]
enabled = true  # ⚠️ Security risk!
use_docker = true  # Recommended for safety
```

### Can I upload files for analysis?

Yes! Supported file types:
- 📊 CSV, Excel
- 📄 PDF, TXT, MD
- 🖼️ Images (PNG, JPG, etc.)
- 💾 JSON, YAML

Web UI: Drag and drop files
Terminal: Provide file path in prompt

### How do I use the multi-agent system?

Enable in `config/config.toml`:

```toml
[runflow]
use_data_analysis_agent = true
```

Then run:
```bash
python run_flow.py
```

⚠️ **Note**: Experimental feature, may be unstable.

### Does it remember previous conversations?

Yes! Conversation history is:
- Saved automatically to `chat_history.json`
- Compressed for efficiency
- Cached for quick retrieval
- Persists across sessions

Clear history:
```bash
rm chat_history.json
# Or use "Clear" button in Web UI
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'XXX'"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

### "API rate limit exceeded"

Your API key has rate limits:

**Solutions:**
1. Wait and retry
2. Upgrade API plan
3. Reduce `max_concurrent_queries`
4. Implement request throttling

### "Connection timeout" errors

**Possible causes:**
- Poor internet connection
- API endpoint down
- Firewall/proxy blocking
- Timeout too short

**Solutions:**
```toml
[llm]
timeout = 120  # Increase timeout
```

### Browser automation fails

```bash
# Reinstall Playwright browsers
playwright install --force

# Install system dependencies (Linux)
playwright install-deps
```

### "Permission denied" errors

**Linux/Mac:**
```bash
# Fix config file permissions
chmod 600 config/config.toml

# Fix script permissions
chmod +x main.py
```

**Windows:**
- Run terminal as Administrator
- Check file properties → Security

### Web UI won't start

**Port already in use:**
```bash
# Use different port
python web_ui.py --port 8080
```

**Check what's using port 5000:**
```bash
# Linux/Mac
lsof -i :5000

# Windows
netstat -ano | findstr :5000
```

### High memory usage

**Reduce memory consumption:**

```toml
[performance]
max_concurrent_queries = 2

[cache]
max_size = 512  # MB

[gpu]
max_memory = 2048  # MB
```

**Clear cache:**
```bash
rm -rf context_cache/*
```

## Security & Privacy

### Is my data safe?

OpenManus:
- ✅ Runs locally on your machine
- ✅ You control all data
- ✅ Automated sensitive data redaction
- ✅ No telemetry or data collection

**However:**
- API calls send data to LLM providers
- Review API provider privacy policies
- Don't share sensitive information

### How do I protect API keys?

1. **Never commit to git**
   ```bash
   # Already in .gitignore
   config/config.toml
   .env
   ```

2. **Use environment variables**
   ```bash
   export OPENMANUS_LLM_API_KEY="sk-..."
   ```

3. **Set file permissions**
   ```bash
   chmod 600 config/config.toml
   ```

4. **Enable auto-redaction**
   ```toml
   [security]
   auto_redact = true
   ```

### Can I use OpenManus offline?

Partially:
- ❌ Requires API connection for LLM
- ✅ Use local models (llama.cpp, ollama)
- ❌ Web search requires internet
- ✅ Code execution works offline
- ✅ Data analysis works offline

### Is code execution safe?

⚠️ **Security Warning**: Code execution has risks!

**Safeguards:**
- Disabled by default
- Docker sandboxing available
- Resource limits enforced
- Timeout protections

**Best practices:**
- Keep `enabled = false` unless needed
- Use Docker sandboxing
- Don't run untrusted code
- Monitor execution logs

## Development

### How can I contribute?

See [Contributing Guide](Contributing) for:
- Code contributions
- Bug reports
- Feature requests
- Documentation improvements
- Testing

### Can I create custom tools?

Yes! Add custom tools in `app/tool/`:

```python
# app/tool/my_custom_tool.py
class MyCustomTool:
    def __init__(self):
        self.name = "my_tool"
    
    def execute(self, params):
        # Your tool logic
        return result
```

Register in configuration:
```toml
[custom_tools.my_tool]
enabled = true
```

### Where can I find the API documentation?

- [API Reference](API-Reference) in wiki
- Inline code documentation
- `app/` directory for implementation
- [Examples](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/tree/master/examples)

### How do I run tests?

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
pytest

# Run specific test
pytest tests/test_specific.py

# Run with coverage
pytest --cov=app
```

## Community & Support

### Where can I get help?

1. **Check documentation**: [Wiki Home](Home)
2. **Search issues**: [GitHub Issues](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
3. **Ask community**: [Discussions](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/discussions)
4. **Report bugs**: [New Issue](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues/new)

### Is there a Discord/Slack community?

Check the main README for community links. The OpenManus community is growing!

### How do I report a bug?

[Open an issue](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues/new) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error logs/screenshots

### How often is OpenManus updated?

- Active development ongoing
- Regular bug fixes
- Feature additions based on community feedback
- Check [Releases](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/releases) for updates

## Comparison

### OpenManus vs AutoGPT?

**OpenManus:**
- ✅ Simpler setup
- ✅ Better performance optimization
- ✅ Cleaner codebase
- ✅ Focus on tool integration

**AutoGPT:**
- More autonomous
- Larger community
- More plugins available

### OpenManus vs LangChain?

**OpenManus:**
- Complete agent system
- Ready to use out-of-box
- Optimized for performance
- Web UI included

**LangChain:**
- Framework/library
- More flexible/customizable
- Requires more coding
- Larger ecosystem

---

**Still have questions?** 

- 📖 Read more [Documentation](Home)
- 💬 Ask in [Discussions](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/discussions)
- 🐛 Report [Issues](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
