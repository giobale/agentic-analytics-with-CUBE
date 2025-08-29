# MySQL CSV Loader Container

This project provides a MySQL container that automatically loads CSV files as database tables. The CSV filenames become the table names in the database.

## Project Structure

```
├── docker-compose.yml          # Docker Compose configuration
├── .env                       # Environment variables
├── README.md                  # This file
├── db-tables/                 # Place your CSV files here
├── mysql-container/
│   ├── docker/
│   │   └── Dockerfile        # MySQL container configuration
│   ├── scripts/
│   │   └── 01-load-csv-tables.sh  # CSV import script
│   └── config/
│       └── mysql.cnf         # MySQL configuration
```

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

### 1. Place Your CSV Files

Place your CSV files in the `db-tables/` directory. The filename (without .csv extension) will become the table name.

Example:
- `db-tables/users.csv` → table name: `users`
- `db-tables/products.csv` → table name: `products`
- `db-tables/order-history.csv` → table name: `order_history`

**CSV File Requirements:**
- First row must contain column headers
- Use comma-separated values
- Text fields with commas are automatically handled (no quotes needed)
- UTF-8 encoding recommended

### 2. Configure Environment (Optional)

Edit the `.env` file to customize database credentials:

```bash
MYSQL_ROOT_PASSWORD=your_secure_password
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_PORT=3306
```

### 3. Start the Container

```bash
# Build and start the container
docker-compose up --build -d

# View logs to monitor the import process
docker-compose logs -f mysql
```

### 4. Verify the Import

```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p

# Or connect using the configured user
docker-compose exec mysql mysql -u csvuser -p

#List the databases 
SHOW DATABASES;

USE your_database_name

# List tables
SHOW TABLES;

# Check table structure
DESCRIBE your_table_name;

# Query data
SELECT * FROM your_table_name LIMIT 10;
```

## Usage Examples

### Connect from Host Machine

```bash
# Using MySQL client
mysql -h 127.0.0.1 -P 3306 -u csvuser -p csvdb

# Using Docker exec
docker-compose exec mysql mysql -u csvuser -p csvdb
```

### Sample CSV Format

**users.csv:**
```csv
id,name,email,created_at,description
1,John Doe,john@example.com,2024-01-15,Software Engineer, Team Lead
2,Jane Smith,jane@example.com,2024-01-16,Product Manager, UX Designer
```

This will create a `users` table with columns: `id`, `name`, `email`, `created_at`, `description`. Note how the description field contains commas without requiring quotes.

## Data Type Mapping

The system automatically maps CSV data to appropriate MySQL types:

| CSV Data | MySQL Type |
|----------|------------|
| Integer numbers | INT/BIGINT |
| Decimal numbers | DECIMAL(10,2) |
| Boolean (true/false) | BOOLEAN |
| Date/DateTime | DATETIME |
| Text | VARCHAR(n) or TEXT |

## Management Commands

```bash
# Stop the container
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v

# Restart after adding new CSV files
docker-compose restart mysql

# View container logs
docker-compose logs mysql

# Access MySQL shell
docker-compose exec mysql bash
```

## Adding New CSV Files

To add new CSV files after the container is running:

1. Place new CSV files in `db-tables/` directory
2. Restart the container: `docker-compose restart mysql`
3. The new tables will be created automatically

## Troubleshooting

### CSV Import Issues

1. **Check file encoding**: Ensure CSV files are UTF-8 encoded
2. **Verify file permissions**: CSV files should be readable
3. **Check logs**: `docker-compose logs mysql` for detailed error messages

### Common Issues

- **Permission denied**: Ensure CSV files in `db-tables/` are readable
- **Table not created**: Check CSV format and headers
- **Connection refused**: Wait for container health check to pass
- **Data truncated**: Large text fields may need manual type adjustment

### Monitoring Import Progress

```bash
# Watch real-time logs
docker-compose logs -f mysql | grep -E "(Processing|Successfully|Error)"
```

## Security Notes

- Change default passwords in production
- The `.env` file contains sensitive information - don't commit it to version control
- Consider using Docker secrets for production deployments

## Container Health

The container includes a health check that verifies MySQL is ready:

```bash
# Check container health
docker-compose ps
```

## Customization

### Custom MySQL Configuration

Edit `mysql-container/config/mysql.cnf` to customize MySQL settings.

### Custom Import Logic

Modify `mysql-container/scripts/01-load-csv-tables.sh` to customize the import process.

## Network Access

The MySQL container is accessible on:
- **Host**: `localhost:3306` (or custom port from .env)
- **Container network**: `mysql-csv-loader:3306`

## Data Persistence

Database data persists in a Docker volume named `mysql_data`. To reset all data:

```bash
docker-compose down -v
docker-compose up --build -d
```