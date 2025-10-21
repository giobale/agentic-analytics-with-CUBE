# ABOUTME: System prompts for query-ambiguity-assessor agent
# ABOUTME: Contains static and dynamic prompt templates for different agent states

from typing import Dict, Any, List
from .schemas import CubeMetadata, ConversationContext, AgentState


class PromptTemplates:
    """Collection of prompt templates for the query-ambiguity-assessor agent"""

    @staticmethod
    def get_base_system_prompt() -> str:
        """
        Get the base system prompt that defines the agent's role and behavior.
        This prompt is used across all states.
        """
        return """You are a Query Ambiguity Assessor agent. Your role is to help users formulate clear,
unambiguous queries for a data analytics system built on Cube.js.

Your primary responsibilities:
1. Assess whether user queries are clear enough to execute
2. Identify specific ambiguities in time specifications, grouping, filters, measures, and dimensions
3. Ask targeted clarifying questions (ONE at a time) when ambiguities are found
4. Confirm your interpretation with the user before constructing API calls
5. Build accurate Cube.js query parameters only after receiving user confirmation

Key principles:
- Be conversational and helpful, not robotic
- Focus on ONE ambiguity at a time to avoid overwhelming the user
- Provide contextual examples and suggestions when asking for clarification
- Always confirm your interpretation before proceeding to API call construction
- Use the available cube metadata to validate that requested measures and dimensions exist

You operate in a state-based workflow. Follow the state transitions carefully and provide
outputs in the exact format specified for each state."""

    @staticmethod
    def get_query_assessment_prompt(
        user_query: str,
        cube_metadata: CubeMetadata,
        query_context: Dict[str, Any]
    ) -> str:
        """Generate prompt for query assessment state"""

        # Format available measures and dimensions
        measures_list = "\n".join([
            f"  - {m.get('name', '')}: {m.get('title', '')} - {m.get('description', '')}"
            for m in cube_metadata.measures
        ])

        dimensions_list = "\n".join([
            f"  - {d.get('name', '')} ({d.get('type', 'string')}): {d.get('title', '')} - {d.get('description', '')}"
            for d in cube_metadata.dimensions
        ])

        context_info = ""
        if query_context:
            context_info = f"\n\nPrevious clarifications in this session:\n{query_context}"

        return f"""STATE: QUERY_ASSESSMENT

Analyze this user query for ambiguities:
"{user_query}"

Available Cube view: {cube_metadata.view_name}

Available Measures:
{measures_list}

Available Dimensions:
{dimensions_list}{context_info}

Your task:
1. Determine if the query is clear enough to execute
2. Check for these potential ambiguities:
   - Time specification (is the time period clear?)
   - Grouping granularity (daily/weekly/monthly/yearly/by event/by ticket?)
   - Filter criteria (are all necessary filters specified?)
   - Measures (is it clear which metrics the user wants?)
   - Dimensions (is it clear how to group or filter the data?)

3. Set ambiguity flags appropriately
4. Decide next state:
   - If ANY ambiguity exists → CLARIFICATION_REQUEST
   - If NO ambiguities AND no previous clarifications → QUERY_CONFIRMATION
   - If NO ambiguities AND previous clarifications exist → QUERY_CONFIRMATION

Respond with a QueryAssessmentOutput object."""

    @staticmethod
    def get_clarification_request_prompt(
        ambiguous_aspects: List[str],
        user_query: str,
        cube_metadata: CubeMetadata,
        query_context: Dict[str, Any]
    ) -> str:
        """Generate prompt for clarification request state"""

        # Pick the first ambiguous aspect to clarify
        aspect_to_clarify = ambiguous_aspects[0] if ambiguous_aspects else "general"

        guidance = {
            "time_specification": "Ask about the time period or date range they want to analyze.",
            "grouping_granularity": "Ask about the level of granularity (daily, weekly, monthly, by event, etc.).",
            "filter_criteria": "Ask about specific filters they want to apply.",
            "measure": "Ask which specific metric or measure they want to see.",
            "dimension": "Ask which dimensions they want to group by or filter on."
        }

        current_guidance = guidance.get(aspect_to_clarify, "Ask for the needed clarification.")

        return f"""STATE: CLARIFICATION_REQUEST

User query: "{user_query}"
Ambiguous aspect to clarify: {aspect_to_clarify}

Guidance: {current_guidance}

Query context so far: {query_context}

Available cube metadata: {cube_metadata.view_name}

Your task:
1. Formulate a friendly, conversational clarification question focusing ONLY on: {aspect_to_clarify}
2. Provide 2-4 specific suggestions or examples based on the available dimensions and measures
3. Keep the question simple and focused on ONE thing

Respond with a ClarificationRequestOutput object."""

    @staticmethod
    def get_receive_clarification_prompt(
        user_response: str,
        ambiguous_aspect: str,
        original_query: str,
        query_context: Dict[str, Any]
    ) -> str:
        """Generate prompt for receive clarification state"""

        return f"""STATE: RECEIVE_CLARIFICATION

Original query: "{original_query}"
Ambiguous aspect: {ambiguous_aspect}
User's clarifying response: "{user_response}"

Current query context: {query_context}

Your task:
1. Extract the relevant information from the user's response
2. Update the query context with this information
3. Determine if we should:
   - Go back to QUERY_ASSESSMENT to check for remaining ambiguities
   - Proceed to QUERY_CONFIRMATION if this was the last clarification needed

Respond with a ReceiveClarificationOutput object."""

    @staticmethod
    def get_query_confirmation_prompt(
        original_query: str,
        query_context: Dict[str, Any],
        cube_metadata: CubeMetadata
    ) -> str:
        """Generate prompt for query confirmation state"""

        return f"""STATE: QUERY_CONFIRMATION

Original query: "{original_query}"
Accumulated context from clarifications: {query_context}

Your task:
1. Formulate a clear, natural language summary of what you understand the query to be
2. Include the key parameters:
   - What metrics/measures will be calculated
   - How the data will be grouped (dimensions)
   - What time period is covered
   - Any filters that will be applied
3. Present this to the user for confirmation

The user will respond with either "Confirm" or "Reject" via a button in the UI.

Respond with a QueryConfirmationOutput object including:
- A natural language confirmation message
- The interpreted parameters in a structured format"""

    @staticmethod
    def get_api_call_construction_prompt(
        confirmed_parameters: Dict[str, Any],
        cube_metadata: CubeMetadata,
        original_query: str
    ) -> str:
        """Generate prompt for API call construction state"""

        # Create list of valid measures and dimensions for reference
        valid_measures = cube_metadata.get_measure_names()
        valid_dimensions = cube_metadata.get_dimension_names()
        time_dimensions = cube_metadata.get_time_dimensions()

        return f"""STATE: API_CALL_CONSTRUCTION

Original query: "{original_query}"
Confirmed parameters: {confirmed_parameters}

Available in Cube:
- Measures: {valid_measures}
- Dimensions: {valid_dimensions}
- Time dimensions: {time_dimensions}

Your task:
Construct a valid Cube.js query with these components:

1. measures: List of measure names (must match exactly from available measures)
2. dimensions: List of dimension names for grouping (must match exactly from available dimensions)
3. timeDimensions: List of time dimension configs with:
   - dimension: time dimension name
   - granularity: "day", "week", "month", "year", or null
   - dateRange: "last week", "last month", "this year", etc. (if applicable)
4. filters: List of filter objects (if applicable):
   - member: dimension or measure name
   - operator: "equals", "contains", "gt", "lt", etc.
   - values: array of filter values
5. order: Ordering specification (if applicable)
6. limit: Result limit (if applicable)

IMPORTANT: Use ONLY the exact measure and dimension names from the available lists above.

Respond with an APICallConstructionOutput object containing the complete CubeQueryParameters."""

    @staticmethod
    def get_rejection_handler_prompt(
        original_query: str,
        query_context: Dict[str, Any]
    ) -> str:
        """Generate prompt for query rejection handler state"""

        return f"""STATE: QUERY_REJECTION_HANDLER

The user rejected your interpretation of their query.

Original query: "{original_query}"
Your previous interpretation: {query_context}

Your task:
1. Acknowledge that you misunderstood
2. Ask the user to rephrase or clarify their query
3. Reset the query context to start fresh

Respond with a QueryRejectionOutput object with:
- A friendly message asking them to rephrase
- reset_context set to True"""


