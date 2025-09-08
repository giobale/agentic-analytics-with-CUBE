# CUBE Semantic Layer POC

This Proof of Concept demonstrates a natural language querying system built on top of a MySQL database using CUBE's semantic layer. Users can interact with their data through a conversational chat interface that leverages an LLM to translate natural language questions into appropriate CUBE API calls.

**Key Workflow:**
1. User enters a natural language question in the chat interface
2. The LLM receives the question along with the semantic layer context  
3. LLM generates the appropriate CUBE API query
4. System executes the query against the CUBE instance
5. Results are exported as CSV and the file path is returned to the user

This project provides a complete data stack with MySQL container that automatically loads CSV files as database tables, and a CUBE semantic layer for analytics and business intelligence.

## Project Structure

```
├── docker-compose.yml          # Docker Compose configuration
├── .env                       # Environment variables
├── README.md                  # This file
├── test-api.sh                # Quick API authentication tester
├── extract-jwt-token.sh       # JWT token extraction script
├── db-tables/                 # Place your CSV files here
├── mysql-container/            # MySQL container setup
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
└── cube-api-client/          # Python API test application
    ├── cube_api_test.py     # Main test application
    ├── requirements.txt     # Python dependencies
    ├── results/             # CSV output files (auto-created)
    └── README.md           # Application documentation
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for test application)
- curl (for API testing)


## Basic Commands

```bash
# Start the environment
docker-compose up --build -d

# Check container status
docker-compose ps

# Stop containers
docker-compose down

# View logs
docker-compose logs cube
docker-compose logs mysql
```

## Quick Start Guide

### 1. Environment Setup

**Prerequisites:**
- Docker and Docker Compose
- Python 3.8+ (for the test application)
- curl (for API testing)

**Start the Environment:**
```bash
# Clone/setup the project
git clone <repository-url>
cd PoC-V1-CUBE-Semantyc-Layer

# Place CSV files in db-tables/ directory (sample files already included)
ls db-tables/  # Should show: DIM_Events.csv, DIM_Shops.csv, DIM_Tickets.csv, FACT_Orders.csv

# Start containers with build
docker-compose up --build -d

# Wait for health checks to pass (usually takes 1-2 minutes)
docker-compose ps

# Both containers should show "healthy" status
```

### 2. Test Database Connection

```bash
# Test MySQL connectivity from host
mysql -h 127.0.0.1 -P 3306 -u organiser -pamatriciana -e "USE ticketshopdb; SHOW TABLES;"

# Expected output: 4 tables (DIM_Events, DIM_Shops, DIM_Tickets, FACT_Orders)

# Alternative: Test from inside container
docker-compose exec mysql mysql -u organiser -pamatriciana -e "USE ticketshopdb; SHOW TABLES;"
```

### 3. Test CUBE Instance

```bash
# Test CUBE health endpoint
curl http://localhost:4000/readyz
# Expected output: {"health":"HEALTH"}

# Test CUBE development playground access
open http://localhost:4000
# Should open CUBE development interface in browser
```

### 4. Test Data Source Connection

```bash
# Run comprehensive connectivity test
docker-compose exec cube /cube/conf/test.sh

# Expected output should show:
# ✅ MySQL connection successful
# ✅ Cube health check passed  
# ✅ JWT authentication successful!
# 📊 Found XX cubes in the semantic layer
```

### 5. Test CUBE Models via API

```bash
# Get JWT token and test meta API
JWT_TOKEN=$(docker-compose logs cube | grep -o 'eyJ[A-Za-z0-9._-]*' | tail -1)
echo "Using JWT token: ${JWT_TOKEN:0:20}..."

# Test CUBE meta endpoint with authentication
curl -H "Authorization: Bearer $JWT_TOKEN" \
     http://localhost:4000/cubejs-api/v1/meta

# Expected: JSON response with cube definitions for DimEvents, DimShops, DimTickets, FactOrders
```

### 6. Run Sample Python Application

**Navigate to the application directory:**
```bash
cd cube-api-client
```

**Installation:**
```bash
# Option 1: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: Install manually with user flag
pip install --user requests pandas
```

**Run the Application:**
```bash
# Execute the test application
python3 cube_api_test.py

# Expected output:
# 🧪 CUBE API Test Application
# ========================================
# ✅ Successfully connected to CUBE API
# ✅ Available cubes: DimEvents, DimShops, DimTickets, FactOrders
# 
# 📊 Testing Simple Count Queries
# ------------------------------
# 🔍 Executing: Events Count
# ✅ Query executed successfully, 1 rows returned
#    Result: {'DimEvents.count': '4'}
#
# 🔍 Executing: Orders Count and Total Value  
# ✅ Query executed successfully, 1 rows returned
#    Result: {'FactOrders.count': '7840', 'FactOrders.totalOrderValue': '2856420.00'}
#
# 💾 Saving 5 query results to CSV files
# ----------------------------------------
# ✅ Results saved to: results/Events_Count_20240903_155412.csv
# ✅ Results saved to: results/Orders_Count_and_Total_Value_20240903_155412.csv
# ✨ Test completed successfully!
# 📁 All CSV files saved to: ./results/ directory
```

**What the Application Tests:**
1. **API Connectivity** - Verifies CUBE server is reachable
2. **Authentication** - Tests JWT/API secret authentication  
3. **Metadata Access** - Retrieves available cubes and their schema
4. **Query Execution** - Runs various count and aggregation queries:
   - Events count
   - Shops count  
   - Tickets count
   - Orders count and total revenue
   - Orders grouped by payment method
5. **CSV Export** - Saves all query results to timestamped CSV files

**Troubleshooting Python App:**
```bash
# If connection fails, check containers are running
docker-compose ps

# If authentication fails, verify API secret in .env file
grep CUBEJS_API_SECRET .env

# For detailed error info, modify the script to add:
# import logging
# logging.basicConfig(level=logging.DEBUG)

# Test API manually first (will likely fail, use the Python app instead)
curl -H "Authorization: Bearer baubeach" http://localhost:4000/cubejs-api/v1/meta
```

**Note**: The Python app automatically retrieves JWT tokens from container logs for proper authentication.

## CUBE Models

The project includes comprehensive YAML models:
- `dim_events.yml` - Events informaiton (id,company_id, name, capacity, location, start_date etc.)
- `dim_shops.yml` - Shop information (id, company_id, name, created_at etc.)
- `dim_tickets.yml` - Ticket information (id, company_id, event_id, name, price, status, capacity etc. )
- `fact_orders.yml` - Ticket ordder transactions data ( order_id, ticket_id, email, shop_id, event_id, company_id, ticket_count, currency, order_value etc. )