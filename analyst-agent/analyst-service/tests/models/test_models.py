# ABOUTME: Unit tests for data models and validation schemas
# ABOUTME: Tests State, AnalystAgentOutput, and ToolResponse classes

import unittest
from unittest.mock import patch
import logging
from src.core.models import State, AnalystAgentOutput, ToolResponse

# Configure test logging
logging.basicConfig(level=logging.DEBUG)


class TestState(unittest.TestCase):
    """Test cases for State dataclass."""

    def test_state_initialization_with_defaults(self):
        """Test State initialization with default values."""
        state = State()

        self.assertEqual(state.user_query, "")
        self.assertEqual(state.file_name, "")

    def test_state_initialization_with_values(self):
        """Test State initialization with provided values."""
        user_query = "Analyze sales data"
        file_name = "sales.csv"

        state = State(user_query=user_query, file_name=file_name)

        self.assertEqual(state.user_query, user_query)
        self.assertEqual(state.file_name, file_name)

    @patch('src.core.models.logger')
    def test_state_post_init_with_empty_values(self, mock_logger):
        """Test State post_init logging with empty values."""
        state = State(user_query="", file_name="")

        # Verify warning logs were called
        mock_logger.warning.assert_called()
        warning_calls = mock_logger.warning.call_args_list

        # Check that warnings were logged for empty values
        warning_messages = [str(call) for call in warning_calls]
        self.assertTrue(any("Empty user query" in msg for msg in warning_messages))
        self.assertTrue(any("Empty file name" in msg for msg in warning_messages))

    @patch('src.core.models.logger')
    def test_state_post_init_with_valid_values(self, mock_logger):
        """Test State post_init logging with valid values."""
        state = State(user_query="Valid query", file_name="valid.csv")

        # Verify debug log was called
        mock_logger.debug.assert_called_once()


class TestAnalystAgentOutput(unittest.TestCase):
    """Test cases for AnalystAgentOutput model."""

    def test_analyst_agent_output_creation(self):
        """Test creating AnalystAgentOutput with valid data."""
        output = AnalystAgentOutput(
            analysis_report="# Test Report",
            metrics=["metric1", "metric2"],
            image_html_path="/path/to/graph.html",
            image_png_path="/path/to/graph.png",
            conclusion="Test conclusion"
        )

        self.assertEqual(output.analysis_report, "# Test Report")
        self.assertEqual(len(output.metrics), 2)
        self.assertEqual(output.image_html_path, "/path/to/graph.html")
        self.assertEqual(output.image_png_path, "/path/to/graph.png")
        self.assertEqual(output.conclusion, "Test conclusion")

    def test_analyst_agent_output_with_empty_paths(self):
        """Test creating AnalystAgentOutput with empty image paths."""
        output = AnalystAgentOutput(
            analysis_report="# Test Report",
            metrics=["metric1"],
            image_html_path="",
            image_png_path="",
            conclusion="Test conclusion"
        )

        self.assertEqual(output.image_html_path, "")
        self.assertEqual(output.image_png_path, "")

    @patch('src.core.models.logger')
    def test_analyst_agent_output_post_init_empty_report(self, mock_logger):
        """Test post_init validation with empty analysis report."""
        output = AnalystAgentOutput(
            analysis_report="",
            metrics=["metric1"],
            image_html_path="",
            image_png_path="",
            conclusion="Test conclusion"
        )

        # Verify warning was logged for empty report
        mock_logger.warning.assert_called()

    @patch('src.core.models.logger')
    def test_analyst_agent_output_post_init_empty_conclusion(self, mock_logger):
        """Test post_init validation with empty conclusion."""
        output = AnalystAgentOutput(
            analysis_report="# Test Report",
            metrics=["metric1"],
            image_html_path="",
            image_png_path="",
            conclusion=""
        )

        # Verify warning was logged for empty conclusion
        mock_logger.warning.assert_called()


class TestToolResponse(unittest.TestCase):
    """Test cases for ToolResponse model."""

    def test_tool_response_success(self):
        """Test creating successful ToolResponse."""
        response = ToolResponse(
            success=True,
            data="Operation completed successfully",
            error=""
        )

        self.assertTrue(response.success)
        self.assertEqual(response.data, "Operation completed successfully")
        self.assertEqual(response.error, "")

    def test_tool_response_failure(self):
        """Test creating failed ToolResponse."""
        response = ToolResponse(
            success=False,
            data="",
            error="Operation failed due to invalid input"
        )

        self.assertFalse(response.success)
        self.assertEqual(response.data, "")
        self.assertEqual(response.error, "Operation failed due to invalid input")

    def test_tool_response_default_error(self):
        """Test ToolResponse with default empty error."""
        response = ToolResponse(
            success=True,
            data="Success data"
        )

        self.assertEqual(response.error, "")

    @patch('src.core.models.logger')
    def test_tool_response_post_init_failed_no_error(self, mock_logger):
        """Test post_init validation when tool failed but no error message."""
        response = ToolResponse(
            success=False,
            data="",
            error=""
        )

        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn("failed but no error message", warning_call)

    @patch('src.core.models.logger')
    def test_tool_response_post_init_success_with_error(self, mock_logger):
        """Test post_init validation when tool succeeded but has error message."""
        response = ToolResponse(
            success=True,
            data="Success data",
            error="Some error message"
        )

        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn("successful but error message provided", warning_call)


if __name__ == '__main__':
    unittest.main()