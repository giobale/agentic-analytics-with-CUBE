# CUBE Semantic Layer POC

This Proof of Concept demonstrates a natural language querying system built on top of a MySQL database using CUBE's semantic layer. Users can interact with their data through a conversational chat interface that leverages an LLM to translate natural language questions into appropriate CUBE API calls.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat Frontend │────│   Orchestrator  │────│   CUBE Core     │────│   MySQL DB      │
│ (React/Nginx)   │    │   (FastAPI)     │    │ (Semantic Layer)│    │ (Data Storage)  │
│ Port: 3000      │    │   Port: 8080    │    │   Port: 4000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                        ┌─────────────────┐
                        │   LLM Service   │
                        │   (OpenAI API)  │
                        └─────────────────┘
```

**Key Workflow:**
1. User enters a natural language question in the chat interface
2. Frontend sends HTTP request to orchestrator REST API (`/query` endpoint)
3. Orchestrator processes query and calls OpenAI LLM for CUBE query generation
4. Orchestrator executes generated query against CUBE API
5. CUBE retrieves data from MySQL database
6. Results flow back through orchestrator to frontend as structured data and CSV exports

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Build and Run

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd PoC-V1-CUBE-Semantyc-Layer

# Add your OpenAI API key to .env file
echo 'OPENAI_API_KEY="your-api-key-here"' >> .env
```

2. **Build and start all services:**
```bash
docker-compose up --build -d
```

3. **Wait for services to be ready (2-3 minutes):**
```bash
# Check all services are healthy
docker-compose ps

# All containers should show "healthy" status
```

4. **Access the chat application:**
```bash
# Open your browser to:
http://localhost:3000
```

## Available Measures and Dimensions

The system provides access to event management data through the **Event Performance Overview** view:

### Measures (Metrics you can query)
- **Order Count**: Total number of orders
- **Total Order Value**: Sum of all order values (total revenue)
- **Average Order Value**: Mean order revenue
- **Total Tickets Sold**: Total number of tickets sold
- **Average Tickets per Order**: Average number of tickets per order

### Dimensions (Ways to filter and group data)
- **Order Information**: Order ID, Order Date, Visitor Email
- **Event Information**: Event ID, Event Name, Event Start Date, Event Status, Event Category
- **Business Information**: Company ID, Shop ID, Ticket ID, Payment Method, Currency

## Example Questions to Ask

Try these natural language queries in the chat interface:

### Revenue Analytics
- "Show me the total revenue for each event"
- "What's the average order value by payment method?"
- "Which events generated the most revenue?"
- "Show monthly revenue trends"

### Event Performance
- "Which events sold the most tickets?"
- "What's the average number of tickets sold per order?"
- "Show me events with the highest average order value"
- "Which event categories perform best?"

### Customer Insights
- "How many orders were placed last month?"
- "What are the most popular payment methods?"
- "Show me orders by currency"
- "Which shop locations have the highest sales?"

### Time-based Analysis
- "Show me revenue by month"
- "What's the trend in ticket sales over time?"
- "Compare this month's performance to last month"
- "Show me orders placed in the last 7 days"

## Service Health Checks

```bash
# Check individual services
curl http://localhost:3000/health        # Frontend
curl http://localhost:8080/health        # Orchestrator
curl http://localhost:4000/readyz        # CUBE Core
curl http://localhost:3306               # MySQL (connection test)

# View logs
docker-compose logs chat-frontend
docker-compose logs orchestrator
docker-compose logs cube
docker-compose logs mysql
```

## Troubleshooting

### If chat interface doesn't load:
```bash
docker-compose restart chat-frontend
```

### If queries fail:
```bash
# Check orchestrator logs
docker-compose logs orchestrator

# Restart orchestrator
docker-compose restart orchestrator
```

### To rebuild everything:
```bash
docker-compose down
docker-compose up --build -d
```

## Development

The system is fully containerized for easy development and deployment. Each service can be developed independently:

- **Frontend**: React application with styled components
- **Orchestrator**: Python FastAPI service with OpenAI integration
- **CUBE Core**: Node.js semantic layer with YAML model definitions
- **MySQL**: Database with CSV data loading capabilities

For detailed development information, see the CLAUDE.md file.