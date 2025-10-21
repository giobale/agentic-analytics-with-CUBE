# Query Ambiguity Assessor - Workflow Examples

This document shows real-world examples of how the agent handles different query scenarios.

## Example 1: Ambiguous Time Period

### User Query
```
"Show me total revenue"
```

### Agent Flow

**STATE 1: QUERY_ASSESSMENT**
- Input: "Show me total revenue"
- Analysis:
  - Measure: Clear (total_revenue)
  - Time period: **AMBIGUOUS** ❌
  - Grouping: Unclear (should we group by anything?)
- Output: Transition to CLARIFICATION_REQUEST

**STATE 2: CLARIFICATION_REQUEST**
- Question: "For which time period would you like to see the total revenue?"
- Suggestions:
  - "Last month"
  - "Last 7 days"
  - "This year"
  - "All time"
- Output: Wait for user response

**User responds**: "Last month"

**STATE 3: RECEIVE_CLARIFICATION**
- Input: "Last month"
- Extraction: time_period = "last month"
- Update context: `{"time_period": "last month"}`
- Output: Transition back to QUERY_ASSESSMENT

**STATE 1: QUERY_ASSESSMENT** (second pass)
- Input: Original query + context
- Analysis:
  - Measure: Clear (total_revenue)
  - Time period: Clear (last month) ✅
  - Grouping: Still unclear
- Output: Transition to CLARIFICATION_REQUEST

**STATE 2: CLARIFICATION_REQUEST** (second clarification)
- Question: "Would you like to see total revenue grouped by any dimension?"
- Suggestions:
  - "By event"
  - "By day"
  - "Overall total (no grouping)"
- Output: Wait for user response

**User responds**: "Overall total"

**STATE 3: RECEIVE_CLARIFICATION**
- Input: "Overall total"
- Extraction: grouping = null
- Update context: `{"time_period": "last month", "grouping": null}`
- Output: Transition to QUERY_CONFIRMATION

**STATE 4: QUERY_CONFIRMATION**
- Message: "I'll show you the total revenue for last month with no grouping. Is this correct?"
- Parameters:
  ```json
  {
    "measures": ["total_revenue"],
    "dimensions": [],
    "time_period": "last month",
    "grouping": null
  }
  ```
- Output: Wait for confirmation

**User clicks**: "Confirm" ✓

**STATE 6: API_CALL_CONSTRUCTION**
- Cube Query:
  ```json
  {
    "measures": ["EventPerformanceOverview.totalRevenue"],
    "dimensions": [],
    "timeDimensions": [
      {
        "dimension": "EventPerformanceOverview.orderDate",
        "granularity": null,
        "dateRange": "last month"
      }
    ]
  }
  ```
- Output: Ready for execution

---

## Example 2: Clear Query

### User Query
```
"Show me daily ticket sales by event for the last 7 days"
```

### Agent Flow

**STATE 1: QUERY_ASSESSMENT**
- Input: "Show me daily ticket sales by event for the last 7 days"
- Analysis:
  - Measure: Clear (ticket sales) ✅
  - Time period: Clear (last 7 days) ✅
  - Grouping: Clear (by event, daily) ✅
  - All parameters present!
- Output: Transition to QUERY_CONFIRMATION

**STATE 4: QUERY_CONFIRMATION**
- Message: "I'll show you daily ticket sales grouped by event for the last 7 days. Is this correct?"
- Parameters:
  ```json
  {
    "measures": ["ticket_count"],
    "dimensions": ["event_name"],
    "time_period": "last 7 days",
    "grouping": "daily"
  }
  ```
- Output: Wait for confirmation

**User clicks**: "Confirm" ✓

**STATE 6: API_CALL_CONSTRUCTION**
- Cube Query:
  ```json
  {
    "measures": ["EventPerformanceOverview.ticketsSold"],
    "dimensions": ["EventPerformanceOverview.eventName"],
    "timeDimensions": [
      {
        "dimension": "EventPerformanceOverview.orderDate",
        "granularity": "day",
        "dateRange": "last 7 days"
      }
    ],
    "order": {
      "EventPerformanceOverview.orderDate": "asc"
    }
  }
  ```
- Output: Ready for execution

---

## Example 3: Query Rejection

### User Query
```
"Show me revenue trends"
```

### Agent Flow

**STATE 1: QUERY_ASSESSMENT**
- Input: "Show me revenue trends"
- Analysis:
  - Measure: Clear (revenue) ✅
  - Time period: AMBIGUOUS ❌
  - Grouping: AMBIGUOUS (what granularity for trends?) ❌
- Output: Transition to CLARIFICATION_REQUEST

**STATE 2: CLARIFICATION_REQUEST**
- Question: "What time period would you like to analyze for revenue trends?"
- Suggestions: ["Last month", "Last quarter", "This year", "Last 12 months"]
- Output: Wait for response

