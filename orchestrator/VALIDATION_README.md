# Cube Query Validation System

## Overview

The Cube Query Validation System ensures that all parameters in LLM-generated Cube.js queries exist in your cube schema before execution. This prevents runtime errors and automatically asks the LLM to fix invalid parameters.

## Architecture

The validation system consists of three main components:

### 1. **CubeQueryValidator** (`cube_query_validator.py`)
Parses the cube/view YML schema and validates query parameters against it.

**Features:**
- Extracts available measures, dimensions, and time dimensions from YML files
- Validates measures, dimensions, and time dimensions in queries
- Provides intelligent suggestions using Levenshtein distance
- Generates correction prompts for the LLM with detailed error information

### 2. **Orchestrator Integration** (`orchestrator.py`)
Integrates validation into the query processing pipeline with automatic retry logic.

**Workflow:**
```
User Query → LLM → Query Validation → Execute or Retry
                          ↓
                    If Invalid → Generate Correction Prompt → LLM Retry → Validate Again
```

### 3. **Test Suite** (`tests/test_cube_validation.py`)
Comprehensive tests verifying validator functionality.

## How It Works

### Query Processing Flow

1. **User submits natural language query**
   ```
   "Show me daily tickets sold last month"
   ```

2. **LLM generates Cube.js query**
   ```json
   {
     "measures": ["EventPerformanceOverview.total_tickets_sold"],
     "timeDimensions": [{
       "dimension": "EventPerformanceOverview.start_date",
       "granularity": "day"
     }]
   }
   ```

