# Orchestrator - Natural Language to CUBE Query Processing

## Overview

The **Orchestrator** is the main component that handles the complete pipeline from natural language queries to CUBE API results. It coordinates system prompt generation, LLM interaction, conversation memory management, and CUBE query execution.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   Orchestrator  │───▶│   CUBE Results  │
│ (Natural Lang.) │    │   (Pipeline)    │    │   (Data + CSV)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
              ┌──────▼──┐ ┌─────▼─────┐ ┌──▼──────┐
              │ System  │ │    LLM    │ │  CUBE   │
              │ Prompt  │ │  Client   │ │ Client  │
              │Generator│ │ (OpenAI)  │ │ (API)   │
              └─────────┘ └───────────┘ └─────────┘
                               │
                    ┌─────────────────┐
                    │ Conversation    │
                    │ Manager         │
                    │ (6 Messages)    │
                    └─────────────────┘
```

## Components

### 📋 **orchestrator.py** - Main Coordinator
- **Purpose**: Orchestrates the complete pipeline from user input to results
- **Features**:
  - Initializes all components (CUBE, OpenAI, System Prompt)
  - Manages the query processing workflow
  - Handles different response types (data, clarification, errors)
  - Maintains conversation state

### 💬 **conversation_manager.py** - Memory Management
- **Purpose**: Tracks conversation history for context-aware responses
- **Features**:
  - Maintains last 6 conversation messages
  - Formats messages for OpenAI API compatibility
  - Provides conversation context and analytics
  - Supports conversation export/import

### 🧠 **llm_client.py** - OpenAI Integration
- **Purpose**: Handles LLM interactions with enhanced JSON response parsing
- **Features**:
  - OpenAI GPT-4 integration with JSON response format
  - Enhanced response structure for chat interfaces
  - Token usage tracking and cost monitoring
  - Comprehensive error handling

### 🎯 **cube_client.py** - CUBE API Integration
- **Purpose**: Executes queries against CUBE instance
- **Features**:
  - JWT token authentication via docker-compose logs
  - Query validation and execution
  - CSV export of results
  - Metadata retrieval and health checks

### 📝 **system-prompt-generator/** - Context Preparation
- **Purpose**: Generates context-aware system prompts
- **Features**:
  - Parses YML view files from `my-cube-views/`
  - Loads business configuration and examples
  - Creates comprehensive system prompts
  - Supports ambiguity handling instructions

## Prerequisites

### System Requirements

1. **Docker & Docker Compose** - For CUBE instance
2. **Python 3.7+** - For orchestrator components
3. **OpenAI API Key** - For LLM integration
4. **CUBE Instance Running** - With JWT authentication enabled

### Environment Setup

Ensure your `.env` file in the project root contains:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# CUBE Configuration
CUBEJS_API_SECRET=baubeach
CUBEJS_DEV_MODE=true

# Database Configuration (for CUBE)
CUBEJS_DB_TYPE=mysql
CUBEJS_DB_HOST=mysql
CUBEJS_DB_NAME=ticketshopdb
CUBEJS_DB_USER=organiser
CUBEJS_DB_PASS=amatriciana
```

## Virtual Environment Setup

### 1. Create Virtual Environment

```bash
cd orchestrator
python3 -m venv orchestrator_env
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source orchestrator_env/bin/activate
```

**On Windows:**
```bash
orchestrator_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install openai python-dotenv requests pandas pyyaml
```

### 4. Verify Installation

```bash
pip list
```

Expected packages:
- `openai` (>= 1.0.0) - OpenAI API client
- `python-dotenv` - Environment variable loading
- `requests` - HTTP client for CUBE API
- `pandas` - Data manipulation and CSV export
- `pyyaml` - YAML file parsing

## Usage

### Basic Usage

```python
from orchestrator import QueryOrchestrator

# Initialize orchestrator (loads .env automatically)
orchestrator = QueryOrchestrator()
init_result = orchestrator.initialize()

if init_result['success']:
    # Process natural language query
    result = orchestrator.process_query("Show me total revenue by event")

    if result['response_type'] == 'data_result':
        print(f"Query successful: {result['row_count']} rows")
        print(f"CSV saved: {result['csv_filename']}")
    elif result['response_type'] == 'clarification':
        print("Need clarification:")
        for question in result['clarification_questions']:
            print(f"- {question}")
```

### Response Types

The orchestrator returns structured responses:

#### 1. **Data Result** (`data_result`)
```json
{
  "success": true,
  "response_type": "data_result",
  "llm_response": {
    "response_type": "cube_query",
    "interpretation": "I'm analyzing your event revenue data...",
    "description": "This shows total revenue and tickets sold by event",
    "confidence_score": 0.95
  },
  "cube_data": [...],
  "csv_filename": "cube_result_measures_20231201_143022.csv",
  "row_count": 15
}
```

#### 2. **Clarification Needed** (`clarification`)
```json
{
  "success": true,
  "response_type": "clarification",
  "llm_response": {
    "response_type": "clarification_needed",
    "interpretation": "I need more information to provide accurate results",
    "clarification_questions": [
      "What time period are you interested in?",
      "How would you like the results grouped?"
    ],
    "suggestions": [
      "Show event revenue for last month grouped by event name"
    ]
  }
}
```

