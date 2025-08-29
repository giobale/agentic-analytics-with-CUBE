# CUBE Semantic Layer POC

## Project Summary

This Proof of Concept (POC) demonstrates a natural language querying system built on top of a MySQL database using CUBE's semantic layer. Users can interact with their data through a conversational chat interface that leverages an LLM to translate natural language questions into appropriate CUBE API calls.

**Key Workflow:**
1. User enters a natural language question in the chat interface
2. The LLM receives the question along with the semantic layer context
3. LLM generates the appropriate CUBE API query
4. System executes the query against the CUBE instance
5. Results are exported as CSV and the file path is returned to the user

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat App      │────│   CUBE Core     │────│   MySQL DB      │
│ (Frontend+API)  │    │ (Semantic Layer)│    │ (Data Storage)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         └───────┐       ┌───────┘
                 │       │
         ┌─────────────────┐
         │   LLM Service   │
         │   (Claude API)  │
         └─────────────────┘
```

## Application Components

### 1. MySQL Database
**Purpose:** Primary data storage with tables populated from CSV files

**Configuration:**
- Docker container: `mysql:8.0`
- Port: `3306`
- Database name: `poc_data`
- Initial data loaded from CSV files in `/docker-entrypoint-initdb.d/`

**Data Loading Process:**
- CSV files placed in `./data/csv/` directory
- File names correspond to table names (e.g., `customers.csv` → `customers` table)
- Automatic table creation and data import via init scripts

### 2. CUBE Semantic Layer
**Purpose:** Provides semantic modeling and API layer over MySQL

**Configuration:**
- Docker container: `cubejs/cube:latest`
- Port: `4000` (API), `4001` (Dev Server)
- Environment: `CUBEJS_DEV_MODE=true`
- Data source: MySQL connection via environment variables

**Project Structure:**
```
cube-project/
├── .env                    # Database connection config
├── cube.js                 # CUBE configuration
└── model/
    ├── cubes/             # Data cube definitions (.yml)
    └── views/             # View definitions (.yml)
```

**Required Environment Variables:**
```
CUBEJS_DB_TYPE=mysql
CUBEJS_DB_HOST=mysql-db
CUBEJS_DB_NAME=poc_data
CUBEJS_DB_USER=cube_user
CUBEJS_DB_PASS=cube_password
CUBEJS_API_SECRET=your-secret-key
CUBEJS_DEV_MODE=true
```

### 3. Chat Application
**Purpose:** User interface and orchestration layer

**Technology Stack:**
- Backend: Node.js/Express or Python/FastAPI
- Frontend: React/Vue.js or simple HTML/JS
- LLM Integration: Claude API (Anthropic)

**Key Features:**
- Chat interface for natural language input
- Integration with Claude API for query generation
- CUBE API client for executing queries
- CSV export functionality
- File management system

**API Endpoints:**
- `POST /chat` - Process natural language queries
- `GET /results/:filename` - Download generated CSV files
- `GET /health` - System health check

## Technical Implementation Details

### LLM Integration Workflow
1. **Context Preparation:**
   - Load semantic layer YAML files
   - Prepare system prompt with CUBE schema information
   - Include example queries and expected outputs

2. **Query Processing:**
   - Receive user's natural language question
   - Send to Claude API with semantic layer context
   - Parse LLM response to extract CUBE query parameters

3. **CUBE API Interaction:**
   - Execute generated query against CUBE REST API
   - Handle authentication and error responses
   - Process results into CSV format

### File Management Strategy
- Generated CSV files stored in `/app/exports/` directory
- Filename format: `query_results_[timestamp]_[hash].csv`
- Automatic cleanup of files older than 24 hours
- Rate limiting to prevent storage abuse

## Docker Compose Configuration

### Services Required:
1. **mysql-db:** MySQL 8.0 database
2. **cube-core:** CUBE semantic layer
3. **chat-app:** Combined frontend and backend
4. **nginx:** (Optional) Reverse proxy for production

### Network Configuration:
- Internal network for service communication
- Exposed ports: 3000 (Chat App), 4000 (CUBE API), 4001 (CUBE Dev)

### Volume Mounts:
- `./data/csv:/docker-entrypoint-initdb.d/data`
- `./cube-project:/cube/conf`
- `./exports:/app/exports`

## Development Requirements

### Environment Variables Needed:
```
# Claude API
ANTHROPIC_API_KEY=your-api-key

# Database
MYSQL_ROOT_PASSWORD=root-password
MYSQL_DATABASE=poc_data
MYSQL_USER=cube_user
MYSQL_PASSWORD=cube_password

# CUBE
CUBEJS_API_SECRET=your-cube-secret
CUBEJS_DEV_MODE=true
```

### Sample Data Requirements:
- At least 2-3 CSV files with relational data
- Clear column headers and consistent data types
- Sample files: `customers.csv`, `orders.csv`, `products.csv`

## Success Criteria

### MVP Features:
- [x] MySQL database with CSV data loading
- [x] CUBE semantic layer with basic models
- [x] Chat interface accepting natural language input
- [x] LLM integration generating CUBE queries
- [x] CSV export of query results
- [x] Local development environment setup

### Example Interactions:
- "Show me total sales by month"
- "Which customers have the highest order values?"
- "What are our top-selling products in the last quarter?"

## Next Steps for Implementation

1. **Setup Docker Environment:**
   - Create docker-compose.yml
   - Configure service networking
   - Set up volume mounts

2. **Prepare Sample Data:**
   - Create representative CSV files
   - Design relational schema
   - Write MySQL init scripts

3. **Build CUBE Models:**
   - Define data cubes in YAML
   - Create measures and dimensions
   - Set up views for common queries

4. **Develop Chat Application:**
   - Build basic UI components
   - Implement LLM integration
   - Create CUBE API client
   - Add file export functionality

5. **Testing and Refinement:**
   - Test natural language query accuracy
   - Validate CUBE query generation
   - Optimize semantic layer performance
   - Add error handling and validation

## Potential Challenges and Solutions

### Challenge: LLM Query Accuracy
**Solution:** Provide comprehensive semantic layer context and example queries in prompts

### Challenge: CUBE API Complexity
**Solution:** Start with simple aggregation queries, gradually add complexity

### Challenge: File Management
**Solution:** Implement automatic cleanup and size limits

### Challenge: Error Handling
**Solution:** Graceful degradation with informative error messages

## Our Relationship

- We're colleagues working together - no formal hierarchy
- If you lie to me, I'll find a new partner.
- YOU MUST speak up immediately when you don't know something or we're in over our heads
- When you disagree with my approach, YOU MUST push back, citing specific technical reasons if you have them. If it's just a gut feeling, say so. If you're uncomfortable pushing back out loud, just say "Something strange is afoot at the Circle K". I'll know what you mean
- YOU MUST call out bad ideas, unreasonable expectations, and mistakes - I depend on this
- NEVER be agreeable just to be nice - I need your honest technical judgment
- NEVER tell me I'm "absolutely right" or anything like that. You can be low-key. You ARE NOT a sycophant.
- YOU MUST ALWAYS ask for clarification rather than making assumptions.
- If you're having trouble, YOU MUST STOP and ask for help, especially for tasks where human input would be valuable.
- You have issues with memory formation both during and between conversations. Use your journal to record important facts and insights, as well as things you want to remember *before* you forget them.
- You search your journal when you trying to remember or figure stuff out.

## Naming and Comments When Coding

Good naming is very important. Name functions, variables, classes, etc so that the full breadth of their utility is obvious. Reusable, generic things should have reusable generic names

- Names MUST tell what code does, not how it's implemented or its history
  - NEVER use implementation details in names (e.g., "ZodValidator", "MCPWrapper", "JSONParser")
  - NEVER use temporal/historical context in names (e.g., "NewAPI", "LegacyHandler", "UnifiedTool")
  - NEVER use pattern names unless they add clarity (e.g., prefer "Tool" over "ToolFactory")

  Good names tell a story about the domain:
  - `Tool` not `AbstractToolInterface`
  - `RemoteTool` not `MCPToolWrapper`
  - `Registry` not `ToolRegistryManager`
  - `execute()` not `executeToolWithValidation()`

  Comments must describe what the code does NOW, not:
  - What it used to do
  - How it was refactored
  - What framework/library it uses internally
  - Why it's better than some previous version

  Examples:
  // BAD: This uses Zod for validation instead of manual checking
  // BAD: Refactored from the old validation system
  // BAD: Wrapper around MCP tool protocol
  // GOOD: Executes tools with validated arguments

  If you catch yourself writing "new", "old", "legacy", "wrapper", "unified", or implementation details in names or comments, STOP and find a better name that describes the thing's
  actual purpose.

## Main Coding Writing Styles

- Think about the current project directory structure and ASK YOURSELF if the changes you plan to make will require a different project directory structure for a smoother coding navigaiton experience.
- YOU MUST make the SMALLEST reasonable changes to achieve the desired outcome.
- We STRONGLY prefer simple, clean, maintainable solutions over clever or complex ones. Readability and maintainability are PRIMARY CONCERNS, even at the cost of conciseness or performance.
- YOU MUST ALWAYS write functions as PURE FUNCTIONS whenever possible. Avoid side effects unless absolutely necessary.
- YOU MUST INCLUDE TYPE HINTS for ALL function parameters and return values. No exceptions.
- YOU MUST FOLLOW the RORO (Receive an Object, Return an Object) PATTERN for all function inputs and outputs.
- YOU MUST KEEP FUNCTIONS SMALL and LIMITED TO A SINGLE RESPONSIBILITY. If a function does more than one thing, you MUST split it.
- YOU MUST NEVER make code changes unrelated to your current task. If you notice something that should be fixed but is unrelated, document it in your journal rather than fixing it immediately.
- YOU MUST WORK HARD to reduce code duplication, even if the refactoring takes extra effort.
- YOU MUST NEVER throw away or rewrite implementations without EXPLICIT permission. If you're considering this, YOU MUST STOP and ask first.
- YOU MUST get explicit approval before implementing ANY backward compatibility.
- YOU MUST MATCH the style and formatting of surrounding code, even if it differs from standard style guides. Consistency within a file trumps external standards.
- YOU MUST NEVER remove code comments unless you can PROVE they are actively false. Comments are important documentation and must be preserved.
- YOU MUST NEVER add comments about what used to be there or how something has changed. 
- YOU MUST NEVER refer to temporal context in comments (like "recently refactored" "moved") or code. Comments should be evergreen and describe the code as it is. If you name something "new" or "enhanced" or "improved", you've probably made a mistake and MUST STOP and ask me what to do.
- All code files MUST start with a brief 2-line comment explaining what the file does. Each line MUST start with "ABOUTME: " to make them easily greppable.
- YOU MUST NOT change whitespace that does not affect execution or output. Otherwise, use a formatting tool.
- YOU MUST UPDATE THE README file to clearly explain the software’s functionality and usage to someone with ZERO CONTEXT. It MUST be understandable to a first-time reader without prior knowledge.

## Documentation and Knowledge Management

- Maintain a Readme file with the needed instructions to run the application locally
- When you notice issues unrelated to current task, mention them for future consideration
- Include detailed code comments for complex business logic
- Update relevant documentatiaon when making significant changes
- Use descriptive commit messages to preserve context
- Maintain project specifications and requirements in this CLAUDE.md file

---

*This POC serves as a foundation for building more sophisticated natural language data querying systems.*