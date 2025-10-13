# ABOUTME: Main entry point for the Data Analyst Agent with modular component integration
# ABOUTME: Provides backward compatibility wrapper while using refactored modular architecture

import logging
from typing import List
from src.core import State, AnalystAgentOutput, run_agent_analysis
from src.config import config

# Configure logging based on environment settings
logger = logging.getLogger(__name__)


# Backward compatibility functions - these now use the modular components
def get_column_list(file_name: str) -> str:
    """
    Legacy wrapper for get_column_list tool.
    Now uses the modular column_analyzer component.
    """
    from src.core.tools import get_column_list as modular_get_column_list
    logger.debug(f"Legacy get_column_list called for file: {file_name}")
    return modular_get_column_list(file_name)


def get_column_description(column_dict: dict) -> str:
    """
    Legacy wrapper for get_column_description tool.
    Now uses the modular column_analyzer component.
    """
    from src.core.tools import get_column_description as modular_get_column_description
    logger.debug(f"Legacy get_column_description called for {len(column_dict)} columns")
    return modular_get_column_description(column_dict)


def graph_generator(code: str) -> str:
    """
    Legacy wrapper for graph_generator tool.
    Now uses the modular visualization_generator component.
    """
    from src.core.tools import graph_generator as modular_graph_generator
    logger.debug("Legacy graph_generator called")
    return modular_graph_generator(code)


def python_execution_tool(code: str) -> str:
    """
    Legacy wrapper for python_execution_tool.
    Now uses the modular code_executor component.
    """
    from src.core.tools import python_execution_tool as modular_python_execution_tool
    logger.debug("Legacy python_execution_tool called")
    return modular_python_execution_tool(code)



# Main entry point function using modular architecture
def run_full_agent(user_query: str, dataset_path: str) -> AnalystAgentOutput:
    """
    Execute the complete analysis workflow using the refactored modular architecture.

    This function now uses the modular agent orchestrator while maintaining
    backward compatibility with the original interface.

    Parameters:
    - user_query: The user's analysis request
    - dataset_path: Path to the CSV dataset

    Returns:
    - AnalystAgentOutput containing analysis results
    """
    logger.info(f"Starting analysis for query: '{user_query}' with dataset: '{dataset_path}'")

    try:
        # Input validation
        if not user_query or not user_query.strip():
            error_msg = "User query cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not dataset_path or not dataset_path.strip():
            error_msg = "Dataset path cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Use the modular agent orchestrator
        result = run_agent_analysis(user_query, dataset_path)

        logger.info("Analysis completed successfully")
        logger.debug(f"Analysis result type: {type(result)}")

        # Print for backward compatibility (original function printed response)
        print(f"Analysis completed for query: {user_query}")
        print(f"Dataset: {dataset_path}")
        print(f"Metrics generated: {len(result.metrics)}")

        return result

    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.error(error_msg)

        # Return error response for consistency
        error_response = AnalystAgentOutput(
            analysis_report=f"# Analysis Failed\n\n**Error:** {error_msg}",
            metrics=[],
            image_html_path="",
            image_png_path="",
            conclusion=f"Analysis could not be completed: {error_msg}"
        )

        print(f"Error: {error_msg}")
        return error_response
