# PydanticAI Agent Implementation Summary

## Overview

This document describes the implementation of the **query-ambiguity-assessor** agent, the first PydanticAI-based component in the transformation of the orchestrator into a modular, agent-based architecture.

## What Was Implemented

### 1. Query Ambiguity Assessor Agent

A standalone PydanticAI agent that implements a 6-state workflow for interpreting and clarifying user queries before constructing Cube.js API calls.

**Location**: `orchestrator/agents/query-ambiguity-assessor/`

**Key Components**:
- `agent.py` - Main agent implementation with PydanticAI
- `schemas.py` - Pydantic models for type-safe data structures
- `prompts.py` - State-specific system prompts
- `tools/` - Agent tools for metadata access and context management
- `utils/` - Utility functions (reserved for future use)

### 2. State-Based Workflow

The agent implements the following states:

1. **QUERY_ASSESSMENT** - Evaluates query clarity
2. **CLARIFICATION_REQUEST** - Asks targeted clarification questions
3. **RECEIVE_CLARIFICATION** - Processes user's clarifying response
4. **QUERY_CONFIRMATION** - Confirms interpretation with user
5. **QUERY_REJECTION_HANDLER** - Handles rejection and asks for rephrasing
6. **API_CALL_CONSTRUCTION** - Builds validated Cube.js query

### 3. Agent Tools

The agent has access to 8 tools:

**Metadata Tools**:
- `get_available_measures()` - List all available metrics
- `get_available_dimensions()` - List all grouping/filtering dimensions
- `get_time_dimensions()` - List time-based dimensions
- `validate_measure_exists()` - Check measure validity
- `validate_dimension_exists()` - Check dimension validity

**Context Tools**:
- `update_query_context()` - Store clarification information
- `get_query_context()` - Retrieve accumulated context
- `clear_query_context()` - Reset on query rejection

## Architecture Decisions

### Why PydanticAI?

1. **Type Safety**: Structured inputs/outputs with Pydantic validation
2. **Tool Integration**: Native support for agent tools
3. **State Management**: Clean state-based workflows
4. **Async Support**: Built-in async/await for efficient I/O
5. **Memory Management**: Conversation context tracking
6. **Modular Design**: Easy to test and maintain independently

### Design Principles Followed

1. **Separation of Concerns**: Agent focuses solely on ambiguity resolution
2. **Single Responsibility**: Each state handles one specific task
3. **Type Safety**: All data validated through Pydantic models
4. **Reusability**: Agent is independent and can be reused
5. **Backwards Compatibility**: Existing orchestrator continues to work

## Integration Strategy

### Phase 1: Independent Development ✅ COMPLETE

- Implement agent as standalone module
- No modifications to existing orchestrator
- Agent can be tested independently

### Phase 2: Parallel Integration (NEXT STEPS)

The agent can be integrated alongside the existing LLM client:

1. **Add agent initialization** in `orchestrator.py`:

```python
from agents.query_ambiguity_assessor import QueryAmbiguityAssessor, CubeMetadata, ConversationContext

class QueryOrchestrator:
    def __init__(self, ...):
        # Existing initialization...

        # Add agent initialization
        self.ambiguity_agent = QueryAmbiguityAssessor(
            model="openai:gpt-4o",
            api_key=openai_api_key
        )
        self.agent_sessions = {}  # Track conversation contexts
```

2. **Convert metadata** to agent format:

```python
def _prepare_cube_metadata(self) -> CubeMetadata:
    """Convert validator metadata to CubeMetadata format"""
    if self.query_validator:
        schema = self.query_validator.get_schema_summary()
        return CubeMetadata(
            view_name=schema.get('cube_name', ''),
            measures=self.metadata_fetcher.get_view_metadata('EventPerformanceOverview').get('measures', []),
            dimensions=self.metadata_fetcher.get_view_metadata('EventPerformanceOverview').get('dimensions', [])
        )
    return CubeMetadata(view_name="", measures=[], dimensions=[])
```

3. **Route queries** through agent:

```python
def process_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
    # Option 1: Use agent for all queries (recommended)
    use_agent = True

    # Option 2: Feature flag for gradual rollout
    # use_agent = os.getenv('USE_AMBIGUITY_AGENT', 'false').lower() == 'true'

    if use_agent:
        return await self._process_query_with_agent(user_query, session_id)
    else:
        return self._process_query_legacy(user_query)
```

4. **Handle agent responses**:

```python
async def _process_query_with_agent(self, user_query: str, session_id: str) -> Dict[str, Any]:
    # Get or create session context
    if session_id not in self.agent_sessions:
        self.agent_sessions[session_id] = ConversationContext(session_id=session_id)

    context = self.agent_sessions[session_id]
    cube_metadata = self._prepare_cube_metadata()

    # Call agent
    agent_response = await self.ambiguity_agent.assess_query(
        user_query=user_query,
        session_id=session_id,
        cube_metadata=cube_metadata,
        conversation_context=context
    )

    # Map agent response to orchestrator format
    if agent_response.response_type == "clarification":
        return {
            "success": True,
            "response_type": "clarification",
            "llm_response": {
                "message": agent_response.data["clarification_question"],
                "clarification_questions": [agent_response.data["clarification_question"]],
                "suggestions": agent_response.data["suggestions"]
            }
        }

    elif agent_response.response_type == "confirmation":
        return {
            "success": True,
            "response_type": "confirmation",
            "llm_response": {
                "message": agent_response.data["confirmation_message"],
                "interpreted_parameters": agent_response.data["interpreted_parameters"]
            }
        }

    elif agent_response.response_type == "cube_query":
        # Execute cube query
        cube_result = self.cube_client.execute_query(
            agent_response.data["cube_query"],
            user_query
        )

        return {
            "success": cube_result["success"],
            "response_type": "data_result",
            "llm_response": {
                "description": agent_response.data["query_description"]
            },
            "cube_data": cube_result.get("data"),
            "csv_filename": cube_result.get("csv_filename"),
            "row_count": cube_result.get("row_count")
        }

    # ... handle other response types
```

### Phase 3: Full Migration

Once the agent is proven stable:

1. Remove legacy LLM client
2. Update all endpoints to use agent
3. Remove old conversation manager
4. Clean up unused code

## Frontend Integration

The agent responses are compatible with the existing frontend:

- **Clarification requests** → Display as clarification UI (already implemented)
- **Confirmation requests** → Show "Confirm"/"Reject" buttons (needs implementation)
- **Data results** → Display table and download CSV (already implemented)

### Required Frontend Changes

1. **Add confirmation UI** in `ChatMessage.js`:

```javascript
{/* Show confirmation UI for confirmation responses */}
{message.sender === 'assistant' && message.responseType === 'confirmation' && message.data && (
  <ConfirmationContainer>
    <ConfirmationTitle>Please confirm</ConfirmationTitle>
    <ConfirmationMessage>{message.data.confirmation_message}</ConfirmationMessage>

    <ButtonGroup>
      <ConfirmButton onClick={() => handleConfirm(message.data.interpreted_parameters)}>
        ✓ Confirm
      </ConfirmButton>
      <RejectButton onClick={() => handleReject()}>
        ✗ Reject
      </RejectButton>
    </ButtonGroup>
  </ConfirmationContainer>
)}
```

2. **Handle confirmation/rejection**:

```javascript
const handleConfirm = async (interpretedParameters) => {
  // Send confirmation to backend
  const response = await axios.post('/api/query/confirm', {
    session_id: sessionId,
    confirmed_parameters: interpretedParameters
  });
  // Handle response...
};

const handleReject = async () => {
  // Send rejection to backend
  const response = await axios.post('/api/query/reject', {
    session_id: sessionId
  });
  // Handle response...
};
```

3. **Add new API endpoints** in `api_server.py`:

```python
@app.post("/query/confirm")
async def confirm_query(request: QueryConfirmRequest):
    """Handle user confirmation of query interpretation"""
    session_id = request.session_id
    confirmed_params = request.confirmed_parameters

    # Get agent response
    response = await orchestrator.ambiguity_agent.construct_api_call(
        confirmed_parameters=confirmed_params,
        original_query=orchestrator.agent_sessions[session_id].get_last_user_message(),
        cube_metadata=orchestrator._prepare_cube_metadata(),
        conversation_context=orchestrator.agent_sessions[session_id]
    )

    # Execute cube query and return results
    ...

@app.post("/query/reject")
async def reject_query(request: QueryRejectRequest):
    """Handle user rejection of query interpretation"""
    session_id = request.session_id

    # Get agent response
    response = await orchestrator.ambiguity_agent.handle_rejection(
        original_query=orchestrator.agent_sessions[session_id].get_last_user_message(),
        conversation_context=orchestrator.agent_sessions[session_id]
    )

    return QueryResponse(
        success=True,
        description=response.data["rephrasing_prompt"],
        response_type="rejection",
        data=response.data
    )
```