**User responds**: "This year"

**STATE 3: RECEIVE_CLARIFICATION**
- Update context: `{"time_period": "this year"}`
- Output: Back to QUERY_ASSESSMENT

**STATE 1: QUERY_ASSESSMENT**
- Analysis:
  - Measure: Clear ✅
  - Time period: Clear ✅
  - Grouping: Still AMBIGUOUS ❌
- Output: Transition to CLARIFICATION_REQUEST

**STATE 2: CLARIFICATION_REQUEST**
- Question: "What granularity would you like for the revenue trends?"
- Suggestions: ["Daily", "Weekly", "Monthly"]
- Output: Wait for response

**User responds**: "Monthly"

**STATE 3: RECEIVE_CLARIFICATION**
- Update context: `{"time_period": "this year", "grouping": "monthly"}`
- Output: Transition to QUERY_CONFIRMATION

**STATE 4: QUERY_CONFIRMATION**
- Message: "I'll show you monthly revenue trends for this year. Is this correct?"
- Parameters: {...}
- Output: Wait for confirmation

**User clicks**: "Reject" ✗

**STATE 5: QUERY_REJECTION_HANDLER**
- Message: "I apologize for misunderstanding. Could you please rephrase your query or provide more details about what you'd like to see?"
- Action: Clear query context
- Output: Reset to initial state

**User provides new query**: "Show me total revenue by event for Q4 2024"

*[Process starts fresh from STATE 1]*

---

## Example 4: Multiple Filters

### User Query
```
"Show me revenue for Rock concerts in Paris last month"
```

### Agent Flow

**STATE 1: QUERY_ASSESSMENT**
- Input: "Show me revenue for Rock concerts in Paris last month"
- Analysis:
  - Measure: Clear (revenue) ✅
  - Time period: Clear (last month) ✅
  - Filters detected:
    - Event category: "Rock" ✅
    - Location: "Paris" ⚠️ (dimension might not exist)
  - Grouping: Unclear
- Output: Transition to CLARIFICATION_REQUEST

**STATE 2: CLARIFICATION_REQUEST**
- Question: "I notice you mentioned Paris. Unfortunately, we don't have location data in this dataset. Would you still like to proceed with just Rock concerts?"
- Suggestions: ["Yes, show Rock concerts only", "Cancel"]
- Output: Wait for response

**User responds**: "Yes, show Rock concerts only"

**STATE 3: RECEIVE_CLARIFICATION**
- Update context: Remove Paris filter, keep Rock category
- Output: Transition to QUERY_CONFIRMATION

**STATE 4: QUERY_CONFIRMATION**
- Message: "I'll show you revenue for Rock concerts for last month. Is this correct?"
- Parameters:
  ```json
  {
    "measures": ["total_revenue"],
    "filters": [
      {
        "member": "event_category",
        "operator": "equals",
        "values": ["Rock"]
      }
    ],
    "time_period": "last month"
  }
  ```
- Output: Wait for confirmation

**User clicks**: "Confirm" ✓

**STATE 6: API_CALL_CONSTRUCTION**
- Cube Query:
  ```json
  {
    "measures": ["EventPerformanceOverview.totalRevenue"],
    "dimensions": [],
    "timeDimensions": [
      {
        "dimension": "EventPerformanceOverview.orderDate",
        "dateRange": "last month"
      }
    ],
    "filters": [
      {
        "member": "EventPerformanceOverview.eventCategory",
        "operator": "equals",
        "values": ["Rock"]
      }
    ]
  }
  ```
- Output: Ready for execution

---

## Key Patterns

### Pattern 1: Progressive Clarification
The agent addresses **ONE ambiguity at a time** to avoid overwhelming users.

### Pattern 2: Context Accumulation
Each clarification builds on previous ones, maintaining context throughout the session.

### Pattern 3: Validation
The agent validates all measures/dimensions against cube metadata before confirming.

### Pattern 4: User Control
Users have final say through confirmation - the agent never assumes.

### Pattern 5: Graceful Degradation
When filters reference unavailable data, the agent suggests alternatives rather than failing.

---

## Response Type Summary

| State | Response Type | Frontend Action |
|-------|---------------|-----------------|
| CLARIFICATION_REQUEST | `clarification` | Show question + suggestions |
| QUERY_CONFIRMATION | `confirmation` | Show Confirm/Reject buttons |
| API_CALL_CONSTRUCTION | `cube_query` | Execute query & show results |
| QUERY_REJECTION_HANDLER | `rejection` | Show rephrasing prompt |
| ERROR | `error` | Show error message |

---

## Testing These Scenarios

Use the test script from `QUICK_START_PYDANTIC_AGENT.md` and modify the queries to match these examples. You should see similar workflows.
