# Data Analyst Agent - Modular Architecture

## Overview

The Data Analyst Agent is an intelligent CSV data analysis system that accepts natural language queries and generates comprehensive analytical reports. This system has been restructured into a modular architecture following the specifications in `.claude/CLAUDE.md`.

## Features

- **Modular Architecture**: Clean separation of concerns with independent, testable components
- **CSV Data Analysis**: Automatic column detection, statistical analysis, and data profiling
- **Natural Language Queries**: Process user questions and generate targeted analysis
- **Visualization Generation**: Create interactive charts and graphs (HTML/PNG formats)
- **Code Execution**: Safe Python code execution for custom calculations
- **Comprehensive Reporting**: Generate markdown reports with insights and recommendations
- **Backward Compatibility**: Legacy interface preserved while using modern modular backend

## Project Structure

```
analyst-service/
├── .env.example                 # Environment variables template
├── .env                        # Environment variables (create from example)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/
│   ├── analyst_agent.py        # Legacy interface (backward compatible)
│   ├── config.py              # Configuration management
│   └── core/                  # Modular components
│       ├── __init__.py
│       ├── models/            # Data models and validation
│       │   ├── __init__.py
│       │   └── models.py      # State, AnalystAgentOutput, ToolResponse
│       ├── tools/             # Analysis tools
│       │   ├── __init__.py
│       │   ├── column_analyzer.py      # Dataset structure analysis
│       │   ├── code_executor.py        # Python code execution
│       │   ├── statistical_processor.py # Mathematical computations
│       │   └── visualization_generator.py # Chart and graph creation
│       └── agent/             # Agent orchestration
│           ├── __init__.py
│           └── agent_orchestrator.py   # Main agent coordination
├── tests/                     # Test suite
│   ├── models/               # Model tests
│   ├── tools/                # Tool tests
│   └── agent/                # Agent tests
└── venv/                     # Virtual environment
```

## Installation & Setup

### 1. Environment Setup

```bash
# Clone/navigate to the project directory
cd analyst-service

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Required: OPENAI_API_KEY=your_openai_api_key_here
```
## Core Components

### 1. Models (`src/core/models/`)
- **State**: Agent state management (user query, file name)
- **AnalystAgentOutput**: Structured analysis results
- **ToolResponse**: Standardized tool execution responses

### 2. Tools (`src/core/tools/`)
- **column_analyzer.py**: CSV column inspection and metadata extraction
- **code_executor.py**: Safe Python code execution with output capture
- **statistical_processor.py**: Mathematical computations and statistical analysis
- **visualization_generator.py**: Chart creation and visualization generation

### 3. Agent (`src/core/agent/`)
- **agent_orchestrator.py**: Main agent coordination, LLM integration, and workflow management

### 4. Configuration (`src/config.py`)
- Centralized environment variable management
- Configuration validation and logging setup
- File handling utilities

## Testing

### Run All Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific component tests
python -m pytest tests/models/ -v
python -m pytest tests/tools/ -v
python -m pytest tests/agent/ -v
```

### Interactive Testing
```bash
# Run interactive test with your own queries
python tests/test_interactive_analysis.py
```

## Key Features

### Error Handling & Debugging
- Comprehensive logging at each core function step
- Try/catch mechanisms for critical operations
- Detailed error messages and recovery strategies
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### Backward Compatibility
- Original `analyst_agent.py` legacy interface preserved
- Legacy function wrappers that use modular components
- Seamless migration path for existing integrations

### Security & Validation
- Input validation for all functions
- File type and size validation
- Safe code execution with restricted operations
- Environment variable validation at startup

### Performance & Scalability
- Modular design enables independent scaling
- Efficient tool coordination
- Minimal memory footprint
- Optimized for large CSV datasets

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **API Key Issues**: Verify OPENAI_API_KEY is set in .env file
3. **File Access**: Check file paths are absolute and files exist
4. **Memory Issues**: Consider file size limits and available system memory

### Debug Mode
Enable debug mode in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Log Analysis
Check logs for detailed execution traces:
- Configuration validation messages
- Tool execution steps
- Error traces with context
- Performance metrics

## Development

### Adding New Tools
1. Create tool module in `src/core/tools/`
2. Add tool import to `src/core/tools/__init__.py`
3. Create corresponding tests in `tests/tools/`
4. Update agent orchestrator if needed

### Extending Models
1. Add new models to `src/core/models/models.py`
2. Export in `src/core/models/__init__.py`
3. Create tests in `tests/models/`
4. Update documentation

### Configuration Changes
1. Update `src/config.py` for new settings
2. Add to `.env.example`
3. Update validation logic
4. Test configuration loading