## Testing Strategy

### Unit Tests

Test each component independently:

```python
# Test schemas
def test_ambiguity_flags():
    flags = AmbiguityFlags(time_specification_unclear=True)
    assert flags.is_ambiguous() == True
    assert "time_specification" in flags.get_ambiguous_aspects()

# Test tools
def test_get_available_measures():
    deps = create_test_dependencies()
    result = get_available_measures(deps)
    assert result["count"] > 0
    assert "measures" in result
```

### Integration Tests

Test agent with real LLM:

```python
@pytest.mark.asyncio
async def test_agent_assessment():
    agent = QueryAmbiguityAssessor(model="openai:gpt-4o")
    metadata = create_test_metadata()

    response = await agent.assess_query(
        user_query="Show me revenue",
        session_id="test-123",
        cube_metadata=metadata
    )

    assert response.success == True
    # Expect clarification due to ambiguous time period
    assert response.response_type == "clarification"
```

### End-to-End Tests

Test full workflow:

```python
@pytest.mark.asyncio
async def test_full_clarification_workflow():
    agent = QueryAmbiguityAssessor(model="openai:gpt-4o")
    metadata = create_test_metadata()
    context = ConversationContext(session_id="test-123")

    # Step 1: Initial query
    response1 = await agent.assess_query(
        user_query="Show me revenue",
        session_id="test-123",
        cube_metadata=metadata,
        conversation_context=context
    )
    assert response1.response_type == "clarification"

    # Step 2: Provide clarification
    response2 = await agent.receive_clarification(
        user_response="Last month",
        ambiguous_aspect=response1.data["ambiguous_aspect"],
        original_query="Show me revenue",
        cube_metadata=metadata,
        conversation_context=context
    )

    # Should proceed to confirmation or query another aspect
    assert response2.success == True
```

## Benefits of This Approach

1. **No Breaking Changes**: Existing orchestrator continues to work
2. **Gradual Migration**: Can roll out agent incrementally
3. **Easy Rollback**: Can switch back to legacy if needed
4. **Better UX**: More intelligent clarification process
5. **Maintainable**: Clean separation of concerns
6. **Testable**: Each component can be tested independently
7. **Scalable**: Easy to add more agents (cube-query-validator next)

## Next Steps

1. **Test the agent** independently with various queries
2. **Implement frontend** confirmation UI
3. **Add orchestrator** integration methods
4. **Create integration tests** for the full workflow
5. **Deploy behind feature flag** for gradual rollout
6. **Monitor and iterate** based on real usage
7. **Implement cube-query-validator** agent (Phase 2)
8. **Add LangGraph** orchestration (Phase 3)

## Files Created

```
orchestrator/agents/
├── __init__.py
└── query-ambiguity-assessor/
    ├── __init__.py
    ├── README.md
    ├── agent.py               (483 lines)
    ├── schemas.py             (254 lines)
    ├── prompts.py             (297 lines)
    ├── tools/
    │   ├── __init__.py
    │   ├── metadata_tools.py  (107 lines)
    │   └── context_tools.py   (60 lines)
    └── utils/
        └── (reserved for future use)
```

**Total**: ~1,200 lines of production code

## Dependencies Added

```
pydantic-ai>=0.0.13
pydantic>=2.0.0
```

## Conclusion

The query-ambiguity-assessor agent is now fully implemented and ready for integration. It follows PydanticAI best practices, maintains type safety throughout, and provides a solid foundation for the transition to a fully agent-based architecture.

The implementation is designed for minimal disruption - the existing orchestrator continues to work while we gradually integrate the new agent-based approach.

---

**Status**: ✅ Implementation Complete
**Date**: 2025-10-21
**Agent**: Query Ambiguity Assessor v1.0
**Next**: Integration & Testing
