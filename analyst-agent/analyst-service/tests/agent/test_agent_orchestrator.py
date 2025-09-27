# ABOUTME: Unit tests for agent orchestration and LLM integration
# ABOUTME: Tests agent initialization, tool coordination, and response generation

import unittest
import tempfile
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.core.agent.agent_orchestrator import (
    initialize_model,
    create_analyst_agent,
    run_agent_analysis
)
from src.core.models import State, AnalystAgentOutput


class TestInitializeModel(unittest.TestCase):
    """Test cases for model initialization."""

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key', 'OPENAI_MODEL': 'gpt-4'})
    @patch('src.core.agent.agent_orchestrator.OpenAIModel')
    @patch('src.core.agent.agent_orchestrator.OpenAIProvider')
    def test_initialize_model_success(self, mock_provider, mock_model):
        """Test successful model initialization."""
        # Setup mocks
        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Call function
        result = initialize_model()

        # Verify calls
        mock_provider.assert_called_once_with(api_key='test-api-key')
        mock_model.assert_called_once_with('gpt-4', provider=mock_provider_instance)
        self.assertEqual(result, mock_model_instance)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'}, clear=True)
    @patch('src.core.agent.agent_orchestrator.OpenAIModel')
    @patch('src.core.agent.agent_orchestrator.OpenAIProvider')
    def test_initialize_model_default_model(self, mock_provider, mock_model):
        """Test model initialization with default model name."""
        # Remove OPENAI_MODEL from environment
        if 'OPENAI_MODEL' in os.environ:
            del os.environ['OPENAI_MODEL']

        # Setup mocks
        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        # Call function
        result = initialize_model()

        # Verify default model is used
        mock_model.assert_called_once_with('gpt-4.1', provider=mock_provider_instance)

    @patch.dict(os.environ, {}, clear=True)
    def test_initialize_model_missing_api_key(self):
        """Test model initialization with missing API key."""
        with self.assertRaises(RuntimeError) as context:
            initialize_model()

        self.assertIn("OPENAI_API_KEY not found", str(context.exception))

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'})
    @patch('src.core.agent.agent_orchestrator.OpenAIProvider')
    def test_initialize_model_provider_error(self, mock_provider):
        """Test model initialization with provider error."""
        mock_provider.side_effect = Exception("Provider initialization failed")

        with self.assertRaises(RuntimeError) as context:
            initialize_model()

        self.assertIn("Failed to initialize OpenAI model", str(context.exception))

    @patch('src.core.agent.agent_orchestrator.logger')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'})
    @patch('src.core.agent.agent_orchestrator.OpenAIModel')
    @patch('src.core.agent.agent_orchestrator.OpenAIProvider')
    def test_initialize_model_logging(self, mock_provider, mock_model, mock_logger):
        """Test that model initialization logs appropriately."""
        mock_provider.return_value = MagicMock()
        mock_model.return_value = MagicMock()

        initialize_model()

        # Verify logging calls
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()


class TestCreateAnalystAgent(unittest.TestCase):
    """Test cases for agent creation."""

    @patch('src.core.agent.agent_orchestrator.initialize_model')
    @patch('src.core.agent.agent_orchestrator.Agent')
    @patch('src.core.agent.agent_orchestrator.Tool')
    def test_create_analyst_agent_success(self, mock_tool, mock_agent, mock_initialize_model):
        """Test successful agent creation."""
        # Setup mocks
        mock_model = MagicMock()
        mock_initialize_model.return_value = mock_model
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance
        mock_tool_instances = [MagicMock() for _ in range(4)]
        mock_tool.side_effect = mock_tool_instances

        # Call function
        result = create_analyst_agent()

        # Verify model initialization
        mock_initialize_model.assert_called_once()

        # Verify agent creation
        mock_agent.assert_called_once()
        call_args = mock_agent.call_args
        self.assertEqual(call_args[1]['model'], mock_model)
        self.assertEqual(len(call_args[1]['tools']), 4)
        self.assertEqual(call_args[1]['deps_type'], State)
        self.assertEqual(call_args[1]['result_type'], AnalystAgentOutput)
        self.assertTrue(call_args[1]['instrument'])

        self.assertEqual(result, mock_agent_instance)

    @patch('src.core.agent.agent_orchestrator.initialize_model')
    def test_create_analyst_agent_model_error(self, mock_initialize_model):
        """Test agent creation with model initialization error."""
        mock_initialize_model.side_effect = RuntimeError("Model init failed")

        with self.assertRaises(RuntimeError) as context:
            create_analyst_agent()

        self.assertIn("Failed to create analyst agent", str(context.exception))

    @patch('src.core.agent.agent_orchestrator.logger')
    @patch('src.core.agent.agent_orchestrator.initialize_model')
    @patch('src.core.agent.agent_orchestrator.Agent')
    @patch('src.core.agent.agent_orchestrator.Tool')
    def test_create_analyst_agent_logging(self, mock_tool, mock_agent, mock_initialize_model, mock_logger):
        """Test that agent creation logs appropriately."""
        mock_initialize_model.return_value = MagicMock()
        mock_agent.return_value = MagicMock()
        mock_tool.return_value = MagicMock()

        create_analyst_agent()

        # Verify logging calls
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()


