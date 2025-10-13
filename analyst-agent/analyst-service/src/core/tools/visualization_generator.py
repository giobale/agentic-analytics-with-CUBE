# ABOUTME: Chart and graph creation utilities for data visualization
# ABOUTME: Provides functionality to generate interactive and static visualizations

import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend before importing pyplot to prevent macOS threading issues

import logging
import os
from typing import Annotated
from io import StringIO
from contextlib import redirect_stdout
from ..models import ToolResponse

# Configure logging for debugging
logger = logging.getLogger(__name__)


def graph_generator(code: Annotated[str, "The python code to execute to generate visualizations"]) -> str:
    """
    Generate graphs and visualizations using python code.

    Print the graph path in html and png format in the following format:
    'The graph path in html format is <graph_path_html> and the graph path in png format is <graph_path_png>'.

    Parameters:
    - code: The Python code to execute for visualization

    Returns:
    - String containing graph paths or error message
    """
    import time
    start_time = time.time()

    logger.info("[TOOL:VIZ] Starting visualization generation")
    logger.debug(f"[TOOL:VIZ] Code length: {len(code)} characters")
    logger.debug(f"[TOOL:VIZ] Code preview: {code[:100]}..." if len(code) > 100 else f"[TOOL:VIZ] Code: {code}")

    # Input validation
    if not code or not code.strip():
        error_msg = "Visualization code cannot be empty"
        logger.error(f"[TOOL:VIZ] {error_msg}")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    # Ensure output directory exists using config
    try:
        from ...config import config
        output_dir = config.graph_output_dir
    except ImportError:
        output_dir = "./results"

    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"[TOOL:VIZ] Ensured output directory exists: {output_dir}")
    except Exception as e:
        logger.warning(f"[TOOL:VIZ] Could not create output directory: {str(e)}")
        output_dir = "./"  # Fallback to current directory

    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            logger.debug(f"[TOOL:VIZ] Compiling visualization code")
            # The compile step can catch syntax errors early
            compiled_code = compile(code, '<string>', 'exec')

            logger.debug(f"[TOOL:VIZ] Executing compiled visualization code")
            exec(compiled_code, globals(), globals())

        output = catcher.getvalue()
        execution_time = time.time() - start_time
        logger.info(f"[TOOL:VIZ] Successfully generated visualization in {execution_time:.2f}s")
        logger.debug(f"[TOOL:VIZ] Output: {output[:200]}..." if len(output) > 200 else f"[TOOL:VIZ] Output: {output}")

        return (
            f"The graph path is \n\n{output}\n"
            f"Proceed to the next step"
        )

    except SyntaxError as e:
        execution_time = time.time() - start_time
        error_msg = f"Syntax error in visualization code: {str(e)}"
        logger.error(f"[TOOL:VIZ] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    except ImportError as e:
        execution_time = time.time() - start_time
        error_msg = f"Import error (missing visualization library): {str(e)}"
        logger.error(f"[TOOL:VIZ] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Visualization error: {repr(e)}"
        logger.error(f"[TOOL:VIZ] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"


def create_visualization_with_response(code: Annotated[str, "The python code for visualization"]) -> ToolResponse:
    """
    Generate visualization and return structured response.

    Parameters:
    - code: The Python code to execute for visualization

    Returns:
    - ToolResponse containing visualization results
    """
    logger.debug("Starting structured visualization generation")

    if not code or not code.strip():
        error_msg = "Visualization code cannot be empty"
        logger.error(error_msg)
        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )

    # Ensure output directory exists using config
    try:
        from ...config import config
        output_dir = config.graph_output_dir
    except ImportError:
        output_dir = "./results"

    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create output directory: {str(e)}")
        output_dir = "./"

    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals(), globals())

        output = catcher.getvalue()
        logger.info("Successfully generated visualization with structured response")

        return ToolResponse(
            success=True,
            data=output,
            error=""
        )

    except Exception as e:
        error_msg = f"Visualization generation failed: {repr(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )


def validate_visualization_code(code: str) -> ToolResponse:
    """
    Validate visualization code for common issues.

    Parameters:
    - code: The Python code to validate

    Returns:
    - ToolResponse indicating validation results
    """
    logger.debug("Validating visualization code")

    required_elements = []
    warnings = []

    # Check for common visualization libraries
    viz_libraries = ['matplotlib', 'plotly', 'seaborn', 'bokeh']
    has_viz_library = any(lib in code for lib in viz_libraries)

    if not has_viz_library:
        warnings.append("No common visualization library detected (matplotlib, plotly, seaborn, bokeh)")

    # Check for data loading
    if 'pd.read_csv' not in code and 'pandas.read_csv' not in code:
        warnings.append("No CSV data loading detected - ensure data is loaded in the code")

    # Check for save operations
    save_operations = ['savefig', 'write_html', 'save', 'export']
    has_save = any(op in code for op in save_operations)

    if not has_save:
        warnings.append("No save operation detected - visualization may not be saved to file")

    # Check for print statements (required for path output)
    if 'print(' not in code:
        warnings.append("No print statement detected - may not output file paths as required")

    if warnings:
        logger.warning(f"Validation warnings: {'; '.join(warnings)}")
        return ToolResponse(
            success=True,  # Warnings don't fail validation, just inform
            data=f"Validation completed with warnings: {'; '.join(warnings)}",
            error=""
        )

    logger.info("Visualization code passed validation")
    return ToolResponse(
        success=True,
        data="Visualization code validation passed",
        error=""
    )


def generate_standard_plots(file_name: Annotated[str, "The CSV file name"], plot_type: Annotated[str, "Type of plot to generate"]) -> ToolResponse:
    """
    Generate standard plot types for quick visualization.

    Parameters:
    - file_name: The name of the CSV file
    - plot_type: Type of plot ('histogram', 'boxplot', 'scatter', 'correlation_heatmap')

    Returns:
    - ToolResponse containing plot generation results
    """
    logger.debug(f"Generating standard {plot_type} plot for file: {file_name}")

    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np

    try:
        # Read data
        df = pd.read_csv(file_name)
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_columns and plot_type in ['histogram', 'boxplot', 'correlation_heatmap']:
            return ToolResponse(
                success=False,
                data="",
                error=f"No numeric columns available for {plot_type}"
            )

        # Ensure output directory exists using config
        try:
            from ...config import config
            output_dir = config.graph_output_dir
        except ImportError:
            output_dir = "./results"

        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(10, 6))

        if plot_type == 'histogram':
            # Create histogram for first numeric column
            column = numeric_columns[0]
            plt.hist(df[column].dropna(), bins=30, alpha=0.7)
            plt.title(f'Histogram of {column}')
            plt.xlabel(column)
            plt.ylabel('Frequency')

        elif plot_type == 'boxplot':
            # Create boxplot for all numeric columns
            df[numeric_columns].boxplot()
            plt.title('Boxplot of Numeric Columns')
            plt.xticks(rotation=45)

        elif plot_type == 'correlation_heatmap':
            # Create correlation heatmap
            correlation_matrix = df[numeric_columns].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')

        elif plot_type == 'scatter':
            # Create scatter plot for first two numeric columns
            if len(numeric_columns) >= 2:
                plt.scatter(df[numeric_columns[0]], df[numeric_columns[1]], alpha=0.6)
                plt.xlabel(numeric_columns[0])
                plt.ylabel(numeric_columns[1])
                plt.title(f'Scatter Plot: {numeric_columns[0]} vs {numeric_columns[1]}')
            else:
                return ToolResponse(
                    success=False,
                    data="",
                    error="Need at least 2 numeric columns for scatter plot"
                )

        # Save plot
        plot_path = f"{output_dir}/{plot_type}_plot.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Successfully generated {plot_type} plot: {plot_path}")

        return ToolResponse(
            success=True,
            data=f"Generated {plot_type} plot saved to: {plot_path}",
            error=""
        )

    except Exception as e:
        error_msg = f"Failed to generate {plot_type} plot: {str(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )