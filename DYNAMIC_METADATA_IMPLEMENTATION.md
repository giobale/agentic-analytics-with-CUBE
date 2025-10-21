# Dynamic Metadata Implementation

## Overview

This document describes the implementation of dynamic metadata fetching from Cube.js API, replacing the static YAML-based approach with real-time metadata retrieval.

## Architecture

### Components

1. **CubeMetadataFetcher** (`orchestrator/cube_metadata_fetcher.py`)
   - Fetches metadata from Cube.js `/v1/meta` API endpoint
   - Caches metadata to disk for performance
   - Provides structured access to views, measures, and dimensions

2. **ContextManager** (`orchestrator/system-prompt-generator/context_preparation/context_manager.py`)
   - Updated to support both dynamic metadata and static YAML fallback
   - Converts Cube API metadata to system prompt format
   - Maintains backward compatibility

3. **QueryOrchestrator** (`orchestrator/orchestrator.py`)
   - Initializes metadata fetcher on startup
   - Provides `/refresh-metadata` endpoint for manual refresh
   - Updates system prompt and query validator when metadata refreshes

4. **CubeQueryValidator** (`orchestrator/cube_query_validator.py`)
   - Updated to accept either YAML path or metadata dictionary
   - Validates queries against dynamic or static schema

5. **Frontend Refresh Button** (`chat-frontend/src/components/Header.js`)
   - User-facing button to trigger metadata refresh
   - Visual feedback during refresh operation

## Features

### ✅ Dynamic Metadata Fetching
- Fetches cube/view metadata from Cube.js API at `/v1/meta`
- Extracts measures, dimensions, and descriptions
- No container rebuild needed when Cube model changes

### ✅ Smart Caching
- Metadata cached to disk on first fetch
- Loaded from cache on subsequent startups
- Manual refresh via button/API endpoint

### ✅ Fallback Strategy
- Tries dynamic metadata first
- Falls back to static YAML if API unavailable
- Graceful degradation ensures system always works

### ✅ Manual Refresh
- Frontend button: "Refresh Context" in header
- API endpoint: `POST /refresh-metadata`
- Refreshes: metadata cache, system prompt, query validator

## Usage

### For Users

1. **Automatic on Startup**: Orchestrator fetches metadata from Cube API on initialization
2. **Manual Refresh**: Click "Refresh Context" button in the frontend header after updating Cube models
3. **No Rebuild Required**: Changes to Cube models are reflected immediately after refresh

### For Developers

#### Enable/Disable Dynamic Metadata

```python
orchestrator = QueryOrchestrator(
    use_dynamic_metadata=True,  # Set to False to use static YAML
    # ... other params
)
```

#### API Endpoint

```bash
# Trigger metadata refresh
curl -X POST http://localhost:8080/refresh-metadata
```

Response:
```json
{
  "success": true,
  "message": "Cube metadata refreshed successfully",
  "metadata_summary": {
    "total_cubes": 5,
    "views_count": 1,
    "cubes_count": 4,
    "view_names": ["EventPerformanceOverview"],
    "timestamp": "2025-01-20T10:30:00"
  },
  "system_prompt_metadata": {
    "views_count": 1,
    "examples_count": 5,
    "generation_timestamp": "2025-01-20T10:30:00"
  },
  "timestamp": "2025-01-20T10:30:00"
}
```

## Implementation Details

### Metadata Fetching Workflow

```
1. Orchestrator initializes
   ↓
2. CubeClient gets JWT token
   ↓
3. CubeMetadataFetcher initialized with JWT
   ↓
4. Fetch metadata from /v1/meta (or load from cache)
   ↓
5. ContextManager uses metadata to generate system prompt
   ↓
6. CubeQueryValidator initialized with metadata
   ↓
7. System ready for queries
```

### Refresh Workflow

```
User clicks "Refresh Context" button
   ↓
Frontend calls POST /refresh-metadata
   ↓
Orchestrator clears metadata cache
   ↓
Fetches fresh metadata from Cube API
   ↓
Regenerates system prompt
   ↓
Updates query validator
   ↓
Saves to cache
   ↓
Returns success response
```

### Metadata Format

**Cube API Response** (`/v1/meta`):
```json
{
  "cubes": [
    {
      "name": "EventPerformanceOverview",
      "title": "Event Performance Overview",
      "type": "view",
      "measures": [
        {
          "name": "EventPerformanceOverview.revenues",
          "title": "Revenues",
          "description": "Total revenue from orders"
        }
      ],
      "dimensions": [
        {
          "name": "EventPerformanceOverview.event_name",
          "title": "Event Name",
          "description": "Name of the event"
        }
      ]
    }
  ]
}
```

