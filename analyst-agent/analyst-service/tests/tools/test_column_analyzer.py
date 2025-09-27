# ABOUTME: Unit tests for column analyzer tools
# ABOUTME: Tests column analysis functions and error handling

import unittest
import tempfile
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.core.tools.column_analyzer import get_column_list, get_column_description, analyze_column_types
from src.core.models import ToolResponse


class TestColumnAnalyzer(unittest.TestCase):
    """Test cases for column analyzer functions."""

    def setUp(self):
        """Set up test fixtures with sample CSV data."""
        # Create temporary CSV file for testing
        self.test_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000],
            'city': ['New York', 'London', 'Tokyo']
        })

        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_get_column_list_success(self):
        """Test successful column list retrieval."""
        result = get_column_list(self.temp_file.name)

        expected_columns = ['name', 'age', 'salary', 'city']
        self.assertEqual(result, str(expected_columns))

    def test_get_column_list_file_not_found(self):
        """Test column list retrieval with non-existent file."""
        result = get_column_list("nonexistent.csv")

        self.assertIn("Error:", result)
        self.assertIn("File not found", result)

    def test_get_column_list_empty_filename(self):
        """Test column list retrieval with empty filename."""
        result = get_column_list("")

        self.assertIn("Error:", result)
        self.assertIn("File name cannot be empty", result)

    def test_get_column_list_whitespace_filename(self):
        """Test column list retrieval with whitespace-only filename."""
        result = get_column_list("   ")

        self.assertIn("Error:", result)
        self.assertIn("File name cannot be empty", result)

    def test_get_column_list_empty_csv(self):
        """Test column list retrieval with empty CSV file."""
        empty_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        empty_file.write("")
        empty_file.close()

        try:
            result = get_column_list(empty_file.name)
            self.assertIn("Error:", result)
        finally:
            os.unlink(empty_file.name)

    @patch('src.core.tools.column_analyzer.pd.read_csv')
    def test_get_column_list_parser_error(self, mock_read_csv):
        """Test column list retrieval with CSV parser error."""
        mock_read_csv.side_effect = pd.errors.ParserError("Invalid CSV format")

        result = get_column_list("test.csv")

        self.assertIn("Error:", result)
        self.assertIn("Failed to parse CSV file", result)

    def test_get_column_description_success(self):
        """Test successful column description retrieval."""
        column_dict = {
            'name': 'Customer name',
            'age': 'Customer age in years',
            'salary': 'Annual salary in USD'
        }

        result = get_column_description(column_dict)

        self.assertEqual(result, str(column_dict))

    def test_get_column_description_empty_dict(self):
        """Test column description with empty dictionary."""
        result = get_column_description({})

        self.assertIn("Error:", result)
        self.assertIn("Column dictionary cannot be empty", result)

    def test_get_column_description_invalid_input(self):
        """Test column description with non-dictionary input."""
        result = get_column_description("not a dict")

        self.assertIn("Error:", result)
        self.assertIn("Column dictionary must be a valid dictionary", result)

    def test_get_column_description_none_input(self):
        """Test column description with None input."""
        result = get_column_description(None)

        self.assertIn("Error:", result)
        self.assertIn("Column dictionary must be a valid dictionary", result)

    def test_analyze_column_types_success(self):
        """Test successful column type analysis."""
        result = analyze_column_types(self.temp_file.name)

        self.assertIsInstance(result, ToolResponse)
        self.assertTrue(result.success)
        self.assertIn("name", result.data)
        self.assertIn("age", result.data)
        self.assertIn("salary", result.data)
        self.assertIn("city", result.data)

    def test_analyze_column_types_file_not_found(self):
        """Test column type analysis with non-existent file."""
        result = analyze_column_types("nonexistent.csv")

        self.assertIsInstance(result, ToolResponse)
        self.assertFalse(result.success)
        self.assertIn("Failed to analyze column types", result.error)

    def test_analyze_column_types_data_validation(self):
        """Test that column type analysis returns expected data structure."""
        result = analyze_column_types(self.temp_file.name)

        self.assertTrue(result.success)

        # Parse the result data (it's a string representation of a dict)
        # In a real implementation, you might want to return structured data
        data_str = result.data

        # Check that basic column information is present
        self.assertIn("dtype", data_str)
        self.assertIn("non_null_count", data_str)
        self.assertIn("null_count", data_str)
        self.assertIn("unique_count", data_str)
        self.assertIn("sample_values", data_str)

    @patch('src.core.tools.column_analyzer.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that appropriate logging occurs during operations."""
        # Test successful operation logging
        get_column_list(self.temp_file.name)

        # Verify debug and info logs were called
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()

    @patch('src.core.tools.column_analyzer.logger')
    def test_error_logging(self, mock_logger):
        """Test that errors are properly logged."""
        # Test with non-existent file
        get_column_list("nonexistent.csv")

        # Verify error log was called
        mock_logger.error.assert_called()


class TestColumnAnalyzerIntegration(unittest.TestCase):
    """Integration tests for column analyzer with different data types."""

    def setUp(self):
        """Set up test fixtures with various data types."""
        # Create CSV with mixed data types including nulls
        self.mixed_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', None, 'David', 'Eva'],
            'score': [85.5, 92.0, 78.5, None, 95.0],
            'active': [True, False, True, False, None],
            'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
        })

        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.mixed_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_mixed_data_types_analysis(self):
        """Test column analysis with mixed data types and null values."""
        result = analyze_column_types(self.temp_file.name)

        self.assertTrue(result.success)

        # Verify all columns are analyzed
        for column in ['id', 'name', 'score', 'active', 'date']:
            self.assertIn(column, result.data)


if __name__ == '__main__':
    unittest.main()