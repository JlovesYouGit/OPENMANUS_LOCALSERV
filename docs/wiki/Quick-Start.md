# Quick Start Guide

Get up and running with OpenManus in minutes!

## Prerequisites

Before starting, ensure you have:
- ✅ [Installed OpenManus](Installation)
- ✅ [Configured API keys](Configuration)
- ✅ Activated your Python environment

## Running OpenManus

### 1. Basic Terminal Interface

The simplest way to start:

```bash
python main.py
```

Then input your task via the terminal:

```
Enter your idea: What's the weather like in New York?
```

**Example Output:**
```
🤖 Processing your request...
🔍 Using weather tool...
📊 Current weather in New York:
    Temperature: 72°F (22°C)
    Condition: Partly Cloudy
    Humidity: 65%
```

### 2. Web UI Interface 🌐

For a more user-friendly experience:

```bash
python web_ui.py
```

Then open your browser to: **http://localhost:5000**

**Features:**
- 💬 Chat-like interface
- 📝 Message history
- 🎨 Syntax highlighting
- 📊 Visual data display
- 💾 Session management

### 3. MCP Tools Version

For enhanced tool integration:

```bash
python run_mcp.py
```

This version provides:
- Advanced tool coordination
- Better error handling
- Extended capabilities

### 4. Multi-Agent System (Experimental)

For complex tasks requiring multiple agents:

```bash
python run_flow.py
```

⚠️ **Note**: This is an experimental feature and may be unstable.

## Your First Tasks

### Task 1: Web Search

```python
# Terminal
python main.py

# Input
Enter your idea: Search for the latest news about AI
```

### Task 2: Data Analysis

```python
# Enable data analysis agent in config/config.toml
[runflow]
use_data_analysis_agent = true

# Run
python run_flow.py

# Input
Enter your idea: Analyze this dataset and create a visualization
```

### Task 3: Browser Automation

```python
# Make sure Playwright is installed
playwright install

# Run
python main.py

# Input
Enter your idea: Go to GitHub and search for OpenManus
```

### Task 4: Code Generation

```python
# Input
Enter your idea: Write a Python function to calculate fibonacci numbers
```

## Web UI Walkthrough

### Starting the Web UI

1. **Launch the server:**
   ```bash
   python web_ui.py
   ```

2. **Open your browser:**
   Navigate to http://localhost:5000

3. **Start chatting:**
   Type your message in the input box and press Enter or click Send

### Web UI Features

**📝 Message Input**
- Multi-line support (Shift + Enter for new line)
- Enter to send message
- Auto-scroll to latest messages

**💾 Session Management**
- Conversations are saved automatically
- Clear history with the "Clear" button
- Resume previous sessions

**⚙️ Settings**
- Adjust model parameters
- Toggle features on/off
- View system status

**📊 Visual Output**
- Charts and graphs rendered inline
- Code syntax highlighting
- Markdown support
- Image display

## Common Use Cases

### Information Retrieval

```
Question: What is the current stock price of Tesla?
```

OpenManus will:
1. Identify need for real-time data
2. Use appropriate search tools
3. Extract and format the information
4. Present results clearly

### Code Assistance

```
Request: Create a REST API with FastAPI for user management
```

OpenManus will:
1. Generate complete code structure
2. Include error handling
3. Add documentation
4. Provide usage examples

### Data Processing

```
Task: Load this CSV file and create a summary report
```

OpenManus will:
1. Read and parse the file
2. Perform statistical analysis
3. Generate visualizations
4. Create a comprehensive report

### Web Automation

```
Instruction: Navigate to Amazon and search for laptops under $1000
```

OpenManus will:
1. Launch browser automation
2. Navigate to the site
3. Perform the search
4. Extract relevant results

## Configuration Tips

### Performance Tuning

For better performance, adjust in `config/config.toml`:

```toml
[performance]
max_concurrent_queries = 5
enable_caching = true
compression_level = "high"
```

### Model Selection

Choose appropriate models:

```toml
[llm]
model = "gpt-4o"  # For complex tasks
# model = "gpt-3.5-turbo"  # For faster, simpler tasks
```

### Tool Configuration

Enable/disable specific tools:

```toml
[tools]
enable_browser = true
enable_code_execution = false  # Disable if security is a concern
enable_web_search = true
```

## Performance Testing

Test your setup:

```bash
# Run performance tests
python test_performance.py

# Test query management
python test_query_management.py
```

## Next Steps

Now that you're up and running:

1. **Explore Features**: Try different types of tasks
2. **Customize Configuration**: Adjust settings to your needs
3. **Learn Advanced Features**: Check out [Advanced Features](Advanced-Features)
4. **Join Community**: Share your experience and get help
5. **Read Documentation**: Deep dive into [Architecture](Architecture)

## Troubleshooting Quick Fixes

**Problem: Server won't start**
```bash
# Check if port is already in use
lsof -i :5000  # On Unix/macOS
netstat -ano | findstr :5000  # On Windows

# Use a different port
python web_ui.py --port 8080
```

**Problem: Slow responses**
```bash
# Enable query management optimization
# Check config/config.toml performance settings
```

**Problem: API key errors**
```bash
# Verify configuration
python verify_config.py
```

## Getting Help

- 📖 Read the [FAQ](FAQ)
- 🐛 Report issues on [GitHub](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/issues)
- 💬 Ask in [Discussions](https://github.com/JlovesYouGit/OPENMANUS_LOCALSERV/discussions)
- 📚 Check detailed [Documentation](Home)

---

**Ready for more?** Check out [Advanced Features](Advanced-Features) to unlock the full potential of OpenManus!