3. **Validator checks parameters**
   - Loads schema from YML file
   - Checks if `total_tickets_sold` exists (it doesn't - should be `tickets_sold`)
   - Checks if `start_date` exists (it doesn't - should be `order_date`)

4. **Validation fails - Generate correction prompt**
   ```
   Your previous cube query contained invalid parameters for the 'FactOrders' cube.

   Errors found:
     - Measure 'EventPerformanceOverview.total_tickets_sold' does not exist
     - Time dimension 'EventPerformanceOverview.start_date' does not exist

   Available measures: tickets_sold, revenues, orders_count, ...
   Available time dimensions: order_date

   Please regenerate the cube query using ONLY the available parameters.
   ```

5. **LLM generates corrected query**
   ```json
   {
     "measures": ["FactOrders.tickets_sold"],
     "timeDimensions": [{
       "dimension": "FactOrders.order_date",
       "granularity": "day"
     }]
   }
   ```

6. **Validator passes - Query executes successfully**

## Configuration

### Orchestrator Initialization

```python
from orchestrator import QueryOrchestrator

orchestrator = QueryOrchestrator(
    openai_api_key="your-key",
    cube_base_url="http://localhost:4000",
    cube_api_secret="your-secret",
    view_yml_path="/path/to/view.yml",  # Optional: auto-detects if not provided
    max_validation_retries=2  # Maximum LLM retry attempts (default: 2)
)
```

### View YML Path

The validator needs a path to your cube/view YML file. By default, it looks for:
```
orchestrator/system-prompt-generator/my-cube-views/event_performance_overview.yml
```

You can override this by passing `view_yml_path` to the orchestrator.

## Usage Examples

### Standalone Validator Usage

```python
from cube_query_validator import CubeQueryValidator

# Initialize validator
validator = CubeQueryValidator("path/to/view.yml")

# Get schema summary
summary = validator.get_schema_summary()
print(f"Available measures: {summary['measures']}")
print(f"Available dimensions: {summary['dimensions']}")

# Validate a query
query = {
    "measures": ["FactOrders.tickets_sold"],
    "dimensions": ["FactOrders.order_date"]
}

result = validator.validate_query(query)

if result['valid']:
    print("✓ Query is valid")
else:
    print("✗ Query has errors:")
    for error in result['errors']:
        print(f"  - {error}")

    # Get suggestions
    if result['suggestions']:
        print("\nSuggested corrections:")
        for invalid, suggestion in result['suggestions'].items():
            print(f"  Replace '{invalid}' with '{suggestion}'")
```

### With Orchestrator (Automatic)

```python
from orchestrator import QueryOrchestrator

orchestrator = QueryOrchestrator()
orchestrator.initialize()

# Validation happens automatically during query processing
result = orchestrator.process_query("Show me daily tickets sold")

# Check validation attempts in result
if result['success']:
    print(f"Query succeeded after {result.get('validation_attempts', 1)} attempt(s)")
```

## Validation Details

### What Gets Validated

1. **Measures**: All items in `query['measures']` list
2. **Dimensions**: All items in `query['dimensions']` list
3. **Time Dimensions**: All `dimension` fields in `query['timeDimensions']` array
4. **Filters** *(warning only)*: Filter members are checked but only generate warnings

### Field Name Extraction

The validator handles fully qualified names:
- `"EventPerformanceOverview.tickets_sold"` → extracts `"tickets_sold"`
- `"FactOrders.order_date"` → extracts `"order_date"`

### Intelligent Suggestions

When a parameter doesn't exist, the validator uses Levenshtein distance to find the closest match:

```python
Invalid: "total_tickets_sold"
Suggestion: "tickets_sold" (distance: 6)

Invalid: "order_dat"
Suggestion: "order_date" (distance: 1)
```

Maximum edit distance for suggestions: 3

## Testing

### Run the Test Suite

```bash
cd orchestrator
./venv/bin/python tests/test_cube_validation.py
```

### Test Coverage

The test suite includes:

1. **Validator Initialization** - Verifies YML parsing works
2. **Valid Query** - Confirms valid queries pass validation
3. **Invalid Measure Detection** - Tests error detection for wrong measures
4. **Correction Prompt Generation** - Verifies correction prompts are well-formed
5. **Mixed Valid/Invalid** - Tests queries with both valid and invalid parameters

### Expected Output

```
╔====================================================================╗
║               CUBE QUERY VALIDATOR TEST SUITE                     ║
╚====================================================================╝

✓ All tests passed!
```

## Error Handling

### Validation Errors

**Error**: Query parameter not found
```json
{
  "valid": false,
  "errors": [
    "Measure 'invalid_measure' does not exist in cube 'FactOrders'"
  ],
  "invalid_measures": ["invalid_measure"],
  "suggestions": {
    "invalid_measure": "FactOrders.tickets_sold"
  }
}
```

### Initialization Errors

**Error**: YML file not found
```python
CubeQueryValidatorError: "File not found: /path/to/view.yml"
```

**Solution**: Verify the view YML path is correct

**Error**: Invalid YML syntax
```python
CubeQueryValidatorError: "YAML parsing error: ..."
```

**Solution**: Check your YML file for syntax errors

## Retry Logic

The orchestrator implements automatic retry logic:

### Retry Behavior

- **Max retries**: 2 (configurable via `max_validation_retries`)
- **Retry trigger**: Validation fails OR Cube.js returns "not found" error
- **Retry process**:
  1. Generate detailed correction prompt
  2. Send to LLM with fresh context
  3. Validate corrected query
  4. Execute if valid, otherwise retry or fail

### Retry Tracking

Query results include validation metadata:

```json
{
  "success": true,
  "validation_attempts": 2,
  "pipeline_steps": {
    "validation_attempt_1": {...},
    "llm_correction_attempt_1": {...},
    "validation_attempt_2": {...},
    "cube_execution": {...}
  }
}
```

## Best Practices

### 1. Keep View YML in Sync

**Always sync your view YML files:**
- When adding new measures/dimensions to cubes
- When renaming existing fields
- When changing cube structure

### 2. Use Descriptive Names

The validator works best with clear, consistent naming:

✓ **Good**: `tickets_sold`, `order_date`, `total_revenue`
✗ **Bad**: `ts`, `od`, `tr`

### 3. Monitor Validation Failures

Track validation failure rates:
```python
result = orchestrator.process_query(user_query)
attempts = result.get('validation_attempts', 1)

if attempts > 1:
    logger.warning(f"Query required {attempts} validation attempts")
```

### 4. Update System Prompts

Ensure your system prompts include:
- Complete list of available measures
- Complete list of available dimensions
- Clear naming conventions
- Example queries

## Troubleshooting

### Issue: Validator always fails even with correct parameters

**Cause**: View YML path is incorrect or points to wrong file

**Solution**:
```python
validator = CubeQueryValidator("/correct/path/to/view.yml")
summary = validator.get_schema_summary()
print(summary)  # Verify measures and dimensions are loaded
```

### Issue: LLM keeps generating invalid queries

**Cause**: System prompt doesn't contain schema information or contains outdated info

**Solution**:
1. Regenerate system prompt cache:
   ```python
   orchestrator.regenerate_system_prompt()
   ```

2. Verify schema in system prompt:
   ```bash
   cat /app/cache/system_prompt.txt
   ```

### Issue: Valid parameters marked as invalid

**Cause**: View YML doesn't match actual cube definition in `cube-core/model/`

**Solution**:
1. Check if you have duplicate cube definitions
2. Ensure view YML is synced with cube YML
3. Verify the cube name matches

## Integration with Docker

The validation system works seamlessly in Docker:

### docker-compose.yml
```yaml
services:
  query-orchestrator:
    volumes:
      - ./orchestrator:/app
      - ./cube-core/model/views:/app/system-prompt-generator/my-cube-views
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Verification

Check validation is working:
```bash
docker-compose logs query-orchestrator | grep "validation"
```

Look for:
```
⚠️  Query validation failed (attempt 1), asking LLM to correct...
✓ Query validated successfully
```

## Future Enhancements

Potential improvements to the validation system:

1. **Multi-cube validation**: Support queries spanning multiple cubes
2. **Filter validation**: Upgrade filter checks from warnings to errors
3. **Value validation**: Validate filter values against dimension domains
4. **Performance caching**: Cache parsed schemas to reduce YML reads
5. **Validation metrics**: Track validation success rates and common errors

## API Reference

### CubeQueryValidator

```python
class CubeQueryValidator:
    def __init__(self, view_yml_path: str)
    def validate_query(self, cube_query: Dict[str, Any]) -> Dict[str, Any]
    def get_schema_summary(self) -> Dict[str, Any]
    def generate_correction_prompt(self, validation_result: Dict, original_query: str) -> str
```

### Validation Result

```python
{
    "valid": bool,
    "errors": List[str],
    "warnings": List[str],
    "invalid_measures": List[str],
    "invalid_dimensions": List[str],
    "invalid_time_dimensions": List[str],
    "suggestions": Dict[str, str]  # {invalid: suggested}
}
```

## License

This validation system is part of the PoC-V1-CUBE-Semantic-Layer project.

## Support

For issues or questions:
1. Check the test suite: `tests/test_cube_validation.py`
2. Review validation logs in Docker: `docker-compose logs query-orchestrator`
3. Verify YML file structure matches expectations
