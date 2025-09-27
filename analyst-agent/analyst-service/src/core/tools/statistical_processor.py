# ABOUTME: Mathematical computations and statistical analysis functions
# ABOUTME: Provides specialized statistical operations and data processing capabilities

import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before importing pyplot to prevent macOS threading issues

import logging
import pandas as pd
import numpy as np
from typing import Annotated, Dict, Any, List
from ..models import ToolResponse

# Configure logging for debugging
logger = logging.getLogger(__name__)


def calculate_descriptive_statistics(file_name: Annotated[str, "The CSV file name"]) -> ToolResponse:
    """
    Calculate comprehensive descriptive statistics for all numeric columns.

    Parameters:
    - file_name: The name of the CSV file

    Returns:
    - ToolResponse containing descriptive statistics
    """
    import time
    start_time = time.time()

    logger.info(f"[TOOL:STATS] Calculating descriptive statistics for file: {file_name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_name)

        # Select only numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_columns:
            logger.warning("No numeric columns found for statistical analysis")
            return ToolResponse(
                success=True,
                data="No numeric columns found in the dataset",
                error=""
            )

        # Calculate statistics
        stats_dict = {}
        for column in numeric_columns:
            column_data = df[column].dropna()

            stats_dict[column] = {
                'count': len(column_data),
                'mean': float(column_data.mean()),
                'median': float(column_data.median()),
                'std': float(column_data.std()),
                'min': float(column_data.min()),
                'max': float(column_data.max()),
                'q25': float(column_data.quantile(0.25)),
                'q75': float(column_data.quantile(0.75)),
                'skewness': float(column_data.skew()),
                'kurtosis': float(column_data.kurtosis())
            }

        logger.info(f"Successfully calculated statistics for {len(numeric_columns)} numeric columns")

        return ToolResponse(
            success=True,
            data=str(stats_dict),
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to calculate descriptive statistics: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )


def calculate_correlation_matrix(file_name: Annotated[str, "The CSV file name"]) -> ToolResponse:
    """
    Calculate correlation matrix for numeric columns.

    Parameters:
    - file_name: The name of the CSV file

    Returns:
    - ToolResponse containing correlation matrix
    """
    logger.debug(f"Calculating correlation matrix for file: {file_name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_name)

        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty or len(numeric_df.columns) < 2:
            logger.warning("Insufficient numeric columns for correlation analysis")
            return ToolResponse(
                success=True,
                data="Insufficient numeric columns for correlation analysis (need at least 2)",
                error=""
            )

        # Calculate correlation matrix
        correlation_matrix = numeric_df.corr()

        # Convert to dictionary for easier handling
        corr_dict = correlation_matrix.to_dict()

        logger.info(f"Successfully calculated correlation matrix for {len(numeric_df.columns)} columns")

        return ToolResponse(
            success=True,
            data=str(corr_dict),
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to calculate correlation matrix: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )


def detect_outliers(file_name: Annotated[str, "The CSV file name"], column_name: Annotated[str, "The column to analyze for outliers"]) -> ToolResponse:
    """
    Detect outliers in a specific column using IQR method.

    Parameters:
    - file_name: The name of the CSV file
    - column_name: The column to analyze for outliers

    Returns:
    - ToolResponse containing outlier detection results
    """
    logger.debug(f"Detecting outliers in column '{column_name}' for file: {file_name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_name)

        # Validate column exists
        if column_name not in df.columns:
            error_msg = f"Column '{column_name}' not found in dataset"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                data="",
                error=error_msg
            )

        # Check if column is numeric
        if not pd.api.types.is_numeric_dtype(df[column_name]):
            error_msg = f"Column '{column_name}' is not numeric"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                data="",
                error=error_msg
            )

        # Calculate IQR
        column_data = df[column_name].dropna()
        Q1 = column_data.quantile(0.25)
        Q3 = column_data.quantile(0.75)
        IQR = Q3 - Q1

        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Identify outliers
        outliers = column_data[(column_data < lower_bound) | (column_data > upper_bound)]

        outlier_info = {
            'total_values': len(column_data),
            'outlier_count': len(outliers),
            'outlier_percentage': (len(outliers) / len(column_data)) * 100,
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_values': outliers.tolist()[:20]  # Limit to first 20 outliers
        }

        logger.info(f"Successfully detected {len(outliers)} outliers in column '{column_name}'")

        return ToolResponse(
            success=True,
            data=str(outlier_info),
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to detect outliers: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )


def calculate_missing_data_summary(file_name: Annotated[str, "The CSV file name"]) -> ToolResponse:
    """
    Calculate summary of missing data across all columns.

    Parameters:
    - file_name: The name of the CSV file

    Returns:
    - ToolResponse containing missing data summary
    """
    logger.debug(f"Calculating missing data summary for file: {file_name}")

    try:
        # Read CSV file
        df = pd.read_csv(file_name)

        # Calculate missing data info
        missing_info = {}
        total_rows = len(df)

        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / total_rows) * 100

            missing_info[column] = {
                'missing_count': int(missing_count),
                'missing_percentage': float(missing_percentage),
                'data_type': str(df[column].dtype)
            }

        # Overall summary
        total_missing = df.isnull().sum().sum()
        total_cells = df.size
        overall_missing_percentage = (total_missing / total_cells) * 100

        summary = {
            'column_details': missing_info,
            'overall_summary': {
                'total_rows': total_rows,
                'total_columns': len(df.columns),
                'total_missing_values': int(total_missing),
                'overall_missing_percentage': float(overall_missing_percentage)
            }
        }

        logger.info(f"Successfully calculated missing data summary for {len(df.columns)} columns")

        return ToolResponse(
            success=True,
            data=str(summary),
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to calculate missing data summary: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )