# ABOUTME: Main PydanticAI agent for query ambiguity assessment
# ABOUTME: Manages state-based workflow for interpreting and clarifying user queries

import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from pydantic_ai import Agent, RunContext
    from pydantic_ai.models import Model
except ImportError:
    raise ImportError(
        "pydantic-ai is required. Install with: pip install pydantic-ai"
    )

from .schemas import (
    AgentState,
    AgentDependencies,
    QueryAssessmentInput,
    QueryAssessmentOutput,
    ClarificationRequestOutput,
    ReceiveClarificationInput,
    ReceiveClarificationOutput,
    QueryConfirmationOutput,
    QueryRejectionOutput,
    APICallConstructionOutput,
    AgentResponse,
    CubeMetadata,
    ConversationContext
)

from .prompts import PromptTemplates, DynamicPromptBuilder

from .tools import (
    get_available_measures,
    get_available_dimensions,
    get_time_dimensions,
    validate_measure_exists,
    validate_dimension_exists,
    update_query_context,
    get_query_context,
    clear_query_context
)

logger = logging.getLogger(__name__)


class QueryAmbiguityAssessor:
    """
    PydanticAI-based agent for assessing and resolving query ambiguities.

    This agent implements a state-based workflow to:
    1. Assess user queries for ambiguities
    2. Request clarifications when needed
    3. Confirm interpretation with the user
    4. Construct Cube.js API calls from confirmed queries
    """

    def __init__(
        self,
        model: str = "openai:gpt-4o",
        api_key: Optional[str] = None
    ):
        """
        Initialize the Query Ambiguity Assessor agent.

        Args:
            model: Model identifier (e.g., "openai:gpt-4o")
            api_key: API key for the model provider
        """
        self.model_name = model
        self.api_key = api_key

        # Create base system prompt
        self.base_system_prompt = PromptTemplates.get_base_system_prompt()

        # Initialize the PydanticAI agent with dependencies
        self.agent = Agent(
            model=self.model_name,
            deps_type=AgentDependencies,
            system_prompt=self.base_system_prompt
        )

        # Register tools with the agent
        self._register_tools()

        # Current state tracking
        self.current_state = AgentState.QUERY_ASSESSMENT

        logger.info(f"QueryAmbiguityAssessor initialized with model: {self.model_name}")

    def _register_tools(self) -> None:
        """Register tools with the PydanticAI agent"""

        # Metadata tools
        @self.agent.tool
        def tool_get_available_measures(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
            """Get list of available measures from the cube metadata."""
            return get_available_measures(ctx.deps)

        @self.agent.tool
        def tool_get_available_dimensions(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
            """Get list of available dimensions from the cube metadata."""
            return get_available_dimensions(ctx.deps)

        @self.agent.tool
        def tool_get_time_dimensions(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
            """Get list of time dimensions from the cube metadata."""
            return get_time_dimensions(ctx.deps)

        @self.agent.tool
        def tool_validate_measure(
            ctx: RunContext[AgentDependencies],
            measure_name: str
        ) -> Dict[str, Any]:
            """Validate that a measure exists in the cube metadata."""
            return validate_measure_exists(ctx.deps, measure_name)

        @self.agent.tool
        def tool_validate_dimension(
            ctx: RunContext[AgentDependencies],
            dimension_name: str
        ) -> Dict[str, Any]:
            """Validate that a dimension exists in the cube metadata."""
            return validate_dimension_exists(ctx.deps, dimension_name)

        # Context management tools
        @self.agent.tool
        def tool_update_context(
            ctx: RunContext[AgentDependencies],
            key: str,
            value: Any
        ) -> Dict[str, Any]:
            """Update the query context with new information from clarifications."""
            return update_query_context(ctx.deps, key, value)

        @self.agent.tool
        def tool_get_context(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
            """Get the current query context."""
            return get_query_context(ctx.deps)

        @self.agent.tool
        def tool_clear_context(ctx: RunContext[AgentDependencies]) -> Dict[str, Any]:
            """Clear the query context (used when query is rejected)."""
            return clear_query_context(ctx.deps)

        logger.debug("Tools registered with agent")

    async def assess_query(
        self,
        user_query: str,
        session_id: str,
        cube_metadata: CubeMetadata,
        conversation_context: Optional[ConversationContext] = None
    ) -> AgentResponse:
        """
        Assess a user query for ambiguities.

        Args:
            user_query: User's natural language query
            session_id: Session identifier
            cube_metadata: Cube metadata for validation
            conversation_context: Optional conversation context

        Returns:
            AgentResponse with assessment results
        """
        try:
            # Initialize conversation context if not provided
            if conversation_context is None:
                conversation_context = ConversationContext(session_id=session_id)

            # Add user message to conversation
            conversation_context.add_message("user", user_query)

            # Create dependencies
            deps = AgentDependencies(
                cube_metadata=cube_metadata,
                conversation_context=conversation_context
            )

            # Build dynamic prompt for query assessment
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.QUERY_ASSESSMENT,
                cube_metadata=cube_metadata,
                conversation_context=conversation_context,
                user_query=user_query
            )

            # Run agent with structured output
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=QueryAssessmentOutput
            )

            assessment = result.data

            # Update conversation with agent response
            conversation_context.add_message(
                "assistant",
                f"Assessment: {assessment.reasoning}"
            )

            # Determine response type based on next state
            if assessment.state == AgentState.CLARIFICATION_REQUEST:
                # Need clarification - get clarification question
                clarification = await self.request_clarification(
                    ambiguous_aspects=assessment.ambiguity_flags.get_ambiguous_aspects(),
                    user_query=user_query,
                    cube_metadata=cube_metadata,
                    conversation_context=conversation_context
                )
                return clarification

            elif assessment.state == AgentState.QUERY_CONFIRMATION:
                # No ambiguities - proceed to confirmation
                confirmation = await self.confirm_query(
                    original_query=user_query,
                    cube_metadata=cube_metadata,
                    conversation_context=conversation_context
                )
                return confirmation

            else:
                # Unknown state
                return AgentResponse(
                    success=False,
                    state=AgentState.ERROR,
                    response_type="error",
                    data={},
                    error=f"Unexpected state transition: {assessment.state}"
                )

        except Exception as e:
            logger.error(f"Error in assess_query: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to assess query: {str(e)}"
            )

    async def request_clarification(
        self,
        ambiguous_aspects: list[str],
        user_query: str,
        cube_metadata: CubeMetadata,
        conversation_context: ConversationContext
    ) -> AgentResponse:
        """
        Request clarification from the user for ambiguous aspects.

        Args:
            ambiguous_aspects: List of ambiguous aspects to clarify
            user_query: Original user query
            cube_metadata: Cube metadata
            conversation_context: Conversation context

        Returns:
            AgentResponse with clarification request
        """
        try:
            deps = AgentDependencies(
                cube_metadata=cube_metadata,
                conversation_context=conversation_context
            )

            # Build clarification prompt
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.CLARIFICATION_REQUEST,
                cube_metadata=cube_metadata,
                conversation_context=conversation_context,
                ambiguous_aspects=ambiguous_aspects,
                user_query=user_query
            )

            # Run agent
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=ClarificationRequestOutput
            )

            clarification = result.data

            # Update conversation
            conversation_context.add_message(
                "assistant",
                clarification.clarification_question
            )

            return AgentResponse(
                success=True,
                state=AgentState.CLARIFICATION_REQUEST,
                response_type="clarification",
                data={
                    "clarification_question": clarification.clarification_question,
                    "ambiguous_aspect": clarification.ambiguous_aspect,
                    "suggestions": clarification.suggestions
                }
            )

        except Exception as e:
            logger.error(f"Error in request_clarification: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to request clarification: {str(e)}"
            )

    async def receive_clarification(
        self,
        user_response: str,
        ambiguous_aspect: str,
        original_query: str,
        cube_metadata: CubeMetadata,
        conversation_context: ConversationContext
    ) -> AgentResponse:
        """
        Receive and process user's clarifying response.

        Args:
            user_response: User's clarifying response
            ambiguous_aspect: The aspect being clarified
            original_query: Original user query
            cube_metadata: Cube metadata
            conversation_context: Conversation context

        Returns:
            AgentResponse with next action
        """
        try:
            # Add user response to conversation
            conversation_context.add_message("user", user_response)

            deps = AgentDependencies(
                cube_metadata=cube_metadata,
                conversation_context=conversation_context
            )

            # Build prompt
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.RECEIVE_CLARIFICATION,
                cube_metadata=cube_metadata,
                conversation_context=conversation_context,
                user_response=user_response,
                ambiguous_aspect=ambiguous_aspect,
                original_query=original_query
            )

            # Run agent
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=ReceiveClarificationOutput
            )

            clarification_result = result.data

            # Update conversation context with extracted info
            for key, value in clarification_result.extracted_info.items():
                conversation_context.update_context(key, value)

            # Add agent response to conversation
            conversation_context.add_message(
                "assistant",
                clarification_result.reasoning
            )

            # Determine next step based on state
            if clarification_result.state == AgentState.QUERY_ASSESSMENT:
                # Re-assess query with new context
                return await self.assess_query(
                    user_query=original_query,
                    session_id=conversation_context.session_id,
                    cube_metadata=cube_metadata,
                    conversation_context=conversation_context
                )
            elif clarification_result.state == AgentState.QUERY_CONFIRMATION:
                # Proceed to confirmation
                return await self.confirm_query(
                    original_query=original_query,
                    cube_metadata=cube_metadata,
                    conversation_context=conversation_context
                )
            else:
                return AgentResponse(
                    success=False,
                    state=AgentState.ERROR,
                    response_type="error",
                    data={},
                    error=f"Unexpected state: {clarification_result.state}"
                )

        except Exception as e:
            logger.error(f"Error in receive_clarification: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to process clarification: {str(e)}"
            )

    async def confirm_query(
        self,
        original_query: str,
        cube_metadata: CubeMetadata,
        conversation_context: ConversationContext
    ) -> AgentResponse:
        """
        Confirm interpretation of the query with the user.

        Args:
            original_query: Original user query
            cube_metadata: Cube metadata
            conversation_context: Conversation context

        Returns:
            AgentResponse with confirmation request
        """
        try:
            deps = AgentDependencies(
                cube_metadata=cube_metadata,
                conversation_context=conversation_context
            )

            # Build prompt
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.QUERY_CONFIRMATION,
                cube_metadata=cube_metadata,
                conversation_context=conversation_context,
                original_query=original_query
            )

            # Run agent
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=QueryConfirmationOutput
            )

            confirmation = result.data

            # Add to conversation
            conversation_context.add_message(
                "assistant",
                confirmation.confirmation_message
            )

            return AgentResponse(
                success=True,
                state=AgentState.QUERY_CONFIRMATION,
                response_type="confirmation",
                data={
                    "confirmation_message": confirmation.confirmation_message,
                    "interpreted_parameters": confirmation.interpreted_parameters
                }
            )

        except Exception as e:
            logger.error(f"Error in confirm_query: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to confirm query: {str(e)}"
            )

    async def handle_rejection(
        self,
        original_query: str,
        conversation_context: ConversationContext
    ) -> AgentResponse:
        """
        Handle user rejection of query interpretation.

        Args:
            original_query: Original user query
            conversation_context: Conversation context

        Returns:
            AgentResponse with rephrasing request
        """
        try:
            # Clear query context
            conversation_context.query_context = {}

            deps = AgentDependencies(
                cube_metadata=CubeMetadata(view_name="", measures=[], dimensions=[]),
                conversation_context=conversation_context
            )

            # Build prompt
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.QUERY_REJECTION_HANDLER,
                cube_metadata=deps.cube_metadata,
                conversation_context=conversation_context,
                original_query=original_query
            )

            # Run agent
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=QueryRejectionOutput
            )

            rejection = result.data

            # Add to conversation
            conversation_context.add_message(
                "assistant",
                rejection.rephrasing_prompt
            )

            return AgentResponse(
                success=True,
                state=AgentState.QUERY_REJECTION_HANDLER,
                response_type="rejection",
                data={
                    "rephrasing_prompt": rejection.rephrasing_prompt
                }
            )

        except Exception as e:
            logger.error(f"Error in handle_rejection: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to handle rejection: {str(e)}"
            )

    async def construct_api_call(
        self,
        confirmed_parameters: Dict[str, Any],
        original_query: str,
        cube_metadata: CubeMetadata,
        conversation_context: ConversationContext
    ) -> AgentResponse:
        """
        Construct Cube.js API call from confirmed parameters.

        Args:
            confirmed_parameters: User-confirmed query parameters
            original_query: Original user query
            cube_metadata: Cube metadata
            conversation_context: Conversation context

        Returns:
            AgentResponse with constructed API call
        """
        try:
            deps = AgentDependencies(
                cube_metadata=cube_metadata,
                conversation_context=conversation_context
            )

            # Build prompt
            state_prompt = DynamicPromptBuilder.build_state_prompt(
                state=AgentState.API_CALL_CONSTRUCTION,
                cube_metadata=cube_metadata,
                conversation_context=conversation_context,
                confirmed_parameters=confirmed_parameters,
                original_query=original_query
            )

            # Run agent
            result = await self.agent.run(
                state_prompt,
                deps=deps,
                result_type=APICallConstructionOutput
            )

            api_call = result.data

            # Add to conversation
            conversation_context.add_message(
                "assistant",
                f"Constructed query: {api_call.query_description}"
            )

            return AgentResponse(
                success=True,
                state=AgentState.API_CALL_CONSTRUCTION,
                response_type="cube_query",
                data={
                    "cube_query": api_call.cube_query.model_dump(),
                    "query_description": api_call.query_description,
                    "reasoning": api_call.reasoning
                }
            )

        except Exception as e:
            logger.error(f"Error in construct_api_call: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=f"Failed to construct API call: {str(e)}"
            )