class TestRunAgentAnalysis(unittest.TestCase):
    """Test cases for agent analysis execution."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary CSV file for testing
        self.test_data = pd.DataFrame({
            'product': ['A', 'B', 'C'],
            'sales': [100, 200, 150],
            'profit': [20, 40, 30]
        })

        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_run_agent_analysis_input_validation(self):
        """Test input validation for agent analysis."""
        # Test empty query
        result = run_agent_analysis("", self.temp_file.name)
        self.assertIsInstance(result, AnalystAgentOutput)
        self.assertIn("Analysis Failed", result.analysis_report)
        self.assertIn("User query cannot be empty", result.conclusion)

        # Test empty dataset path
        result = run_agent_analysis("Analyze sales", "")
        self.assertIsInstance(result, AnalystAgentOutput)
        self.assertIn("Analysis Failed", result.analysis_report)
        self.assertIn("Dataset path cannot be empty", result.conclusion)

        # Test whitespace-only inputs
        result = run_agent_analysis("   ", self.temp_file.name)
        self.assertIn("User query cannot be empty", result.conclusion)

        result = run_agent_analysis("Analyze sales", "   ")
        self.assertIn("Dataset path cannot be empty", result.conclusion)

    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    def test_run_agent_analysis_success(self, mock_agent):
        """Test successful agent analysis execution."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.data = AnalystAgentOutput(
            analysis_report="# Test Analysis Report",
            metrics=["metric1: 100", "metric2: 200"],
            image_html_path="/path/to/graph.html",
            image_png_path="/path/to/graph.png",
            conclusion="Test conclusion"
        )
        mock_agent.run_sync.return_value = mock_response

        # Call function
        result = run_agent_analysis("Analyze sales data", self.temp_file.name)

        # Verify agent was called with correct state
        mock_agent.run_sync.assert_called_once()
        call_args = mock_agent.run_sync.call_args
        state = call_args[1]['deps']
        self.assertEqual(state.user_query, "Analyze sales data")
        self.assertEqual(state.file_name, self.temp_file.name)

        # Verify result
        self.assertEqual(result.analysis_report, "# Test Analysis Report")
        self.assertEqual(len(result.metrics), 2)
        self.assertEqual(result.conclusion, "Test conclusion")

    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    def test_run_agent_analysis_agent_error(self, mock_agent):
        """Test agent analysis with agent execution error."""
        mock_agent.run_sync.side_effect = Exception("Agent execution failed")

        result = run_agent_analysis("Analyze sales data", self.temp_file.name)

        self.assertIsInstance(result, AnalystAgentOutput)
        self.assertIn("Analysis Failed", result.analysis_report)
        self.assertIn("Agent execution failed", result.conclusion)

    @patch('src.core.agent.agent_orchestrator.logger')
    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    def test_run_agent_analysis_logging(self, mock_agent, mock_logger):
        """Test that agent analysis logs appropriately."""
        mock_response = MagicMock()
        mock_response.data = AnalystAgentOutput(
            analysis_report="Test",
            metrics=[],
            image_html_path="",
            image_png_path="",
            conclusion="Test"
        )
        mock_agent.run_sync.return_value = mock_response

        run_agent_analysis("Test query", self.temp_file.name)

        # Verify logging calls
        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()


class TestSystemPromptGeneration(unittest.TestCase):
    """Test cases for system prompt generation."""

    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    async def test_system_prompt_generation(self, mock_agent):
        """Test system prompt generation with valid context."""
        from src.core.agent.agent_orchestrator import get_analyst_agent_system_prompt

        # Create mock context
        mock_context = MagicMock()
        mock_context.deps = State(
            user_query="Analyze sales trends",
            file_name="sales_data.csv"
        )

        # Generate prompt
        prompt = await get_analyst_agent_system_prompt(mock_context)

        # Verify prompt content
        self.assertIsInstance(prompt, str)
        self.assertIn("Analyze sales trends", prompt)
        self.assertIn("sales_data.csv", prompt)
        self.assertIn("data analyst agent", prompt.lower())
        self.assertIn("get_column_list", prompt)
        self.assertIn("python_execution_tool", prompt)

    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    @patch('src.core.agent.agent_orchestrator.logger')
    async def test_system_prompt_empty_context(self, mock_logger, mock_agent):
        """Test system prompt generation with empty context values."""
        from src.core.agent.agent_orchestrator import get_analyst_agent_system_prompt

        # Create mock context with empty values
        mock_context = MagicMock()
        mock_context.deps = State(user_query="", file_name="")

        # Generate prompt
        prompt = await get_analyst_agent_system_prompt(mock_context)

        # Verify warnings were logged
        mock_logger.warning.assert_called()

        # Verify prompt still generated
        self.assertIsInstance(prompt, str)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = pd.DataFrame({
            'month': ['Jan', 'Feb', 'Mar'],
            'revenue': [1000, 1500, 1200],
            'expenses': [800, 900, 850]
        })

        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()

    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @patch('src.core.agent.agent_orchestrator.analyst_agent')
    def test_complete_analysis_workflow(self, mock_agent):
        """Test complete analysis workflow from start to finish."""
        # Setup comprehensive mock response
        mock_response = MagicMock()
        mock_response.data = AnalystAgentOutput(
            analysis_report="""
# Financial Analysis Report

## Executive Summary
Revenue analysis shows positive trends with total revenue of $3,700.

## Dataset Overview
- 3 months of financial data
- Key variables: month, revenue, expenses

## Methodology
Statistical analysis using descriptive statistics and trend analysis.

## Detailed Findings
- Average monthly revenue: $1,233.33
- Highest revenue month: February ($1,500)
- Revenue growth trend observed

## Statistical Results
Mean revenue: $1,233.33 (95% CI: $1,000 - $1,500)

## Conclusion
Strong revenue performance with growth opportunities.
""",
            metrics=[
                "Total Revenue: $3,700",
                "Average Monthly Revenue: $1,233.33",
                "Revenue Growth Rate: 15%",
                "Profit Margin: 25%"
            ],
            image_html_path="/path/to/revenue_chart.html",
            image_png_path="/path/to/revenue_chart.png",
            conclusion="Revenue shows positive trends with 15% growth rate and opportunities for continued expansion."
        )
        mock_agent.run_sync.return_value = mock_response

        # Execute analysis
        result = run_agent_analysis(
            "Analyze the revenue trends and provide insights on financial performance",
            self.temp_file.name
        )

        # Comprehensive verification
        self.assertIsInstance(result, AnalystAgentOutput)

        # Check analysis report structure
        self.assertIn("# Financial Analysis Report", result.analysis_report)
        self.assertIn("Executive Summary", result.analysis_report)
        self.assertIn("Dataset Overview", result.analysis_report)
        self.assertIn("Methodology", result.analysis_report)

        # Check metrics
        self.assertEqual(len(result.metrics), 4)
        self.assertIn("Total Revenue: $3,700", result.metrics)

        # Check visualization paths
        self.assertEqual(result.image_html_path, "/path/to/revenue_chart.html")
        self.assertEqual(result.image_png_path, "/path/to/revenue_chart.png")

        # Check conclusion
        self.assertIn("15% growth rate", result.conclusion)


if __name__ == '__main__':
    unittest.main()