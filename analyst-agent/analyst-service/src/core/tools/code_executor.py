# ABOUTME: Dynamic Python code execution utilities for calculations and data processing
# ABOUTME: Provides secure code execution with output capture and error handling

import logging
from typing import Annotated
from io import StringIO
from contextlib import redirect_stdout
from ..models import ToolResponse

# Configure logging for debugging
logger = logging.getLogger(__name__)


def python_execution_tool(code: Annotated[str, "The python code to execute for calculations and data processing"]) -> str:
    """
    Execute Python code for calculations, data processing, and metric computation.

    Always use print statement to print the result in format:
    'The calculated value for <variable_name> is <calculated_value>'.

    Parameters:
    - code: The Python code to execute

    Returns:
    - String containing execution results or error message
    """
    logger.debug("Starting Python code execution")
    logger.debug(f"Code to execute: {code[:100]}..." if len(code) > 100 else f"Code to execute: {code}")

    # Input validation
    if not code or not code.strip():
        error_msg = "Code cannot be empty"
        logger.error(error_msg)
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            logger.debug("Compiling Python code")
            # The compile step can catch syntax errors early
            compiled_code = compile(code, '<string>', 'exec')

            logger.debug("Executing compiled code")
            exec(compiled_code, globals(), globals())

        output = catcher.getvalue()
        logger.info("Successfully executed Python code")
        logger.debug(f"Execution output: {output}")

        return (
            f"The calculated value is \n\n{output}\n"
            f"Make sure to include this value in the report\n"
        )

    except SyntaxError as e:
        execution_time = time.time() - start_time
        error_msg = f"Syntax error in code: {str(e)}"
        logger.error(f"[TOOL:CODE] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    except NameError as e:
        execution_time = time.time() - start_time
        error_msg = f"Name error (undefined variable/function): {str(e)}"
        logger.error(f"[TOOL:CODE] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    except ImportError as e:
        execution_time = time.time() - start_time
        error_msg = f"Import error (missing module): {str(e)}"
        logger.error(f"[TOOL:CODE] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Runtime error: {repr(e)}"
        logger.error(f"[TOOL:CODE] {error_msg} (after {execution_time:.2f}s)")
        return f"Failed to run code. Error: {error_msg}, try a different approach"


def execute_code_with_response(code: Annotated[str, "The python code to execute"]) -> ToolResponse:
    """
    Execute Python code and return structured response.

    Parameters:
    - code: The Python code to execute

    Returns:
    - ToolResponse containing execution results
    """
    logger.debug("Starting structured Python code execution")

    if not code or not code.strip():
        error_msg = "Code cannot be empty"
        logger.error(error_msg)
        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )

    catcher = StringIO()

    try:
        with redirect_stdout(catcher):
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals(), globals())

        output = catcher.getvalue()
        logger.info("Successfully executed Python code with structured response")

        return ToolResponse(
            success=True,
            data=output,
            error=""
        )

    except Exception as e:
        error_msg = f"Code execution failed: {repr(e)}"
        logger.error(error_msg)

        return ToolResponse(
            success=False,
            data="",
            error=error_msg
        )


def validate_code_safety(code: str) -> ToolResponse:
    """
    Validate code for potentially dangerous operations.

    Parameters:
    - code: The Python code to validate

    Returns:
    - ToolResponse indicating whether code is safe to execute
    """
    logger.debug("Validating code safety")

    dangerous_operations = [
        'import os',
        'import subprocess',
        'import sys',
        'eval(',
        'exec(',
        '__import__',
        'open(',
        'file(',
        'input(',
        'raw_input(',
    ]

    warnings = []
    for operation in dangerous_operations:
        if operation in code:
            warning = f"Potentially dangerous operation detected: {operation}"
            warnings.append(warning)
            logger.warning(warning)

    if warnings:
        return ToolResponse(
            success=False,
            data="",
            error=f"Code safety validation failed: {'; '.join(warnings)}"
        )

    logger.info("Code passed safety validation")
    return ToolResponse(
        success=True,
        data="Code is safe to execute",
        error=""
    )