**Converted Format** (for ContextManager):
```python
{
  'name': 'EventPerformanceOverview',
  'title': 'Event Performance Overview',
  'description': 'KPIs and attributes...',
  'type': 'view',
  'measures': [
    {
      'name': 'revenues',
      'title': 'Revenues',
      'description': 'Total revenue from orders'
    }
  ],
  'dimensions': [
    {
      'name': 'event_name',
      'title': 'Event Name',
      'description': 'Name of the event'
    }
  ]
}
```

## Configuration

### Environment Variables

```bash
# Enable/disable dynamic metadata (default: true)
USE_DYNAMIC_METADATA=true

# Cache directory
CACHE_DIR=/app/cache

# Cube API connection
CUBE_BASE_URL=http://cube:4000
CUBEJS_API_SECRET=your_secret
```

### Docker Compose

The orchestrator service automatically uses dynamic metadata by default:

```yaml
orchestrator:
  environment:
    CUBE_BASE_URL: http://cube:4000
    CUBEJS_API_SECRET: ${CUBEJS_API_SECRET:-baubeach}
    CACHE_DIR: /app/cache
```

## File Structure

```
orchestrator/
├── cube_metadata_fetcher.py          # NEW: Metadata fetcher
├── orchestrator.py                   # UPDATED: Integration
├── cube_query_validator.py           # UPDATED: Dynamic metadata support
├── api_server.py                     # UPDATED: Refresh endpoint
└── system-prompt-generator/
    └── context_preparation/
        └── context_manager.py        # UPDATED: Dynamic metadata support

chat-frontend/
└── src/
    └── components/
        └── Header.js                 # UPDATED: Refresh button
```

## Benefits

1. **No Rebuild Required**: Cube model changes reflect immediately after refresh
2. **Always in Sync**: Guaranteed consistency between Cube model and orchestrator
3. **Better Performance**: Cached metadata, fetched only when needed
4. **Graceful Degradation**: Falls back to static YAML if API unavailable
5. **User Control**: Manual refresh via frontend button
6. **Developer Friendly**: Simple API endpoint for automation

## Testing

### Manual Testing

1. **Start the system**:
   ```bash
   docker-compose up -d
   ```

2. **Verify dynamic metadata is loaded**:
   ```bash
   docker logs query-orchestrator | grep "Metadata fetched"
   # Should show: ✅ Metadata fetched from api (or cache)
   ```

3. **Update a Cube model**:
   - Edit `cube-core/model/cubes/fact_orders.yml`
   - Add or modify a measure/dimension

4. **Refresh via frontend**:
   - Open chat frontend
   - Click "Refresh Context" button
   - Should show "✅ Context refreshed!"

5. **Refresh via API**:
   ```bash
   curl -X POST http://localhost:8080/refresh-metadata
   ```

6. **Query with new fields**:
   - Ask a question using the new measure/dimension
   - Should work without container restart

### Automated Testing

Run Docker builds to verify no syntax errors:
```bash
docker-compose build orchestrator chat-frontend
```

## Troubleshooting

### Metadata fetch fails on startup

**Symptom**: `⚠️ Metadata fetch failed, will use static YAML fallback`

**Causes**:
- Cube API not accessible
- Invalid JWT token
- Network issues

**Solution**: System automatically falls back to static YAML. Check Cube service health.

### Refresh button shows error

**Symptom**: `❌ Refresh failed` or `❌ Connection error`

**Causes**:
- Orchestrator not running
- Cube API unavailable
- Dynamic metadata disabled

**Solution**:
1. Check orchestrator logs: `docker logs query-orchestrator`
2. Verify Cube is running: `docker logs cube-semantic-layer`
3. Check `USE_DYNAMIC_METADATA` environment variable

### Queries fail after model update

**Symptom**: Validation errors for newly added fields

**Cause**: Metadata not refreshed after model update

**Solution**: Click "Refresh Context" button in frontend

## Future Enhancements

- [ ] Auto-refresh on Cube model changes (webhooks)
- [ ] TTL-based automatic refresh
- [ ] Multi-view support in validator
- [ ] Metadata version tracking
- [ ] Diff view for metadata changes

## Migration Notes

### From Static YAML to Dynamic Metadata

The system maintains **full backward compatibility**:

1. **Static YAML still works**: Set `use_dynamic_metadata=False`
2. **Automatic fallback**: If API fails, uses YAML
3. **No data loss**: Existing YAML files remain unchanged
4. **Gradual adoption**: Can test dynamic metadata while keeping YAML as backup

To disable dynamic metadata:
```python
# In api_server.py startup
orchestrator = QueryOrchestrator(
    use_dynamic_metadata=False  # Use static YAML
)
```

## Summary

This implementation provides a robust, performant, and user-friendly solution for keeping the orchestrator in sync with Cube model changes. The hybrid approach (dynamic with static fallback) ensures reliability while the manual refresh gives users full control.

---

**Implementation Date**: January 2025
**Version**: 1.0
**Status**: ✅ Production Ready
