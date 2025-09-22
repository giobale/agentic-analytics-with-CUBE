# CUBE Semantic Layer POC

## Project Summary

This Proof of Concept (POC) demonstrates a natural language querying system built on top of a MySQL database using CUBE's semantic layer. Users can interact with their data through a conversational chat interface that leverages an LLM to translate natural language questions into appropriate CUBE API calls.

**Key Workflow:**
1. User enters a natural language question in the chat interface
2. The chat app sennds the query to the orchestrator
3. The LLM receives the question along with the semantic layer and conversation context
4. LLM generates the appropriate CUBE API query and descriptive text
5. The orchestrator executes the query against the CUBE instance
6. Results are encapsulated in a descriptive answer and sent back to the chat applicaiton

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat App      │────│   Orchestrator  │────│   CUBE Instance │
│ (Frontend+API)  │    │   (Query Mgmt)  │    │ (Data Analytics)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   LLM Service   │
                        │   (OpenAI API)  │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │ Semantic Layer  │
                        │ & Context Store │
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
**Purpose:** User interface for natural language interactions

**Technology Stack:**
- Backend: Node.js/Express or Python/FastAPI
- Frontend: React/Vue.js or simple HTML/JS
- Communication: REST API calls to Orchestrator

**Key Features:**
- Chat interface for natural language input
- Session management and conversation history
- Response formatting and display
- File download interface for generated CSV files
- User authentication (if required)

### 4. Orchestrator Service
**Purpose:** Intelligent query coordination service that transforms natural language into actionable data queries

**Technology Stack:**
- Backend: Python/FastAPI
- LLM Integration: OpenAI GPT-4 with JSON response format
- CUBE Integration: JWT-authenticated REST API client
- File Management: CSV generation and export system

**Workflow Features (in processing order):**
1. **Context Preparation**: Generates comprehensive system prompts by parsing CUBE view definitions and business configuration
2. **Conversation Management**: Maintains rolling conversation history (last 6 messages) for context-aware responses
3. **LLM Query Generation**: Processes natural language with enhanced JSON response parsing and token usage tracking
4. **Query Validation & Execution**: Authenticates with CUBE via JWT tokens and executes validated queries
5. **Result Processing**: Formats responses for different types (data results, clarifications, errors) and generates CSV exports
6. **Response Orchestration**: Coordinates the complete pipeline and maintains conversation state throughout

**Key Capabilities:**
- Context-aware natural language understanding using semantic layer definitions
- Multi-format response handling (structured data, clarifications, error messages)
- Conversation memory with analytics and export functionality
- Cost monitoring with token usage tracking
- Comprehensive error handling and query validation
- Automated CSV export of analytical results

## Technical Implementation Details

### Orchestrator Workflow
1. **Context Preparation:**
   - Load semantic layer views YML files from the container directory
   - Prepare system prompt with CUBE schema information
   - Include example queries and expected outputs

2. **Query Processing:**
   - Receive user's natural language question
   - Send to OpenAI API with semantic layer context
   - Parse LLM response to extract CUBE query parameters

3. **CUBE API Interaction:**
   - Execute generated query against CUBE REST API
   - Handle authentication and error responses
   - Process results and send them back to chat app

### File Management Strategy
- Generated CSV files from tests stored in `relusts` directories
- Filename format: `query_results_[timestamp]_[hash].csv`

## Docker Compose Configuration

### Services Required:
1. **mysql-db:** MySQL 8.0 database
2. **cube-core:** CUBE semantic layer
3. **orchestrator:** Backend service for query processing and LLM integration
4. **chat-app:** Frontend application for user interface
5. **nginx:** (Optional) Reverse proxy for production

## Success Criteria

### MVP Features:
- [x] MySQL database with CSV data loading
- [x] CUBE semantic layer with basic models
- [x] Chat interface accepting natural language input
- [x] Orchestrator managing, system prompot generation, LLM integration generating and CUBE queries
- [x] Unit tests per component
- [x] Local development environment setup


## Implementation Steps

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

4. **Develop Orchestrator Service:**
   - Build LLM integration with OpenAI
   - Create CUBE API client with JWT authentication
   - Implement conversation management
   - Add system prompt generation
   - Set up CSV export functionality

5. **Build Chat Application:**
   - Develop user interface components
   - Implement API client for orchestrator communication
   - Create conversation display and management
   - Add file download functionality

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