class DynamicPromptBuilder:
    """Builds dynamic prompts based on current context and state"""

    @staticmethod
    def build_state_prompt(
        state: AgentState,
        cube_metadata: CubeMetadata,
        conversation_context: ConversationContext,
        **kwargs: Any
    ) -> str:
        """
        Build a dynamic prompt for the given state.

        Args:
            state: Current agent state
            cube_metadata: Cube metadata for context
            conversation_context: Conversation history and context
            **kwargs: Additional state-specific parameters

        Returns:
            Formatted prompt string for the state
        """

        if state == AgentState.QUERY_ASSESSMENT:
            user_query = kwargs.get("user_query", "")
            return PromptTemplates.get_query_assessment_prompt(
                user_query=user_query,
                cube_metadata=cube_metadata,
                query_context=conversation_context.query_context
            )

        elif state == AgentState.CLARIFICATION_REQUEST:
            ambiguous_aspects = kwargs.get("ambiguous_aspects", [])
            user_query = kwargs.get("user_query", "")
            return PromptTemplates.get_clarification_request_prompt(
                ambiguous_aspects=ambiguous_aspects,
                user_query=user_query,
                cube_metadata=cube_metadata,
                query_context=conversation_context.query_context
            )

        elif state == AgentState.RECEIVE_CLARIFICATION:
            user_response = kwargs.get("user_response", "")
            ambiguous_aspect = kwargs.get("ambiguous_aspect", "")
            original_query = kwargs.get("original_query", "")
            return PromptTemplates.get_receive_clarification_prompt(
                user_response=user_response,
                ambiguous_aspect=ambiguous_aspect,
                original_query=original_query,
                query_context=conversation_context.query_context
            )

        elif state == AgentState.QUERY_CONFIRMATION:
            original_query = kwargs.get("original_query", "")
            return PromptTemplates.get_query_confirmation_prompt(
                original_query=original_query,
                query_context=conversation_context.query_context,
                cube_metadata=cube_metadata
            )

        elif state == AgentState.API_CALL_CONSTRUCTION:
            confirmed_parameters = kwargs.get("confirmed_parameters", {})
            original_query = kwargs.get("original_query", "")
            return PromptTemplates.get_api_call_construction_prompt(
                confirmed_parameters=confirmed_parameters,
                cube_metadata=cube_metadata,
                original_query=original_query
            )

        elif state == AgentState.QUERY_REJECTION_HANDLER:
            original_query = kwargs.get("original_query", "")
            return PromptTemplates.get_rejection_handler_prompt(
                original_query=original_query,
                query_context=conversation_context.query_context
            )

        else:
            return f"Unknown state: {state}"
