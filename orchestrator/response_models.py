# ABOUTME: Pydantic models for OpenAI Structured Outputs
# ABOUTME: Defines strict schemas for LLM response types to guarantee JSON format

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class TimeDimension(BaseModel):
    """Time dimension for CUBE queries"""
    dimension: str = Field(description="The time dimension field name")
    granularity: Optional[str] = Field(default=None, description="Time granularity (day, week, month, year)")
    dateRange: Optional[List[str]] = Field(default=None, description="Date range filter [start, end]")


class CubeQuery(BaseModel):
    """CUBE API query structure"""
    measures: Optional[List[str]] = Field(default=None, description="List of measures to query")
    dimensions: Optional[List[str]] = Field(default=None, description="List of dimensions to query")
    timeDimensions: Optional[List[TimeDimension]] = Field(default=None, description="Time-based dimensions")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Query filters")
    limit: Optional[int] = Field(default=None, description="Result limit")
    order: Optional[Dict[str, str]] = Field(default=None, description="Sort order")


class CubeQueryResponse(BaseModel):
    """Response when LLM generates a CUBE query"""
    response_type: Literal["cube_query"] = Field(description="Must be 'cube_query'")
    cube_query: CubeQuery = Field(description="The CUBE API query to execute")
    description: str = Field(description="Human-readable description of what the query does")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class ClarificationResponse(BaseModel):
    """Response when LLM needs clarification"""
    response_type: Literal["clarification_needed"] = Field(description="Must be 'clarification_needed'")
    message: str = Field(description="Explanation of what clarification is needed")
    questions: List[str] = Field(description="Specific questions that need to be answered")
    suggestions: List[str] = Field(description="Example queries the user could ask")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class ErrorResponse(BaseModel):
    """Response when LLM encounters an error"""
    response_type: Literal["error"] = Field(description="Must be 'error'")
    description: str = Field(description="Description of the error that occurred")
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0, description="Confidence score between 0 and 1")


# Union type for all possible responses
class QueryResponse(BaseModel):
    """Union response model that can be any of the three response types"""
    pass  # This will be used as discriminator in the API call


# Function to get the JSON schema for OpenAI API
def get_response_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for OpenAI Structured Outputs.

    Note: OpenAI Structured Outputs doesn't support if/then/else,
    so we make all fields optional and validate in the code.

    Returns:
        JSON schema dictionary compatible with OpenAI API
    """
    return {
        "name": "query_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "response_type": {
                    "type": "string",
                    "enum": ["cube_query", "clarification_needed", "error"],
                    "description": "The type of response being returned"
                },
                "cube_query": {
                    "type": ["object", "null"],
                    "properties": {
                        "measures": {
                            "type": ["array", "null"],
                            "items": {"type": "string"},
                            "description": "List of measures to query"
                        },
                        "dimensions": {
                            "type": ["array", "null"],
                            "items": {"type": "string"},
                            "description": "List of dimensions to query"
                        },
                        "timeDimensions": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "properties": {
                                    "dimension": {"type": "string"},
                                    "granularity": {
                                        "type": ["string", "null"]
                                    },
                                    "dateRange": {
                                        "type": ["array", "null"],
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["dimension"],
                                "additionalProperties": False
                            },
                            "description": "Time-based dimensions"
                        },
                        "filters": {
                            "type": ["array", "null"],
                            "items": {
                                "type": "object",
                                "additionalProperties": True
                            },
                            "description": "Query filters"
                        },
                        "limit": {
                            "type": ["integer", "null"],
                            "description": "Result limit"
                        },
                        "order": {
                            "type": ["object", "null"],
                            "additionalProperties": True,
                            "description": "Sort order"
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                    "description": "CUBE query object (required when response_type is cube_query)"
                },
                "description": {
                    "type": ["string", "null"],
                    "description": "Human-readable description (required for cube_query and error types)"
                },
                "message": {
                    "type": ["string", "null"],
                    "description": "Message for clarification (required when response_type is clarification_needed)"
                },
                "questions": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Questions for clarification (required when response_type is clarification_needed)"
                },
                "suggestions": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Example queries for clarification (required when response_type is clarification_needed)"
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Confidence score between 0 and 1"
                }
            },
            "required": ["response_type", "confidence_score"],
            "additionalProperties": False
        }
    }
