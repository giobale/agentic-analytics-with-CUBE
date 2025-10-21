# Query Ambiguity Assessor Agent

A PydanticAI-based agent that interprets natural language queries and ensures they are clear and unambiguous before constructing Cube.js API calls.

## Overview

The Query Ambiguity Assessor implements a state-based workflow to:

1. **Assess** user queries for clarity
2. **Request clarifications** when ambiguities are detected
3. **Confirm** the interpreted query with the user
4. **Construct** valid Cube.js API calls only after user confirmation

## Architecture

### State-Based Workflow

```
┌─────────────────────────┐
│  QUERY_ASSESSMENT       │
│  (Initial evaluation)   │
└───────┬─────────────────┘
        │
        ├─── Ambiguous ────► CLARIFICATION_REQUEST ──► RECEIVE_CLARIFICATION ──┐
        │                                                                      │
        └─── Clear ─────────► QUERY_CONFIRMATION ◄──────────────────────────┘
                                     │
                                     ├─── Confirmed ──► API_CALL_CONSTRUCTION
                                     │
                                     └─── Rejected ───► QUERY_REJECTION_HANDLER
```

### Components

```
query-ambiguity-assessor/
├── agent.py              # Main PydanticAI agent implementation
├── schemas.py            # Pydantic models for all data structures
├── prompts.py            # System prompts for each state
├── tools/                # Agent tools for metadata and context management
│   ├── metadata_tools.py # Access cube metadata
│   └── context_tools.py  # Manage conversation context
└── utils/                # Utility functions (reserved for future use)
```

## Key Features

### 1. Ambiguity Detection

The agent identifies five types of ambiguities:

- **Time specification**: Unclear time periods or date ranges
- **Grouping granularity**: Unclear aggregation level (daily/weekly/monthly)
- **Filter criteria**: Missing or unclear filter conditions
- **Measure ambiguity**: Unclear which metrics to calculate
- **Dimension ambiguity**: Unclear grouping or filtering dimensions

### 2. Focused Clarification

- Addresses **ONE ambiguity at a time** to avoid overwhelming users
- Provides contextual examples and suggestions
- Uses available cube metadata to offer valid options

### 3. User Confirmation

- Always confirms interpretation before proceeding
- Presents clear, natural language summaries
- Supports confirmation/rejection via UI buttons

### 4. Structured Outputs

All agent responses use type-safe Pydantic models ensuring consistency with the orchestrator and frontend.

## Usage

### Basic Usage

```python
from orchestrator.agents.query_ambiguity_assessor import (
    QueryAmbiguityAssessor,
    CubeMetadata,
    ConversationContext
)

# Initialize agent
agent = QueryAmbiguityAssessor(
    model="openai:gpt-4o",
    api_key="your-openai-api-key"
)

# Prepare cube metadata
cube_metadata = CubeMetadata(
    view_name="EventPerformanceOverview",
    measures=[
        {"name": "total_revenue", "title": "Total Revenue", "description": "Sum of all order values"},
        {"name": "ticket_count", "title": "Tickets Sold", "description": "Total tickets sold"}
    ],
    dimensions=[
        {"name": "event_name", "title": "Event Name", "description": "Name of the event", "type": "string"},
        {"name": "order_date", "title": "Order Date", "description": "Date of order", "type": "time"}
    ]
)

# Assess a query
response = await agent.assess_query(
    user_query="Show me revenue last month",
    session_id="session-123",
    cube_metadata=cube_metadata
)

# Handle different response types
if response.response_type == "clarification":
    # Agent needs clarification
    print(f"Question: {response.data['clarification_question']}")
    print(f"Suggestions: {response.data['suggestions']}")

elif response.response_type == "confirmation":
    # Agent ready for confirmation
    print(f"Interpretation: {response.data['confirmation_message']}")
    # User clicks "Confirm" or "Reject" in UI

elif response.response_type == "cube_query":
    # Ready to execute
    cube_query = response.data['cube_query']
    # Pass to cube client for execution
```

### Handling Clarifications

```python
# User provides clarification
clarification_response = await agent.receive_clarification(
    user_response="All events in December 2024",
    ambiguous_aspect="time_specification",
    original_query="Show me revenue last month",
    cube_metadata=cube_metadata,
    conversation_context=conversation_context
)
```

### Handling Confirmation/Rejection

```python
# User confirms the interpretation
api_call_response = await agent.construct_api_call(
    confirmed_parameters=confirmed_params,
    original_query="Show me revenue last month",
    cube_metadata=cube_metadata,
    conversation_context=conversation_context
)

# User rejects the interpretation
rejection_response = await agent.handle_rejection(
    original_query="Show me revenue last month",
    conversation_context=conversation_context
)
```

## Data Models

### AgentState

Enumeration of all possible agent states:
- `QUERY_ASSESSMENT`
- `CLARIFICATION_REQUEST`
- `RECEIVE_CLARIFICATION`
- `QUERY_CONFIRMATION`
- `QUERY_REJECTION_HANDLER`
- `API_CALL_CONSTRUCTION`
- `COMPLETED`
- `ERROR`

### AgentResponse

Unified response format:

```python
{
    "success": bool,
    "state": AgentState,
    "response_type": "assessment" | "clarification" | "confirmation" | "rejection" | "cube_query" | "error",
    "data": {...},  # State-specific data
    "error": str | None,
    "timestamp": str
}
```

### CubeQueryParameters

Structured Cube.js query:

```python
{
    "measures": ["total_revenue"],
    "dimensions": ["event_name"],
    "timeDimensions": [
        {
            "dimension": "order_date",
            "granularity": "month",
            "dateRange": "last month"
        }
    ],
    "filters": [],
    "order": {},
    "limit": None
}
```

## Tools Available to Agent

The agent has access to the following tools:

### Metadata Tools
- `tool_get_available_measures()`: List all measures
- `tool_get_available_dimensions()`: List all dimensions
- `tool_get_time_dimensions()`: List time dimensions
- `tool_validate_measure(measure_name)`: Check if measure exists
- `tool_validate_dimension(dimension_name)`: Check if dimension exists

### Context Tools
- `tool_update_context(key, value)`: Store clarification info
- `tool_get_context()`: Retrieve current context
- `tool_clear_context()`: Reset context (on rejection)

## Integration with Orchestrator

The agent integrates seamlessly with the existing orchestrator:

1. Replace direct LLM calls with agent methods
2. Convert cube metadata to `CubeMetadata` format
3. Maintain conversation context using `ConversationContext`
4. Map agent responses to orchestrator response types

See the main README for integration examples.

## Best Practices

1. **Always provide complete cube metadata** - The agent uses this to validate requests and provide suggestions

2. **Maintain conversation context** - Pass the same `ConversationContext` instance through the entire conversation session

3. **Handle all response types** - The agent can return multiple response types; ensure your integration handles each appropriately

4. **Use session IDs** - Unique session IDs help track and debug conversations

5. **Log agent state transitions** - Useful for debugging and understanding user interactions

## Error Handling

The agent uses comprehensive try-catch mechanisms and returns structured error responses:

```python
{
    "success": False,
    "state": AgentState.ERROR,
    "response_type": "error",
    "data": {},
    "error": "Detailed error message"
}
```

## Future Enhancements

Planned improvements:
- Multi-turn clarification optimization
- Learning from past successful queries
- Automatic suggestion ranking based on query patterns
- Integration with cube-query-validator agent (next phase)

## Dependencies

- `pydantic-ai >= 0.0.13`: Core agent framework
- `pydantic >= 2.0.0`: Data validation
- `openai >= 1.0.0`: LLM provider (default)

## Testing

See `tests/` directory for unit and integration tests.

```bash
# Run tests
pytest orchestrator/agents/query-ambiguity-assessor/tests/
```

## License

Part of the CUBE Semantic Layer PoC project.
