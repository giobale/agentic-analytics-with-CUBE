# CUBE Semantic Layer POC

This Proof of Concept demonstrates a natural language querying system built on top of a MySQL database using CUBE's semantic layer. Users can interact with their data through a conversational chat interface that leverages an LLM to translate natural language questions into appropriate CUBE API calls.

## Components Overview

### 1. MySQL Database
Primary data storage with tables populated from CSV files. Provides the foundational data layer for the event management system.

### 2. CUBE Core (Semantic Layer)
Provides semantic modeling and API layer over MySQL. Defines data cubes, measures, dimensions, and business logic for analytical queries.

### 3. Orchestrator Service
Intelligent query coordination service that transforms natural language into actionable data queries. Features context preparation, conversation management, LLM integration, and CUBE query execution.

### 4. Chat Application (Future Component)
User interface for natural language interactions with session management and response formatting.

## Project Structure

```
├── docker-compose.yml          # Docker Compose configuration
├── .env                       # Environment variables
├── README.md                  # This file
├── test-api.sh                # Quick API authentication tester
├── extract-jwt-token.sh       # JWT token extraction script
├── db-tables/                 # Place your CSV files here
├── mysql-container/           # MySQL container setup
│   ├── docker/
│   │   └── Dockerfile        # MySQL container configuration
│   ├── scripts/
│   │   └── csv-import-service.py  # CSV import service
│   └── config/
│       └── mysql.cnf         # MySQL configuration
├── cube-core/                 # Cube.js semantic layer
│   ├── Dockerfile            # Cube container configuration
│   ├── index.js             # Main application entry point
│   ├── cube.js              # Root configuration file
│   ├── test.sh              # Internal testing script
│   ├── package.json         # Node.js dependencies
│   ├── config/
│   │   └── cube.js          # Cube configuration file
│   └── model/
│       ├── cubes/           # YAML cube schema definitions
│       │   ├── dim_events.yml
│       │   ├── dim_shops.yml
│       │   ├── dim_tickets.yml
│       │   └── fact_orders.yml
│       └── views/           # View definitions
├── orchestrator/              # Natural language query processor
│   ├── orchestrator.py      # Main orchestrator service
│   ├── llm_client.py        # OpenAI API integration
│   ├── cube_client.py       # CUBE API client
│   ├── conversation_manager.py # Chat history management
│   ├── system-prompt-generator/ # Context preparation system
│   │   ├── context_preparation/
│   │   ├── templates/       # System prompt templates
│   │   ├── config/          # Configuration files
│   │   └── tests/          # Testing utilities
│   └── tests/              # Orchestrator tests
└── cube-api-client/          # Python API test application
    ├── cube_api_test.py     # Main test application
    ├── requirements.txt     # Python dependencies
    └── results/             # CSV output files (auto-created)
```

## Quick Start Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for test applications)
- OpenAI API key (for orchestrator)
- curl (for API testing)

### 1. Environment Setup

```bash
# Clone the project
git clone <repository-url>
cd PoC-V1-CUBE-Semantyc-Layer

# Create environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Place CSV files in db-tables/ directory (sample files included)
ls db-tables/  # Should show: DIM_Events.csv, DIM_Shops.csv, DIM_Tickets.csv, FACT_Orders.csv
```

### 2. Start the Core Services

```bash
# Start MySQL and CUBE containers
docker-compose up --build -d

# Wait for health checks to pass (1-2 minutes)
docker-compose ps
# Both containers should show "healthy" status
```

### 3. Test CUBE Instance

```bash
# Test CUBE health
curl http://localhost:4000/readyz
# Expected: {"health":"HEALTH"}

# Test CUBE development interface
open http://localhost:4000
```

### 4. Test with Python API Client

```bash
cd cube-api-client

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run test queries
python3 cube_api_test.py
```

### 5. Test the Orchestrator (Natural Language Processing)

```bash
cd orchestrator

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run interactive test
python3 tests/test_orchestrator_interactive.py
```

### 6. Basic Usage Commands

```bash
# View container logs
docker-compose logs cube
docker-compose logs mysql

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

## Testing Natural Language Queries

With the orchestrator running, you can test queries like:
- "Show me total revenue for each event"
- "Which events sold the most tickets?"
- "What's the average order value by shop?"
- "Show monthly revenue trends"

The orchestrator will convert these into appropriate CUBE API calls and return formatted results.