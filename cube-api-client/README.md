# CUBE API Client

Python application that tests CUBE API connectivity, authenticates using JWT tokens, and exports query results to CSV files.

## Features

- **JWT Authentication**: Automatically retrieves JWT tokens from CUBE container logs
- **API Testing**: Tests connectivity, metadata access, and query execution
- **Query Execution**: Runs sample queries on all cube models
- **CSV Export**: Saves results to timestamped CSV files in dedicated results directory
- **Error Handling**: Comprehensive error reporting and fallback authentication

## Directory Structure

```
cube-api-client/
├── cube_api_test.py      # Main application
├── requirements.txt      # Python dependencies
├── results/             # CSV output files (auto-created)
└── README.md           # This file
```

## Installation

```bash
# Option 1: Virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: User installation
pip install --user requests pandas
```

## Usage

```bash
# Run the application
python3 cube_api_test.py

# Expected output:
# 🧪 CUBE API Test Application
# ========================================
# ✅ Successfully connected to CUBE API
# 🔐 Retrieving JWT token...
# ✅ Retrieved JWT token: eyJhbGciOiJIUzI1NiIs...
# ✅ Available cubes: DimEvents, DimShops, DimTickets, FactOrders
# ...
# ✅ Results saved to: results/Events_Count_20240903_160542.csv
# ✨ Test completed successfully!
# 📁 All CSV files saved to: ./results/ directory
```

## Output Files

All CSV files are automatically saved to the `results/` directory with timestamps:

- `Events_Count_[timestamp].csv` - Event count metrics
- `Shops_Count_[timestamp].csv` - Shop count metrics  
- `Tickets_Count_[timestamp].csv` - Ticket count metrics
- `Orders_Count_and_Total_Value_[timestamp].csv` - Order metrics and revenue
- `Orders_by_Payment_Method_[timestamp].csv` - Orders grouped by payment method

## Requirements

- **Docker**: CUBE containers must be running (`docker-compose up -d`)
- **Python 3.8+**: For the application
- **Dependencies**: requests, pandas (see requirements.txt)
- **Docker Compose**: For JWT token extraction from logs

## Troubleshooting

- **403 Forbidden**: JWT token extraction failed, check if CUBE container is running
- **Connection refused**: CUBE API not accessible, verify containers with `docker-compose ps`
- **No JWT token found**: Access http://localhost:4000 in browser to generate token
- **Import errors**: Install dependencies with `pip install -r requirements.txt`