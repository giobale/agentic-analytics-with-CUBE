# LLM Integration for CUBE Semantic Layer

## Overview

This component provides intelligent natural language query processing for the CUBE semantic layer. It transforms user questions into properly structured CUBE API calls through advanced context preparation and prompt engineering.

## Context Preparation Manager

The **Context Preparation Manager** is the core orchestrator that dynamically builds comprehensive system prompts for LLM integration. It combines multiple information sources to create intelligent, context-aware prompts for natural language query processing.

### Key Components

#### 1. **ContextManager** (Main Orchestrator)
- **Purpose**: Coordinates all context preparation components
- **Location**: `context_preparation/context_manager.py`
- **Features**:
  - Orchestrates YML parsing, business configuration, and prompt building
  - Generates comprehensive system prompts ready for OpenAI API
  - Provides validation and metadata for debugging
  - Handles error management and fallback scenarios

#### 2. **YMLParser** (View File Processing)
- **Purpose**: Parses CUBE view YML files from `my-cube-views/` directory
- **Location**: `context_preparation/yml_parser.py`
- **Features**:
  - Automatically discovers and parses all YML view files
  - Extracts dimensions and measures from CUBE view specifications
  - Handles multiple YML formats (cube definitions and view definitions)
  - Provides structured view information for prompt generation

#### 3. **BusinessConfig** (Domain Knowledge)
- **Purpose**: Manages business context and domain-specific information
- **Location**: `context_preparation/business_config.py`
- **Configuration**: `config/business_domain.yaml`
- **Features**:
  - Loads business entities, relationships, and key metrics
  - Provides domain-specific context for better query understanding
  - Configurable through YAML files for easy customization

#### 4. **ExampleManager** (Learning System)
- **Purpose**: Manages successful query examples and natural language patterns
- **Location**: `context_preparation/example_manager.py`
- **Examples**: `templates/examples/`
- **Features**:
  - Loads successful query examples for pattern recognition
  - Provides natural language to CUBE API mapping patterns
  - Includes ambiguous query handling examples
  - Supports similarity matching for query suggestions

#### 5. **PromptBuilder** (Template Engine)
- **Purpose**: Constructs comprehensive system prompts using templates
- **Location**: `context_preparation/prompt_builder.py`
- **Templates**: `templates/`
- **Features**:
  - Combines all context components into structured prompts
  - Uses template-driven approach for consistency
  - Includes ambiguity handling and clarification instructions
  - Generates prompts optimized for OpenAI API integration

### Architecture Flow

```
User YML Files → YMLParser →
Business Config → BusinessConfig →
Examples → ExampleManager → ContextManager → PromptBuilder → System Prompt
Templates → PromptBuilder →
```

### Key Features

- **Dynamic Context Building**: Automatically adapts to new YML files and configuration changes
- **Business-Aware Processing**: Understands domain-specific terminology and relationships
- **Example-Driven Learning**: Uses successful query patterns to improve accuracy
- **Ambiguity Handling**: Provides intelligent clarification when queries are unclear
- **Template-Based Flexibility**: Easy to modify prompts without code changes
- **Comprehensive Validation**: Ensures all components are properly configured

## Testing

### Prerequisites

Before running tests, you need to set up a Python virtual environment with the required dependencies.

### Setup Instructions

1. **Navigate to the LLM integration directory**:
   ```bash
   cd llm-integration
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv test_env
   ```

3. **Activate the virtual environment**:
   ```bash
   source test_env/bin/activate
   ```

4. **Install required dependencies**:
   ```bash
   pip install pyyaml
   ```

### Running the Test

1. **Navigate to the tests directory**:
   ```bash
   cd tests
   ```

2. **Run the system prompt generation test**:
   ```bash
   python test_system_prompt_generation.py
   ```

### Test Output

The test will:
- ✅ Parse YML files from `my-cube-views/` directory
- ✅ Load business configuration and examples
- ✅ Generate a complete system prompt
- ✅ Save the generated prompt to `tests/results/system_prompt_[timestamp].txt`
- ✅ Display metadata and prompt preview

### Expected Results

```
🚀 Testing LLM Integration System

📂 Base path: /path/to/llm-integration
📁 Views path: /path/to/my-cube-views
📄 Found 1 YML files: ['event_performance_overview.yml']

🤖 Generating system prompt...
✅ System prompt generated successfully!
📊 Metadata: {'views_count': 1, 'examples_count': 6, 'business_entities': 0, ...}
📏 Prompt length: 14864 characters
💾 System prompt saved to: tests/results/system_prompt_20250918_193658.txt

🎉 Test completed successfully!
```

## Configuration

### Adding YML View Files

1. Place your CUBE view YML files in the `my-cube-views/` directory
2. The system will automatically discover and parse them
3. Run the test to validate parsing and integration

### Customizing Business Context

Edit `config/business_domain.yaml` to customize:
- Business name and description
- Entity definitions and relationships
- Key metrics and calculations
- Common business questions

### Modifying Templates

Templates are located in `templates/`:
- `system_prompt_base.txt` - Main prompt structure
- `cube_api_instructions.txt` - CUBE API formatting rules
- `ambiguity_instructions.txt` - Ambiguity handling guidelines
- `examples/` - Query examples and patterns

## Integration

The generated system prompt can be used directly with OpenAI API:

```python
from context_preparation.context_manager import ContextManager

# Initialize context manager
manager = ContextManager()

# Generate system prompt
result = manager.generate_system_prompt()
system_prompt = result['system_prompt']

# Use with OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Show me revenue by event"}
    ]
)
```

## Dependencies

- **Python 3.7+**
- **PyYAML** - For parsing YML configuration files

## Notes

- Virtual environment folders are automatically excluded from git
- Generated prompts are saved to `tests/results/` for inspection
- The system is designed to be easily extensible and configurable
- All components include comprehensive error handling and validation