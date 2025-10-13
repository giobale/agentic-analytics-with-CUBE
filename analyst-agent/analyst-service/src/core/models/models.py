# ABOUTME: Type-safe data structures and validation for the Data Analyst Agent
# ABOUTME: Contains request/response schemas, agent state definitions, and configuration structures

import logging
from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field

# Configure logging for debugging
logger = logging.getLogger(__name__)

@dataclass
class State:
    """Agent state container for managing user query and dataset information."""
    user_query: str = field(default_factory=str)
    file_name: str = field(default_factory=str)

    def __post_init__(self):
        """Validate state after initialization."""
        logger.debug(f"Initializing State with query: '{self.user_query}' and file: '{self.file_name}'")

        if not self.user_query.strip():
            logger.warning("Empty user query provided")

        if not self.file_name.strip():
            logger.warning("Empty file name provided")


class AnalystAgentOutput(BaseModel):
    """Structured output schema for analyst agent responses."""
    analysis_report: str = Field(description="The analysis report in markdown format")
    metrics: List[str] = Field(description="The metrics of the analysis")
    image_html_path: str = Field(description="The path of the graph in html format, if no graph is generated, return empty string")
    image_png_path: str = Field(description="The path of the graph in png format, if no graph is generated, return empty string")
    conclusion: str = Field(description="The conclusion of the analysis")

    def model_post_init(self, __context) -> None:
        """Validate output after model initialization."""
        logger.debug(f"Created AnalystAgentOutput with {len(self.metrics)} metrics")

        if not self.analysis_report.strip():
            logger.warning("Empty analysis report provided")

        if not self.conclusion.strip():
            logger.warning("Empty conclusion provided")


class ToolResponse(BaseModel):
    """Standard response format for tool execution results."""
    success: bool = Field(description="Whether the tool execution was successful")
    data: str = Field(description="The tool execution result data")
    error: str = Field(default="", description="Error message if execution failed")

    def model_post_init(self, __context) -> None:
        """Validate tool response after initialization."""
        if not self.success and not self.error:
            logger.warning("Tool marked as failed but no error message provided")

        if self.success and self.error:
            logger.warning("Tool marked as successful but error message provided")