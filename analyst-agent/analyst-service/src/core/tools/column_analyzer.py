# ABOUTME: Dataset structure analysis tools for column inspection and metadata extraction
# ABOUTME: Provides functionality to analyze CSV file columns and their properties

import logging
import pandas as pd
from typing import Annotated, Dict, Any
from ..models import ToolResponse

# Configure logging for debugging
logger = logging.getLogger(__name__)


def get_column_list(file_name: Annotated[str, "The name of the csv file that has the data"]) -> str:
    """
    Retrieve all column names from the CSV file.

    Parameters:
    - file_name: The name of the CSV file that has the data

    Returns:
    - String representation of the column list
    """
    import time
    start_time = time.time()

    logger.info(f"[TOOL:COLUMN] Starting column list extraction for file: {file_name}")

    try:
        # Validate file name
        if not file_name or not file_name.strip():
            error_msg = "File name cannot be empty"
            logger.error(f"[TOOL:COLUMN] {error_msg}")
            return f"Error: {error_msg}"

        # Read CSV file
        logger.debug(f"[TOOL:COLUMN] Reading CSV file: {file_name}")
        df = pd.read_csv(file_name)

        # Log dataset info
        logger.debug(f"[TOOL:COLUMN] Dataset shape: {df.shape}")

        # Extract column names
        columns = df.columns.tolist()
        execution_time = time.time() - start_time
        logger.info(f"[TOOL:COLUMN] Successfully extracted {len(columns)} columns in {execution_time:.2f}s")
        logger.debug(f"[TOOL:COLUMN] Columns found: {columns}")

        return str(columns)

    except FileNotFoundError:
        execution_time = time.time() - start_time
        error_msg = f"File not found: {file_name}"
        logger.error(f"[TOOL:COLUMN] {error_msg} (after {execution_time:.2f}s)")
        return f"Error: {error_msg}"

    except pd.errors.EmptyDataError:
        execution_time = time.time() - start_time
        error_msg = f"Empty CSV file: {file_name}"
        logger.error(f"[TOOL:COLUMN] {error_msg} (after {execution_time:.2f}s)")
        return f"Error: {error_msg}"

    except pd.errors.ParserError as e:
        execution_time = time.time() - start_time
        error_msg = f"Failed to parse CSV file {file_name}: {str(e)}"
        logger.error(f"[TOOL:COLUMN] {error_msg} (after {execution_time:.2f}s)")
        return f"Error: {error_msg}"

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Unexpected error reading {file_name}: {str(e)}"
        logger.error(f"[TOOL:COLUMN] {error_msg} (after {execution_time:.2f}s)")
        return f"Error: {error_msg}"


def get_column_description(column_dict: Annotated[Dict[str, Any], "The dictionary of the column name and the description of the column"]) -> str:
    """
    Get description and metadata for specific columns.

    Parameters:
    - column_dict: Dictionary containing column names and their descriptions

    Returns:
    - String representation of the column descriptions
    """
    logger.debug(f"Processing column descriptions for {len(column_dict)} columns")

    try:
        # Validate input
        if not isinstance(column_dict, dict):
            error_msg = "Column dictionary must be a valid dictionary"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        if not column_dict:
            error_msg = "Column dictionary cannot be empty"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        logger.info(f"Successfully processed column descriptions for {len(column_dict)} columns")
        logger.debug(f"Column descriptions: {column_dict}")

        return str(column_dict)

    except Exception as e:
        error_msg = f"Unexpected error processing column descriptions: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def analyze_column_types(file_name: Annotated[str, "The name of the csv file"]) -> ToolResponse:
    """
    Analyze data types and basic statistics for all columns in the CSV file.

    Parameters:
    - file_name: The name of the CSV file

    Returns:
    - ToolResponse containing column type analysis
    """
    logger.debug(f"Starting column type analysis for file: {file_name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_name)

        # Analyze column types and basic info
        column_info = {}
        for column in df.columns:
            column_info[column] = {
                'dtype': str(df[column].dtype),
                'non_null_count': int(df[column].count()),
                'null_count': int(df[column].isnull().sum()),
                'unique_count': int(df[column].nunique()),
                'sample_values': df[column].dropna().head(3).tolist()
            }

        logger.info(f"Successfully analyzed column types for {len(column_info)} columns")

        return ToolResponse(
            success=True,
            data=str(column_info),
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to analyze column types for {file_name}: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )