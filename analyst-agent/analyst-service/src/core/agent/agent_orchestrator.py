# ABOUTME: Main agent orchestration and LLM integration for the Data Analyst Agent
# ABOUTME: Handles agent initialization, tool coordination, and response generation

import logging
import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import AsyncGenerator

from ..models import State, AnalystAgentOutput
from ..tools import (
    get_column_list,
    get_column_description,
    graph_generator,
    python_execution_tool
)

# Configure logging for debugging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def initialize_model() -> OpenAIModel:
    """
    Initialize the OpenAI model with configuration from environment variables.

    Returns:
    - Configured OpenAIModel instance
    """
    logger.debug("[AGENT] Initializing OpenAI model")

    try:
        api_key = os.getenv('OPENAI_API_KEY')
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4.1')

        if not api_key:
            logger.error("[AGENT] OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        logger.debug(f"[AGENT] Using model: {model_name}")

        model = OpenAIModel(
            model_name,
            provider=OpenAIProvider(api_key=api_key)
        )

        logger.info("[AGENT] Successfully initialized OpenAI model")
        return model

    except Exception as e:
        error_msg = f"Failed to initialize OpenAI model: {str(e)}"
        logger.error(f"[AGENT] {error_msg}")
        raise RuntimeError(error_msg)


def get_analyst_agent_system_prompt(ctx: RunContext[State]) -> str:
    """
    Generate the system prompt for the analyst agent based on context.

    Parameters:
    - ctx: Agent run context containing state information

    Returns:
    - String containing the system prompt
    """
    logger.debug("Generating system prompt")

    try:
        # Validate context
        if not ctx.deps.user_query.strip():
            logger.warning("Empty user query in context")

        if not ctx.deps.file_name.strip():
            logger.warning("Empty file name in context")

        prompt = f"""
        You are an expert data analyst agent responsible for executing comprehensive data analysis workflows and generating professional analytical reports.

        **Your Mission:**
        Analyze the provided dataset to answer the user's query through systematic data exploration, statistical analysis, and visualization. Deliver actionable insights through a comprehensive report backed by quantitative evidence.

        **Available Tools:**
        - `get_column_list`: Retrieve all column names from the dataset
        - `get_column_description`: Get detailed descriptions and metadata for specific columns
        - `graph_generator`: Create visualizations (charts, plots, graphs) and save them in HTML and PNG formats. Use plotly express library to make the graph interactive.
        - `python_execution_tool`: Execute Python code for statistical calculations, data processing, and metric computation

        **Input Context:**
        - User Query: {ctx.deps.user_query}
        - Dataset File Name: {ctx.deps.file_name}

        **Execution Workflow:**
        **CRITICAL**: State is not persistent between tool calls. Always reload the dataset and import necessary libraries in each Python execution.

        1. **Dataset Discovery**: Use `get_column_list` to retrieve all available columns, then use `get_column_description` to understand column meanings and data types.

        2. **Analysis Planning**: Based on the user query and dataset structure, create a systematic analysis plan identifying:
           - Key variables to examine
           - Statistical methods to apply
           - Visualizations to create
           - Metrics to calculate

        3. **Data Exploration**: Load the dataset using pandas and perform initial exploration:
           - Check data shape, types, and quality
           - Identify missing values and outliers
           - Generate descriptive statistics

        4. **Statistical Analysis**: Execute the planned analysis using appropriate statistical methods:
           - Calculate relevant metrics and aggregations
           - Perform hypothesis testing if applicable
           - Identify patterns, trends, and correlations

        5. **Visualization Creation**: Generate meaningful visualizations that support your findings:
           - Use appropriate chart types for the data
           - Ensure visualizations are clear and informative
           - Save outputs in both HTML and PNG formats

        6. **Report Synthesis**: Compile all findings into a comprehensive analytical report.

        **Tool Usage Best Practices:**

        **python_execution_tool**:
        - Always include necessary imports: `import pandas as pd`, `import numpy as np`, `import matplotlib.pyplot as plt`, `import seaborn as sns`
        - Load dataset fresh each time: `df = pd.read_csv('{ctx.deps.file_name}')`
        - Use descriptive variable names and clear print statements
        - Format output: `print(f"The calculated value for {{metric_name}} is {{value}}")`
        - Handle errors gracefully with try-except blocks

        **graph_generator**:
        - Always include necessary imports and dataset loading
        - Create publication-quality visualizations with proper labels, titles, and legends
        - Save graphs in the results directory: `plt.savefig('results/analysis_graph.png', dpi=300, bbox_inches='tight')`
        - For interactive plots, save HTML files to: `fig.write_html('results/analysis_graph.html')`
        - **CRITICAL**: Always generate BOTH HTML and PNG formats for every visualization
        - Print file paths in the required format: `print("The graph path in html format is results/graph.html and the graph path in png format is results/graph.png")`

        **get_column_list & get_column_description**:
        - Use these tools first to understand the dataset structure
        - Reference column information when planning analysis steps

        **Output Requirements:**
        Your final output must include:

        - **analysis_report**: Professional markdown report containing:
          * Executive Summary (key findings in 2-3 sentences)
          * Dataset Overview (structure, size, key variables)
          * Methodology (analytical approach taken)
          * Detailed Findings (organized by analysis steps)
          * Statistical Results (with proper interpretation)
          * Data Quality Assessment (missing values, outliers, limitations)
          * Insights and Implications

        - **metrics**: List of all calculated numerical values with descriptive labels

        - **image_html_path**: Path to HTML visualization file (empty string if none generated)

        - **image_png_path**: Path to PNG visualization file (empty string if none generated)

        - **conclusion**: Concise summary with actionable recommendations

        **Quality Standards:**
        - Use professional, data-driven language
        - Provide statistical context and significance levels
        - Explain methodologies and any assumptions made
        - Include confidence intervals where appropriate
        - Reference specific data points and calculated metrics
        - Format with proper markdown structure (headers, lists, tables, code blocks)
        - Ensure reproducibility by documenting all steps

        **Error Handling:**
        - If code execution fails, analyze the error and try alternative approaches
        - Handle missing data appropriately (document and address)
        - Validate results for reasonableness before reporting

        **Final Note:**
        Approach this analysis systematically. Think step-by-step, validate your work, and ensure every insight is backed by quantitative evidence. Your goal is to provide the user with a thorough, professional analysis that directly addresses their query.
        """

        logger.debug("Successfully generated system prompt")
        return prompt

    except Exception as e:
        error_msg = f"Failed to generate system prompt: {str(e)}"
        logger.error(error_msg)
        return f"Error generating system prompt: {error_msg}"


def create_analyst_agent() -> Agent:
    """
    Create and configure the analyst agent with tools and settings.

    Returns:
    - Configured Agent instance
    """
    logger.debug("Creating analyst agent")

    try:
        # Initialize model
        model = initialize_model()

        # Create agent with tools and system prompt
        agent = Agent(
            model=model,
            tools=[
                Tool(get_column_list, takes_ctx=False),
                Tool(get_column_description, takes_ctx=False),
                Tool(graph_generator, takes_ctx=False),
                Tool(python_execution_tool, takes_ctx=False)
            ],
            deps_type=State,
            output_type=AnalystAgentOutput,
            retries=1,
            instructions=get_analyst_agent_system_prompt
        )

        logger.info("Successfully created analyst agent")
        return agent

    except Exception as e:
        error_msg = f"Failed to create analyst agent: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


# Initialize the global agent instance
analyst_agent = create_analyst_agent()


def run_agent_analysis(user_query: str, dataset_path: str) -> AnalystAgentOutput:
    """
    Execute the complete analysis workflow using the analyst agent.

    Parameters:
    - user_query: The user's analysis request
    - dataset_path: Path to the CSV dataset

    Returns:
    - AnalystAgentOutput containing analysis results
    """
    import time
    start_time = time.time()

    logger.info(f"[AGENT] Starting analysis workflow")
    logger.info(f"[AGENT] Query: {user_query}")
    logger.info(f"[AGENT] Dataset: {dataset_path}")

    try:
        # Validate inputs
        logger.debug(f"[AGENT] Validating inputs")
        if not user_query.strip():
            logger.error(f"[AGENT] Validation failed: User query cannot be empty")
            raise ValueError("User query cannot be empty")

        if not dataset_path.strip():
            logger.error(f"[AGENT] Validation failed: Dataset path cannot be empty")
            raise ValueError("Dataset path cannot be empty")

        # Check if dataset file exists
        if not os.path.exists(dataset_path):
            logger.error(f"[AGENT] Dataset file not found: {dataset_path}")
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

        logger.debug(f"[AGENT] Input validation completed")

        # Create state
        logger.debug(f"[AGENT] Creating agent state")
        state = State(user_query=user_query, file_name=dataset_path)
        logger.debug(f"[AGENT] Agent state created successfully")

        # Run agent
        logger.info(f"[AGENT] Initializing analyst agent execution")
        logger.debug(f"[AGENT] Agent will process: {len(user_query)} chars query, dataset: {os.path.basename(dataset_path)}")

        execution_start = time.time()

        # Log API call initiation
        logger.info(f"[AGENT] Calling OpenAI API for analysis")

        try:
            response = analyst_agent.run_sync(deps=state)
            execution_time = time.time() - execution_start
            logger.info(f"[AGENT] OpenAI API call completed successfully")
        except Exception as api_error:
            execution_time = time.time() - execution_start
            logger.error(f"[AGENT] OpenAI API call failed after {execution_time:.2f}s: {str(api_error)}")
            raise

        # Log response details
        logger.info(f"[AGENT] Agent execution completed in {execution_time:.2f}s")
        logger.debug(f"[AGENT] Response output type: {type(response.output)}")

        # Validate output
        if hasattr(response.output, 'analysis_report'):
            report_length = len(response.output.analysis_report) if response.output.analysis_report else 0
            metrics_count = len(response.output.metrics) if response.output.metrics else 0
            logger.debug(f"[AGENT] Generated report: {report_length} chars, {metrics_count} metrics")

            if response.output.image_html_path:
                logger.debug(f"[AGENT] HTML visualization: {response.output.image_html_path}")
            if response.output.image_png_path:
                logger.debug(f"[AGENT] PNG visualization: {response.output.image_png_path}")

        total_time = time.time() - start_time
        logger.info(f"[AGENT] Complete analysis workflow finished in {total_time:.2f}s")

        return response.output

    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"Agent analysis failed after {total_time:.2f}s: {str(e)}"
        logger.error(f"[AGENT] {error_msg}")
        logger.debug(f"[AGENT] Error details: {type(e).__name__}: {str(e)}")

        # Return error response
        return AnalystAgentOutput(
            analysis_report=f"# Analysis Failed\n\nError: {error_msg}",
            metrics=[],
            image_html_path="",
            image_png_path="",
            conclusion=f"Analysis could not be completed due to error: {error_msg}"
        )