# ABOUTME: Pydantic models for query-ambiguity-assessor agent
# ABOUTME: Defines input, output, dependency, and state schemas for the agent

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AgentState(str, Enum):
    """Agent state enumeration for workflow management"""
    QUERY_ASSESSMENT = "query_assessment"
    CLARIFICATION_REQUEST = "clarification_request"
    RECEIVE_CLARIFICATION = "receive_clarification"
    QUERY_CONFIRMATION = "query_confirmation"
    QUERY_REJECTION_HANDLER = "query_rejection_handler"
    API_CALL_CONSTRUCTION = "api_call_construction"
    COMPLETED = "completed"
    ERROR = "error"


class AmbiguityFlags(BaseModel):
    """Flags indicating which aspects of the query are ambiguous"""
    time_specification_unclear: bool = Field(
        default=False,
        description="Whether the time range or period is unclear"
    )
    grouping_granularity_unclear: bool = Field(
        default=False,
        description="Whether the grouping or aggregation level is unclear (daily/weekly/monthly/etc.)"
    )
    filter_criteria_unclear: bool = Field(
        default=False,
        description="Whether filter conditions are missing or unclear"
    )
    measure_ambiguous: bool = Field(
        default=False,
        description="Whether the requested metric or measure is unclear"
    )
    dimension_ambiguous: bool = Field(
        default=False,
        description="Whether the requested dimensions are unclear"
    )

    def is_ambiguous(self) -> bool:
        """Check if any ambiguity flags are set"""
        return any([
            self.time_specification_unclear,
            self.grouping_granularity_unclear,
            self.filter_criteria_unclear,
            self.measure_ambiguous,
            self.dimension_ambiguous
        ])

    def get_ambiguous_aspects(self) -> List[str]:
        """Get list of ambiguous aspects"""
        aspects = []
        if self.time_specification_unclear:
            aspects.append("time_specification")
        if self.grouping_granularity_unclear:
            aspects.append("grouping_granularity")
        if self.filter_criteria_unclear:
            aspects.append("filter_criteria")
        if self.measure_ambiguous:
            aspects.append("measure")
        if self.dimension_ambiguous:
            aspects.append("dimension")
        return aspects


class CubeMetadata(BaseModel):
    """Cube view metadata for context"""
    view_name: str = Field(description="Name of the cube view")
    measures: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Available measures with name, title, and description"
    )
    dimensions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Available dimensions with name, title, description, and type"
    )

    def get_measure_names(self) -> List[str]:
        """Get list of measure names"""
        return [m.get("name", "") for m in self.measures]

    def get_dimension_names(self) -> List[str]:
        """Get list of dimension names"""
        return [d.get("name", "") for d in self.dimensions]

    def get_time_dimensions(self) -> List[str]:
        """Get list of time dimension names"""
        return [d.get("name", "") for d in self.dimensions if d.get("type") == "time"]


class ConversationContext(BaseModel):
    """Conversation history and context"""
    session_id: str = Field(description="Unique session identifier")
    messages: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Conversation message history"
    )
    query_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Accumulated query context from clarifications"
    )

    def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
        """Add message to conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message"""
        for message in reversed(self.messages):
            if message["role"] == "user":
                return message["content"]
        return None

    def update_context(self, key: str, value: Any) -> None:
        """Update query context with new information"""
        self.query_context[key] = value


class AgentDependencies(BaseModel):
    """Dependencies injected into the agent"""
    cube_metadata: CubeMetadata = Field(description="Cube metadata for query validation")
    conversation_context: ConversationContext = Field(description="Conversation history and context")

    class Config:
        arbitrary_types_allowed = True


class QueryAssessmentInput(BaseModel):
    """Input for query assessment state"""
    user_query: str = Field(description="User's natural language query")
    session_id: str = Field(description="Session identifier")


class QueryAssessmentOutput(BaseModel):
    """Output from query assessment state"""
    state: AgentState = Field(description="Next state to transition to")
    ambiguity_flags: AmbiguityFlags = Field(description="Identified ambiguities")
    reasoning: str = Field(description="Explanation of the assessment")
    next_action: str = Field(description="Description of what happens next")


class ClarificationRequestOutput(BaseModel):
    """Output from clarification request state"""
    state: AgentState = Field(description="Next state (always RECEIVE_CLARIFICATION)")
    clarification_question: str = Field(description="Natural language question asking for clarification")
    ambiguous_aspect: str = Field(description="The specific aspect being clarified")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Example values or options to help the user"
    )


class ReceiveClarificationInput(BaseModel):
    """Input for receive clarification state"""
    user_response: str = Field(description="User's clarifying response")
    ambiguous_aspect: str = Field(description="The aspect that was clarified")


class ReceiveClarificationOutput(BaseModel):
    """Output from receive clarification state"""
    state: AgentState = Field(description="Next state (back to QUERY_ASSESSMENT or QUERY_CONFIRMATION)")
    extracted_info: Dict[str, Any] = Field(description="Information extracted from clarification")
    reasoning: str = Field(description="Explanation of what was understood")


class QueryConfirmationOutput(BaseModel):
    """Output from query confirmation state"""
    state: AgentState = Field(description="Next state (QUERY_CONFIRMATION for confirmation request)")
    confirmation_message: str = Field(description="Natural language summary of interpreted query")
    interpreted_parameters: Dict[str, Any] = Field(description="Interpreted query parameters")
    confirmation_required: bool = Field(default=True, description="Whether user confirmation is needed")


class QueryRejectionOutput(BaseModel):
    """Output from query rejection handler state"""
    state: AgentState = Field(description="Next state (back to QUERY_ASSESSMENT)")
    rephrasing_prompt: str = Field(description="Message asking user to rephrase")
    reset_context: bool = Field(default=True, description="Whether to clear query context")


class CubeQueryParameters(BaseModel):
    """Structured Cube.js query parameters"""
    measures: List[str] = Field(description="List of measures to query")
    dimensions: List[str] = Field(
        default_factory=list,
        description="List of dimensions for grouping"
    )
    filters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Filter conditions"
    )
    time_dimensions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Time dimension configurations with granularity"
    )
    order: Dict[str, str] = Field(
        default_factory=dict,
        description="Ordering configuration"
    )
    limit: Optional[int] = Field(default=None, description="Result limit")


class APICallConstructionOutput(BaseModel):
    """Output from API call construction state"""
    state: AgentState = Field(description="Next state (COMPLETED)")
    cube_query: CubeQueryParameters = Field(description="Constructed Cube.js query")
    query_description: str = Field(description="Human-readable description of the query")
    reasoning: str = Field(description="Explanation of how query was constructed")


class AgentResponse(BaseModel):
    """Unified agent response format"""
    success: bool = Field(description="Whether the agent succeeded")
    state: AgentState = Field(description="Current agent state")
    response_type: Literal[
        "assessment",
        "clarification",
        "confirmation",
        "rejection",
        "cube_query",
        "error"
    ] = Field(description="Type of response for routing")
    data: Dict[str, Any] = Field(description="Response data specific to the state")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
