# ABOUTME: Unit tests for code execution utilities
# ABOUTME: Tests Python code execution, safety validation, and error handling

import unittest
from unittest.mock import patch
from io import StringIO
from src.core.tools.code_executor import (
    python_execution_tool,
    execute_code_with_response,
    validate_code_safety
)
from src.core.models import ToolResponse


class TestPythonExecutionTool(unittest.TestCase):
    """Test cases for python_execution_tool function."""

    def test_simple_calculation(self):
        """Test execution of simple mathematical calculation."""
        code = """
result = 2 + 2
print(f"The calculated value for sum is {result}")
"""
        result = python_execution_tool(code)

        self.assertIn("The calculated value is", result)
        self.assertIn("4", result)
        self.assertIn("Make sure to include this value in the report", result)

    def test_pandas_operations(self):
        """Test execution of pandas operations."""
        code = """
import pandas as pd
data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)
mean_a = df['A'].mean()
print(f"The calculated value for mean_A is {mean_a}")
"""
        result = python_execution_tool(code)

        self.assertIn("The calculated value is", result)
        self.assertIn("2.0", result)

    def test_empty_code(self):
        """Test execution with empty code."""
        result = python_execution_tool("")

        self.assertIn("Failed to run code", result)
        self.assertIn("Code cannot be empty", result)

    def test_whitespace_only_code(self):
        """Test execution with whitespace-only code."""
        result = python_execution_tool("   \n   \t   ")

        self.assertIn("Failed to run code", result)
        self.assertIn("Code cannot be empty", result)

    def test_syntax_error(self):
        """Test execution with syntax error."""
        code = "print('hello world'"  # Missing closing parenthesis

        result = python_execution_tool(code)

        self.assertIn("Failed to run code", result)
        self.assertIn("Syntax error", result)

    def test_name_error(self):
        """Test execution with undefined variable."""
        code = "print(undefined_variable)"

        result = python_execution_tool(code)

        self.assertIn("Failed to run code", result)
        self.assertIn("Name error", result)

    def test_import_error(self):
        """Test execution with missing import."""
        code = "import nonexistent_module"

        result = python_execution_tool(code)

        self.assertIn("Failed to run code", result)
        self.assertIn("Import error", result)

    def test_runtime_error(self):
        """Test execution with runtime error."""
        code = "result = 1 / 0"

        result = python_execution_tool(code)

        self.assertIn("Failed to run code", result)
        self.assertIn("Runtime error", result)

    def test_multiple_print_statements(self):
        """Test execution with multiple print statements."""
        code = """
print("First calculation:")
result1 = 5 * 3
print(f"The calculated value for multiplication is {result1}")
print("Second calculation:")
result2 = 10 - 3
print(f"The calculated value for subtraction is {result2}")
"""
        result = python_execution_tool(code)

        self.assertIn("First calculation:", result)
        self.assertIn("15", result)
        self.assertIn("Second calculation:", result)
        self.assertIn("7", result)

    @patch('src.core.tools.code_executor.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that appropriate logging occurs during code execution."""
        code = "print('test')"
        python_execution_tool(code)

        # Verify debug and info logs were called
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()

    @patch('src.core.tools.code_executor.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are properly logged."""
        code = "invalid syntax here"
        python_execution_tool(code)

        # Verify error log was called
        mock_logger.error.assert_called()


class TestExecuteCodeWithResponse(unittest.TestCase):
    """Test cases for execute_code_with_response function."""

    def test_successful_execution(self):
        """Test successful code execution with structured response."""
        code = "print('Hello, World!')"

        result = execute_code_with_response(code)

        self.assertIsInstance(result, ToolResponse)
        self.assertTrue(result.success)
        self.assertIn("Hello, World!", result.data)
        self.assertEqual(result.error, "")

    def test_failed_execution(self):
        """Test failed code execution with structured response."""
        code = "invalid syntax"

        result = execute_code_with_response(code)

        self.assertIsInstance(result, ToolResponse)
        self.assertFalse(result.success)
        self.assertEqual(result.data, "")
        self.assertIn("Code execution failed", result.error)

    def test_empty_code_structured(self):
        """Test empty code with structured response."""
        result = execute_code_with_response("")

        self.assertIsInstance(result, ToolResponse)
        self.assertFalse(result.success)
        self.assertEqual(result.data, "")
        self.assertIn("Code cannot be empty", result.error)


class TestValidateCodeSafety(unittest.TestCase):
    """Test cases for validate_code_safety function."""

    def test_safe_code(self):
        """Test validation of safe code."""
        safe_code = """
import pandas as pd
import numpy as np
df = pd.DataFrame({'A': [1, 2, 3]})
result = df.mean()
print(result)
"""

        result = validate_code_safety(safe_code)

        self.assertIsInstance(result, ToolResponse)
        self.assertTrue(result.success)
        self.assertIn("Code is safe to execute", result.data)
        self.assertEqual(result.error, "")

    def test_dangerous_import_os(self):
        """Test validation detects dangerous os import."""
        dangerous_code = "import os\nos.system('rm -rf /')"

        result = validate_code_safety(dangerous_code)

        self.assertIsInstance(result, ToolResponse)
        self.assertFalse(result.success)
        self.assertIn("import os", result.error)

    def test_dangerous_subprocess(self):
        """Test validation detects subprocess import."""
        dangerous_code = "import subprocess\nsubprocess.call(['ls', '-la'])"

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        self.assertIn("import subprocess", result.error)

    def test_dangerous_eval(self):
        """Test validation detects eval usage."""
        dangerous_code = "result = eval('2 + 2')"

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        self.assertIn("eval(", result.error)

    def test_dangerous_exec(self):
        """Test validation detects exec usage."""
        dangerous_code = "exec('print(\"hello\")')"

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        self.assertIn("exec(", result.error)

    def test_dangerous_file_operations(self):
        """Test validation detects file operations."""
        dangerous_code = "with open('/etc/passwd', 'r') as f: content = f.read()"

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        self.assertIn("open(", result.error)

    def test_dangerous_input(self):
        """Test validation detects input operations."""
        dangerous_code = "user_input = input('Enter password: ')"

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        self.assertIn("input(", result.error)

    def test_multiple_dangerous_operations(self):
        """Test validation detects multiple dangerous operations."""
        dangerous_code = """
import os
import subprocess
result = eval('2 + 2')
with open('/etc/passwd', 'r') as f:
    content = f.read()
"""

        result = validate_code_safety(dangerous_code)

        self.assertFalse(result.success)
        # Should contain multiple warnings
        self.assertIn("import os", result.error)
        self.assertIn("import subprocess", result.error)
        self.assertIn("eval(", result.error)
        self.assertIn("open(", result.error)

    @patch('src.core.tools.code_executor.logger')
    def test_safety_logging(self, mock_logger):
        """Test that safety validation logging works correctly."""
        # Test safe code
        validate_code_safety("print('hello')")
        mock_logger.info.assert_called()

        # Test dangerous code
        validate_code_safety("import os")
        mock_logger.warning.assert_called()


class TestCodeExecutorIntegration(unittest.TestCase):
    """Integration tests for code executor functions."""

    def test_data_analysis_workflow(self):
        """Test a complete data analysis workflow."""
        code = """
import pandas as pd
import numpy as np

# Create sample data
data = {
    'sales': [100, 150, 200, 175, 225],
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May']
}
df = pd.DataFrame(data)

# Calculate statistics
mean_sales = df['sales'].mean()
max_sales = df['sales'].max()
min_sales = df['sales'].min()

print(f"The calculated value for mean_sales is {mean_sales}")
print(f"The calculated value for max_sales is {max_sales}")
print(f"The calculated value for min_sales is {min_sales}")
"""

        result = python_execution_tool(code)

        self.assertIn("The calculated value is", result)
        self.assertIn("170.0", result)  # mean
        self.assertIn("225", result)    # max
        self.assertIn("100", result)    # min

    def test_error_recovery_workflow(self):
        """Test error handling in a multi-step workflow."""
        # First, test with erroneous code
        bad_code = "result = undefined_variable * 2"
        result1 = python_execution_tool(bad_code)
        self.assertIn("Failed to run code", result1)

        # Then test with corrected code
        good_code = """
result = 5 * 2
print(f"The calculated value for multiplication is {result}")
"""
        result2 = python_execution_tool(good_code)
        self.assertIn("10", result2)


if __name__ == '__main__':
    unittest.main()