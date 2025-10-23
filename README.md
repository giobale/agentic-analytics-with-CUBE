# CUBE Semantic Layer POC

Natural language querying system that translates user questions into CUBE API calls. Users ask questions in plain English, the system retrieves data from MySQL through CUBE's semantic layer, and provides results as structured data and CSV exports.

## Architecture

```
Chat Frontend (React) → Orchestrator (FastAPI) → CUBE Core → MySQL
                               ↓
                          OpenAI API
```

**Components:**

- **Chat Frontend**: React UI for natural language queries. Displays results as tables and charts. Saves queries for reuse.
- **Orchestrator**: FastAPI service that processes queries using OpenAI LLM, validates generated CUBE queries, executes them, and returns results.
- **CUBE Core**: Semantic layer that translates CUBE queries into SQL and manages data models via YAML definitions.
- **MySQL**: Stores event management data loaded from CSV files.
- **Analyst Agent**: Streamlit application for CSV data analysis and report generation using AI.

## Running Locally

**Prerequisites:**
- Docker and Docker Compose
- OpenAI API key

**Steps:**

1. Clone repository and add API key:
```bash
git clone <repository-url>
cd PoC-V1-CUBE-Semantyc-Layer
echo 'OPENAI_API_KEY="your-key"' >> .env
```

2. Start all services:
```bash
docker-compose up --build -d
```

3. Wait 2-3 minutes for services to initialize, then access:
- Chat interface: http://localhost:3000
- Analyst tool: http://localhost:8501

**Service health checks:**
```bash
docker-compose ps                    # Check all services
curl http://localhost:3000/health    # Frontend
curl http://localhost:8080/health    # Orchestrator
curl http://localhost:4000/readyz    # CUBE
```

**View logs:**
```bash
docker-compose logs chat-frontend
docker-compose logs orchestrator
docker-compose logs cube
docker-compose logs mysql
docker-compose logs analyst-agent
```

**Restart services:**
```bash
docker-compose restart <service-name>
docker-compose down && docker-compose up --build -d  # Full rebuild
```

## Data Model

**Event Performance Overview** provides:

**Measures:**
- Order Count
- Total Order Value (revenue)
- Average Order Value
- Total Tickets Sold
- Average Tickets per Order

**Dimensions:**
- Order: ID, Date, Visitor Email
- Event: ID, Name, Start Date, Status, Category
- Business: Company ID, Shop ID, Ticket ID, Payment Method, Currency

## Example Queries

- "Show total revenue by event"
- "Which events sold the most tickets?"
- "Monthly revenue trends"
- "Orders placed last 7 days"
- "Average order value by payment method"
- "Top performing event categories"