#!/usr/bin/env python3
import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def get_mysql_type(dtype, max_length=None):
    """Convert pandas dtype to MySQL data type"""
    if pd.api.types.is_integer_dtype(dtype):
        if dtype == 'int64':
            return 'BIGINT'
        else:
            return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'DECIMAL(10,2)'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        # String type - determine appropriate VARCHAR size
        if max_length and max_length > 0:
            if max_length <= 255:
                return f'VARCHAR({max(max_length, 10)})'
            else:
                return 'TEXT'
        else:
            return 'VARCHAR(255)'

def wait_for_mysql():
    """Wait for MySQL to be fully ready"""
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            connection = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                database=os.environ['MYSQL_DATABASE'],
                user='root',
                password=os.environ['MYSQL_ROOT_PASSWORD'],
                connection_timeout=5
            )
            
            if connection.is_connected():
                logger.info("Successfully connected to MySQL")
                connection.close()
                return True
                
        except Error as e:
            attempt += 1
            logger.info(f"MySQL not ready yet (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(10)
    
    logger.error("Failed to connect to MySQL after maximum attempts")
    return False

def create_table_from_csv(csv_path, table_name, connection):
    """Create MySQL table from CSV file structure"""
    try:
        logger.info(f"Processing {csv_path} -> table '{table_name}'")
        
        # Read CSV with flexible parsing that handles both quoted and unquoted fields
        df = pd.read_csv(csv_path, skipinitialspace=True, quotechar='"', doublequote=True)
        
        if df.empty:
            logger.warning(f"{csv_path} is empty, skipping...")
            return False
            
        # Clean column names (replace spaces and special chars with underscores)
        df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
        df.columns = df.columns.str.replace(r'^(\d)', r'col_\1', regex=True)  # Prefix if starts with number
        
        cursor = connection.cursor()
        
        # Drop table if exists
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        
        # Build CREATE TABLE statement
        columns = []
        for col in df.columns:
            # Get max string length for varchar sizing
            if df[col].dtype == 'object':
                max_len = df[col].astype(str).str.len().max() if not df[col].isnull().all() else 10
                max_len = min(max_len * 2, 1000)  # Add buffer, cap at 1000
            else:
                max_len = None
                
            mysql_type = get_mysql_type(df[col].dtype, max_len)
            columns.append(f"`{col}` {mysql_type}")
        
        create_sql = f"CREATE TABLE `{table_name}` ({', '.join(columns)})"
        logger.info(f"Creating table: {create_sql}")
        cursor.execute(create_sql)
        
        # Load data using pandas and INSERT statements (handles commas in text properly)
        logger.info(f"Loading data into {table_name}...")
        
        # Prepare data for insertion
        values_list = []
        for _, row in df.iterrows():
            # Convert each row to a list of values, handling None/NaN
            row_values = []
            for val in row:
                if pd.isna(val):
                    row_values.append('NULL')
                elif isinstance(val, str):
                    # Escape single quotes and wrap in quotes
                    escaped_val = val.replace("'", "''")
                    row_values.append(f"'{escaped_val}'")
                else:
                    row_values.append(str(val))
            values_list.append(f"({', '.join(row_values)})")
        
        # Insert data in batches to avoid memory issues
        batch_size = 1000
        total_rows = len(values_list)
        
        for i in range(0, total_rows, batch_size):
            batch = values_list[i:i + batch_size]
            insert_sql = f"INSERT INTO `{table_name}` VALUES {', '.join(batch)}"
            cursor.execute(insert_sql)
        
        connection.commit()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        row_count = cursor.fetchone()[0]
        logger.info(f"Successfully loaded {row_count} rows into table '{table_name}'")
        
        cursor.close()
        return True
        
    except Exception as e:
        logger.error(f"Error processing {csv_path}: {str(e)}")
        return False

def process_csv_files():
    """Process all CSV files in the directory"""
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            database=os.environ['MYSQL_DATABASE'],
            user='root',
            password=os.environ['MYSQL_ROOT_PASSWORD'],
            connection_timeout=10
        )
        
        if not connection.is_connected():
            logger.error("Failed to connect to MySQL")
            return False
            
        logger.info("Connected to MySQL database")
        
        # Process all CSV files in the directory
        csv_dir = '/var/lib/mysql-files/csv-data'
        if not os.path.exists(csv_dir):
            logger.warning(f"CSV directory {csv_dir} does not exist")
            return False
            
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        
        if not csv_files:
            logger.info("No CSV files found in /var/lib/mysql-files/csv-data")
            logger.info("Place your CSV files in the db-tables directory and they will be processed")
            return True
        
        success_count = 0
        for csv_file in csv_files:
            table_name = os.path.splitext(csv_file)[0]
            # Clean table name
            table_name = table_name.replace('-', '_').replace(' ', '_')
            table_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
            
            csv_path = os.path.join(csv_dir, csv_file)
            if create_table_from_csv(csv_path, table_name, connection):
                success_count += 1
        
        logger.info(f"Successfully processed {success_count}/{len(csv_files)} CSV files")
        
        connection.close()
        return True
        
    except Error as e:
        logger.error(f"Error during processing: {e}")
        return False

def main():
    logger.info("Starting CSV Import Service...")
    
    # Wait for MySQL to be ready
    if not wait_for_mysql():
        sys.exit(1)
    
    # Process existing CSV files
    logger.info("Processing existing CSV files...")
    process_csv_files()
    
    # Keep the service running and check periodically for new files
    logger.info("CSV Import Service is now running. Checking for new files every 30 seconds...")
    processed_files = set()
    
    while True:
        try:
            csv_dir = '/var/lib/mysql-files/csv-data'
            if os.path.exists(csv_dir):
                csv_files = set(f for f in os.listdir(csv_dir) if f.endswith('.csv'))
                new_files = csv_files - processed_files
                
                if new_files:
                    logger.info(f"Found {len(new_files)} new CSV file(s): {', '.join(new_files)}")
                    if process_csv_files():
                        processed_files.update(new_files)
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            logger.info("CSV Import Service stopped")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()