#### 3. **Error** (`cube_error`, `llm_error`)
```json
{
  "success": false,
  "response_type": "cube_error",
  "error": "CUBE query execution failed",
  "llm_response": {...},
  "cube_error": {
    "error": "Invalid query structure",
    "details": "Missing required measures"
  }
}
```

## Testing

### Interactive Test

Run the comprehensive interactive test:

```bash
cd orchestrator/tests
python test_orchestrator_interactive.py
```

#### Test Workflow:

1. **Initialization** - Tests all component connections
2. **Sample Questions** - Displays 3 curated questions based on your YML views:
   - "Show me the total revenue and tickets sold for each event"
   - "Which events have the highest average order value?"
   - "What is the payment method breakdown for all events?"
3. **User Input** - Interactive query input with validation
4. **LLM Processing** - OpenAI API call with token usage tracking
5. **CUBE Execution** - Query execution and CSV export
6. **Results Display** - User-friendly result presentation
7. **Follow-up** - Conversation continuation with memory

#### Expected Test Output:

```
🚀 ORCHESTRATOR INTERACTIVE TEST
==================================================
Test Session ID: 20231201_143022

🔧 Initializing Orchestrator...
📊 Initialization Result:
   Success: True
   ✅ CUBE Client: Connected
   ✅ LLM Client: gpt-4
   ✅ System Prompt: 14864 chars
   ✅ Available Cubes: 1 views

📋 SAMPLE QUESTIONS ABOUT EVENT DATA
----------------------------------------
1. Show me the total revenue and tickets sold for each event
   💡 Gets revenue metrics (total_order_value, total_tickets_sold) grouped by event name

[... interactive flow continues ...]
```

### Troubleshooting Tests

#### Common Issues:

1. **JWT Token Error**
   ```
   Error: Failed to retrieve JWT token
   ```
   **Solution**: Ensure CUBE docker container is running and accessible

2. **OpenAI API Error**
   ```
   Error: LLM API error: Incorrect API key provided
   ```
   **Solution**: Check `OPENAI_API_KEY` in `.env` file

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   **Solution**: Activate virtual environment and install dependencies

4. **Connection Error**
   ```
   Error: Failed to connect to CUBE API
   ```
   **Solution**: Ensure docker-compose services are running:
   ```bash
   docker-compose up -d
   docker-compose ps  # Check service status
   ```

## Configuration

### Customizing the Orchestrator

```python
# Custom configuration
orchestrator = QueryOrchestrator(
    openai_api_key="your-key",           # Override env var
    cube_base_url="http://localhost:4000", # CUBE API URL
    cube_api_secret="baubeach",          # CUBE secret
    max_conversation_messages=6          # Conversation memory limit
)
```

### Adding New YML Views

1. Add your YML view files to `system-prompt-generator/my-cube-views/`
2. Regenerate system prompt:
   ```python
   result = orchestrator.regenerate_system_prompt()
   ```

### Business Context Configuration

Edit `system-prompt-generator/config/business_domain.yaml` to customize:
- Business entities and relationships
- Key metrics and calculations
- Common business questions

## API Reference

### Main Methods

#### `initialize() -> Dict[str, Any]`
Initialize all components and validate connections.

#### `process_query(user_query: str) -> Dict[str, Any]`
Process natural language query through complete pipeline.

#### `get_conversation_history() -> List[Dict[str, Any]]`
Get current conversation messages.

#### `clear_conversation() -> None`
Clear conversation history.

#### `get_status() -> Dict[str, Any]`
Get health status of all components.

#### `regenerate_system_prompt() -> Dict[str, Any]`
Regenerate system prompt (useful after YML updates).

## File Structure

```
orchestrator/
├── orchestrator.py              # Main coordinator
├── conversation_manager.py      # Memory management
├── llm_client.py               # OpenAI integration
├── cube_client.py              # CUBE API client
├── system-prompt-generator/     # Context preparation (renamed from llm-integration)
│   ├── context_preparation/     # Core prompt generation
│   ├── my-cube-views/          # YML view files
│   ├── templates/              # Prompt templates
│   ├── config/                 # Business configuration
│   └── tests/                  # System prompt tests
├── tests/
│   ├── test_orchestrator_interactive.py  # Interactive pipeline test
│   └── __init__.py
├── results/                    # Generated CSV files
├── README.md                   # This file
└── __init__.py
```

## Next Steps

1. **Add YML Views** - Place your CUBE view files in `system-prompt-generator/my-cube-views/`
2. **Configure Business Context** - Update business domain configuration
3. **Run Tests** - Validate the complete pipeline with interactive tests
4. **Build Chat Interface** - Use orchestrator as backend for chat applications
5. **Monitor Usage** - Track OpenAI API usage and costs

## Dependencies

### Required Python Packages
- `openai >= 1.0.0` - OpenAI API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP client for APIs
- `pandas` - Data manipulation and export
- `pyyaml` - YAML configuration parsing

### System Dependencies
- Docker & Docker Compose (for CUBE instance)
- Python 3.7+
- Active OpenAI API account

### Optional Dependencies
- `jupyter` - For interactive development
- `pytest` - For additional testing frameworks

---

The orchestrator provides a complete, production-ready pipeline for natural language to CUBE query processing with comprehensive error handling, conversation memory, and chat interface compatibility.