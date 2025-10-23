# ABOUTME: Interactive debugging test for the query-ambiguity-assessor agent
# ABOUTME: Enables terminal-based query testing with detailed agent state and tool tracking

"""
=================================================================================
TESTING GUIDE - Query Ambiguity Agent Debugger
=================================================================================

QUICK START
-----------
1. Setup environment:
   cd orchestrator
   pip install -r requirements.txt
   export OPENAI_API_KEY="your-api-key"

2. Run interactive mode:
   python tests/test_ambiguity_agent.py

3. Test single query:
   python tests/test_ambiguity_agent.py --query "Show me total revenue"

4. Enable verbose logging:
   python tests/test_ambiguity_agent.py --verbose

5. Enable minimalistic debug output:
   python tests/test_ambiguity_agent.py --debug


USAGE MODES
-----------

Interactive Mode (Recommended for Debugging)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Launch without arguments for full interactive session:

    $ python tests/test_ambiguity_agent.py

Features:
- Enter queries one at a time
- See real-time agent state transitions
- Track tool usage and prompts
- View conversation history with 'history' command
- View state transitions with 'states' command
- View accumulated context with 'context' command
- Clear session with 'clear' command
- Exit with 'exit' or 'quit'

Single Query Mode (Quick Testing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test specific queries directly:

    $ python tests/test_ambiguity_agent.py --query "Show revenue by event"

Useful for:
- Quick smoke tests
- CI/CD integration
- Batch testing with scripts

Verbose Mode (Deep Debugging)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enable detailed logging to see agent internals:

    $ python tests/test_ambiguity_agent.py --verbose

Shows:
- Prompt construction details
- Tool call arguments and results
- PydanticAI internal state
- Model API interactions
- Error stack traces

Debug Mode (Minimalistic Tracking)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enable clean, minimalistic debug output:

    $ python tests/test_ambiguity_agent.py --debug

Shows (clean, one-line format):
- State transitions (→ State: QUERY_ASSESSMENT)
- Prompt function usage (→ Prompt: query_assessment())
- Final interpreted parameters
- No clutter, just essential workflow tracking


WHAT YOU CAN DEBUG
-------------------

1. State Transitions
~~~~~~~~~~~~~~~~~~~~
Track how the agent moves through its 6-state workflow:

   QUERY_ASSESSMENT
   ├─► CLARIFICATION_REQUEST (if ambiguous)
   │   └─► RECEIVE_CLARIFICATION
   │       └─► QUERY_ASSESSMENT (re-assess with new info)
   └─► QUERY_CONFIRMATION (if clear)
       ├─► API_CALL_CONSTRUCTION (if confirmed)
       └─► QUERY_REJECTION_HANDLER (if rejected)

Use 'states' command to view transition history.

2. Tool Usage
~~~~~~~~~~~~~
Monitor which tools the agent calls and why:

   Metadata Tools:
   - tool_get_available_measures() - Lists all available metrics
   - tool_get_available_dimensions() - Lists all grouping dimensions
   - tool_get_time_dimensions() - Lists time-based dimensions
   - tool_validate_measure(name) - Checks if measure exists
   - tool_validate_dimension(name) - Checks if dimension exists

   Context Tools:
   - tool_update_context(key, value) - Stores clarification info
   - tool_get_context() - Retrieves accumulated context
   - tool_clear_context() - Resets context on rejection

Enable --verbose to see tool calls in real-time.

3. Prompt Construction
~~~~~~~~~~~~~~~~~~~~~~
See which prompts the agent uses for each state:

   - Base system prompt (always included)
   - State-specific prompts (changes per workflow state)
   - Dynamic context injection (cube metadata, conversation history)
   - User query formatting

4. Agent Reasoning
~~~~~~~~~~~~~~~~~~
View agent's internal reasoning:

   - Ambiguity detection logic
   - Clarification question generation
   - Interpretation confirmation
   - API call construction logic

5. Conversation Flow
~~~~~~~~~~~~~~~~~~~~
Track complete user-agent dialogue:

   USER: "Show me revenue"
   AGENT: "Assessment: Missing time specification..."
   AGENT: "For what time period would you like to see revenue?"
   USER: "Last month"
   AGENT: "Understood. Time period: last month..."

Use 'history' command to view full conversation.

6. Context Accumulation
~~~~~~~~~~~~~~~~~~~~~~~
Monitor how clarifications build up context:

   Initial: {}
   After clarification 1: {"time_period": "last_month"}
   After clarification 2: {"time_period": "last_month", "grouping": "event_name"}

Use 'context' command to view current context.


SAMPLE TEST SCENARIOS
---------------------

Scenario 1: Ambiguous Query Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Query: "Show me total revenue"

Expected Behavior:
1. Agent detects missing time_specification
2. Enters CLARIFICATION_REQUEST state
3. Asks: "For what time period?"
4. Provides suggestions: ["last 7 days", "last month", "this year"]

Debug Focus:
- Check ambiguity_flags in output
- Verify clarification_question is clear
- Ensure suggestions are helpful

Scenario 2: Clear Query Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Query: "Show total revenue by event name for last month"

Expected Behavior:
1. Agent detects all required info present
2. Enters QUERY_CONFIRMATION state
3. Shows interpreted parameters
4. Ready for API construction

Debug Focus:
- Verify no ambiguity flags raised
- Check interpreted_parameters accuracy
- Confirm smooth state transition

Scenario 3: Partial Ambiguity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Query: "Show revenue by event"

Expected Behavior:
1. Agent detects missing time_specification
2. But recognizes grouping (by event)
3. Requests clarification for time only
4. Context preserves grouping info

Debug Focus:
- Check which ambiguity flags are set
- Verify context accumulation
- Ensure no duplicate clarifications

Scenario 4: Multi-Turn Clarification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Query 1: "Show tickets"
Agent: "What time period?"
Query 2: "Last month"
Agent: "How should I group the data?"
Query 3: "By venue"
Agent: "Confirms interpretation..."

Debug Focus:
- Track state transitions across turns
- Monitor context building
- Verify conversation coherence


TEST QUERY CATEGORIES
----------------------

🔴 Highly Ambiguous (Multiple Issues)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- "Show me total revenue"          → Missing time + filters
- "How many tickets?"              → Missing time + grouping + measure clarity
- "List events"                    → Missing dimensions + time + measures

Expected: Multiple clarification rounds

🟡 Partially Ambiguous (Single Issue)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- "Show revenue by event"          → Missing time only
- "Total tickets sold last month"  → Missing grouping only
- "Events with high revenue"       → Missing time + unclear "high" threshold

Expected: Single clarification request

🟢 Clear Queries (Complete Info)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- "Show total revenue by event name for last month"
- "List total tickets sold by venue for the past 7 days"
- "Show average order value by payment method for 2024"

Expected: Direct to confirmation


COMMAND REFERENCE
-----------------

Interactive Commands:
- <your query>     → Test agent with your query
- history         → View conversation history
- states          → View state transition history
- context         → View accumulated query context
- clear           → Start new session
- exit/quit       → Exit debugger

Command Line Arguments:
--model <name>           → Specify model (default: openai:gpt-4o)
--query <text>           → Test single query (non-interactive)
--verbose                → Enable verbose debug logging (detailed)
--debug                  → Enable minimalistic debug output (clean)
--use-sample-metadata    → Use hardcoded sample instead of Cube.js API
--cube-url <url>         → Cube.js API base URL (default: http://localhost:4000)
--cube-secret <secret>   → Cube.js API secret (default: baubeach)


INTERPRETING OUTPUT
--------------------

Success Indicators:
✅ Success: True              → Agent processed successfully
🟢 Clear query detected       → No ambiguities found
🎯 CUBE QUERY CONSTRUCTED     → Ready for API call

Clarification Indicators:
❓ CLARIFICATION REQUEST      → Agent needs more info
💡 Suggestions: [...]         → Agent provides examples
🟡 Partial ambiguity          → Some info present, some missing

Error Indicators:
❌ Error: <message>           → Something failed
🔴 High ambiguity             → Multiple issues detected
🔄 State: error               → Agent entered error state


TROUBLESHOOTING
---------------

Issue: ImportError: No module named 'pydantic_ai'
Solution: pip install pydantic-ai

Issue: OPENAI_API_KEY not set
Solution: export OPENAI_API_KEY="sk-..."

Issue: Agent responses too slow
Solution: python tests/test_ambiguity_agent.py --model "openai:gpt-3.5-turbo"

Issue: Agent not detecting ambiguities
Solution: Run with --verbose and check:
  1. Cube metadata is correct
  2. Prompts are being constructed properly
  3. Tool calls are succeeding

Issue: State transitions incorrect
Solution: Use 'states' command to review transition history
  1. Check initial_state → final_state progression
  2. Verify response_type matches state
  3. Look for unexpected ERROR states


INTEGRATION TESTING
--------------------

After debugging individual queries, test integration:

1. Test with real cube metadata (DEFAULT):
   - By default, the test fetches metadata from Cube.js API
   - Requires Cube.js running at http://localhost:4000
   - Uses /cubejs-api/v1/meta endpoint to fetch schema
   - Validates measures and dimensions against actual Cube.js views
   - To use hardcoded sample instead: --use-sample-metadata

2. Test clarification flow:
   - Enter ambiguous query
   - Provide clarification
   - Verify context accumulation

3. Test rejection handling:
   - Confirm query interpretation
   - Simulate rejection
   - Verify context clears

4. Test error recovery:
   - Use invalid cube names
   - Provide malformed queries
   - Verify graceful error handling


NEXT STEPS
----------

After testing here:
1. Integrate agent into orchestrator.py
2. Add frontend confirmation UI
3. Connect to real Cube.js instance
4. Add comprehensive logging
5. Create unit tests
6. Deploy behind feature flag

See QUICK_START_PYDANTIC_AGENT.md for integration guide.

=================================================================================
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging
import jwt

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from agents import (
        QueryAmbiguityAssessor,
        CubeMetadata,
        ConversationContext,
        AgentResponse,
        AgentState
    )
    from cube_metadata_fetcher import CubeMetadataFetcher
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
    print("Make sure pydantic-ai is installed: pip install pydantic-ai")
    print("\nNote: Run this script from the orchestrator directory:")
    print("  cd orchestrator")
    print("  source venv/bin/activate")
    print("  python tests/test_ambiguity_agent.py")
    sys.exit(1)


class AmbiguityAgentDebugger:
    """
    Interactive debugger for the Query Ambiguity Assessor agent.
    Provides detailed insights into agent processing, tool usage, and state transitions.
    """

    def __init__(self,
                 model: str = "openai:gpt-4o",
                 verbose: bool = True,
                 debug: bool = False,
                 cube_base_url: str = "http://localhost:4000",
                 cube_api_secret: str = "baubeach",
                 use_real_metadata: bool = True):
        """
        Initialize the debugger.

        Args:
            model: Model identifier for the agent
            verbose: Enable verbose logging of agent internals
            debug: Enable minimalistic debug output (tool calls, prompts, states)
            cube_base_url: Cube.js API base URL
            cube_api_secret: Cube.js API secret for JWT generation
            use_real_metadata: If True, fetch metadata from Cube.js API; if False, use hardcoded sample
        """
        self.model = model
        self.verbose = verbose
        self.debug = debug
        self.cube_base_url = cube_base_url
        self.cube_api_secret = cube_api_secret
        self.use_real_metadata = use_real_metadata
        self.agent: Optional[QueryAmbiguityAssessor] = None
        self.session_id = f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_context: Optional[ConversationContext] = None
        self.state_history = []
        self.metadata_fetcher: Optional[CubeMetadataFetcher] = None
        self.cube_metadata: Optional[CubeMetadata] = None
        self.tool_calls = []
        self.prompt_history = []

        # Configure logging for agent debugging
        if verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # Enable debug logging for the agent
            logging.getLogger('orchestrator.agents.query_ambiguity_assessor').setLevel(logging.DEBUG)

    def _generate_jwt_token(self) -> str:
        """
        Generate JWT token for Cube.js API authentication.

        Returns:
            JWT token string
        """
        payload = {
            'iat': int(datetime.now().timestamp()),
            'exp': int((datetime.now() + timedelta(days=30)).timestamp())
        }
        return jwt.encode(payload, self.cube_api_secret, algorithm='HS256')

    def _fetch_cube_metadata(self) -> bool:
        """
        Fetch metadata from Cube.js API.

        Returns:
            True if metadata fetched successfully
        """
        try:
            print("🔍 Fetching metadata from Cube.js API...")
            print(f"   URL: {self.cube_base_url}")

            # Generate JWT token
            jwt_token = self._generate_jwt_token()

            # Initialize metadata fetcher
            self.metadata_fetcher = CubeMetadataFetcher(
                base_url=self.cube_base_url,
                jwt_token=jwt_token
            )

            # Fetch metadata
            result = self.metadata_fetcher.fetch_metadata(use_cache=False)

            if not result["success"]:
                print(f"❌ Failed to fetch metadata: {result.get('error')}")
                return False

            # Get metadata for EventPerformanceOverview view
            view_metadata = self.metadata_fetcher.get_view_metadata('EventPerformanceOverview')

            if not view_metadata.get('success'):
                print(f"❌ Failed to get EventPerformanceOverview metadata: {view_metadata.get('error')}")
                available_views = view_metadata.get('available_cubes', [])
                if available_views:
                    print(f"   Available views/cubes: {', '.join(available_views)}")
                return False

            # Convert to CubeMetadata format
            self.cube_metadata = CubeMetadata(
                view_name=view_metadata['view'],
                measures=view_metadata['measures'],
                dimensions=view_metadata['dimensions']
            )

            print(f"✅ Metadata fetched successfully")
            print(f"   View: {view_metadata['view']}")
            print(f"   Measures: {view_metadata['measures_count']}")
            print(f"   Dimensions: {view_metadata['dimensions_count']}")

            if self.verbose:
                print(f"\n📊 Available Measures:")
                for measure in view_metadata['measures'][:5]:  # Show first 5
                    print(f"   - {measure['name']}: {measure['title']}")
                if len(view_metadata['measures']) > 5:
                    print(f"   ... and {len(view_metadata['measures']) - 5} more")

                print(f"\n📏 Available Dimensions:")
                for dimension in view_metadata['dimensions'][:5]:  # Show first 5
                    print(f"   - {dimension['name']} ({dimension['type']}): {dimension['title']}")
                if len(view_metadata['dimensions']) > 5:
                    print(f"   ... and {len(view_metadata['dimensions']) - 5} more")

            print()
            return True

        except Exception as e:
            print(f"❌ Failed to fetch metadata: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def initialize_agent(self) -> bool:
        """
        Initialize the ambiguity assessor agent.

        Returns:
            True if initialization successful
        """
        try:
            print("🔧 Initializing Query Ambiguity Assessor Agent...")
            print(f"   Model: {self.model}")
            print(f"   Session ID: {self.session_id}")
            print(f"   Use Real Metadata: {self.use_real_metadata}")
            print()

            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("❌ OPENAI_API_KEY environment variable not set")
                return False

            # Fetch cube metadata if requested
            if self.use_real_metadata:
                if not self._fetch_cube_metadata():
                    print("⚠️  Falling back to hardcoded sample metadata")
                    self.cube_metadata = self.get_sample_cube_metadata()
                    self.use_real_metadata = False
            else:
                print("📝 Using hardcoded sample metadata")
                self.cube_metadata = self.get_sample_cube_metadata()

            # Initialize agent
            self.agent = QueryAmbiguityAssessor(
                model=self.model,
                api_key=api_key
            )

            # Initialize conversation context
            self.conversation_context = ConversationContext(
                session_id=self.session_id
            )

            # Wrap agent with debug hooks if debug mode enabled
            self._wrap_agent_with_debug_hooks()

            print("✅ Agent initialized successfully\n")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize agent: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_sample_cube_metadata(self) -> CubeMetadata:
        """
        Create sample cube metadata for testing.

        Returns:
            Sample CubeMetadata object
        """
        return CubeMetadata(
            view_name="EventPerformanceOverview",
            measures=[
                {
                    "name": "EventPerformanceOverview.total_order_value",
                    "title": "Total Revenue",
                    "description": "Sum of all order values across events"
                },
                {
                    "name": "EventPerformanceOverview.total_tickets_sold",
                    "title": "Total Tickets Sold",
                    "description": "Total number of tickets sold"
                },
                {
                    "name": "EventPerformanceOverview.avg_order_value",
                    "title": "Average Order Value",
                    "description": "Average value per order"
                },
                {
                    "name": "EventPerformanceOverview.count",
                    "title": "Order Count",
                    "description": "Total number of orders"
                }
            ],
            dimensions=[
                {
                    "name": "EventPerformanceOverview.event_name",
                    "title": "Event Name",
                    "description": "Name of the event",
                    "type": "string"
                },
                {
                    "name": "EventPerformanceOverview.venue_name",
                    "title": "Venue Name",
                    "description": "Name of the venue hosting the event",
                    "type": "string"
                },
                {
                    "name": "EventPerformanceOverview.payment_method",
                    "title": "Payment Method",
                    "description": "Method of payment used",
                    "type": "string"
                },
                {
                    "name": "EventPerformanceOverview.order_date",
                    "title": "Order Date",
                    "description": "Date when order was placed",
                    "type": "time"
                }
            ]
        )

    def display_sample_queries(self):
        """Display sample queries for testing different ambiguity scenarios."""
        print("\n" + "="*60)
        print("📋 SAMPLE TEST QUERIES")
        print("="*60)

        samples = [
            {
                "category": "🔴 Highly Ambiguous",
                "queries": [
                    "Show me total revenue",
                    "How many tickets?",
                    "List events"
                ]
            },
            {
                "category": "🟡 Partially Ambiguous",
                "queries": [
                    "Show revenue by event",
                    "Total tickets sold last month",
                    "Events with high revenue"
                ]
            },
            {
                "category": "🟢 Clear Queries",
                "queries": [
                    "Show me total revenue by event name for last month",
                    "List total tickets sold by venue for the past 7 days",
                    "Show average order value by payment method for 2024"
                ]
            }
        ]

        for sample in samples:
            print(f"\n{sample['category']}:")
            for i, query in enumerate(sample['queries'], 1):
                print(f"   {i}. {query}")

        print("\n" + "="*60 + "\n")

    def _wrap_agent_with_debug_hooks(self):
        """Wrap agent methods to intercept tool calls and state changes"""
        if not self.debug:
            return

        # Store original methods
        original_assess = self.agent.assess_query
        original_clarification = self.agent.request_clarification
        original_receive = self.agent.receive_clarification
        original_confirm = self.agent.confirm_query
        original_construct = self.agent.construct_api_call

        # Wrap assess_query
        async def wrapped_assess(*args, **kwargs):
            self._log_state_transition("QUERY_ASSESSMENT")
            self._log_prompt_usage("query_assessment")
            return await original_assess(*args, **kwargs)

        # Wrap request_clarification
        async def wrapped_clarification(*args, **kwargs):
            self._log_state_transition("CLARIFICATION_REQUEST")
            self._log_prompt_usage("clarification_request")
            return await original_clarification(*args, **kwargs)

        # Wrap receive_clarification
        async def wrapped_receive(*args, **kwargs):
            self._log_state_transition("RECEIVE_CLARIFICATION")
            self._log_prompt_usage("receive_clarification")
            return await original_receive(*args, **kwargs)

        # Wrap confirm_query
        async def wrapped_confirm(*args, **kwargs):
            self._log_state_transition("QUERY_CONFIRMATION")
            self._log_prompt_usage("query_confirmation")
            return await original_confirm(*args, **kwargs)

        # Wrap construct_api_call
        async def wrapped_construct(*args, **kwargs):
            self._log_state_transition("API_CALL_CONSTRUCTION")
            self._log_prompt_usage("api_call_construction")
            return await original_construct(*args, **kwargs)

        # Apply wrappers
        self.agent.assess_query = wrapped_assess
        self.agent.request_clarification = wrapped_clarification
        self.agent.receive_clarification = wrapped_receive
        self.agent.confirm_query = wrapped_confirm
        self.agent.construct_api_call = wrapped_construct

    def _log_state_transition(self, state: str):
        """Log state transition in debug mode"""
        if self.debug:
            print(f"  → State: {state}")

    def _log_prompt_usage(self, prompt_name: str):
        """Log prompt function usage in debug mode"""
        if self.debug:
            print(f"  → Prompt: {prompt_name}()")
            self.prompt_history.append(prompt_name)

    def _log_tool_call(self, tool_name: str, args: dict = None):
        """Log tool call in debug mode"""
        if self.debug:
            args_str = f"({', '.join(f'{k}={v}' for k, v in args.items())})" if args else "()"
            print(f"  → Tool: {tool_name}{args_str}")
            self.tool_calls.append({"tool": tool_name, "args": args or {}})

    async def assess_query_with_debug(self, user_query: str) -> AgentResponse:
        """
        Assess a query with detailed debugging output.

        Args:
            user_query: User's natural language query

        Returns:
            AgentResponse from the agent
        """
        if not self.debug:
            print("\n" + "="*60)
            print("🤖 ASSESSING QUERY")
            print("="*60)
            print(f"Query: '{user_query}'")
            print(f"State: {self.agent.current_state}")
            print()
        else:
            print(f"\n🔍 Query: '{user_query}'")

        # Track state before processing
        initial_state = self.agent.current_state

        # Use the cached cube metadata (fetched during initialization)
        if not self.cube_metadata:
            print("❌ Cube metadata not available. Agent not properly initialized.")
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error="Cube metadata not available"
            )

        try:
            # Call agent's assess_query method
            if not self.debug:
                print("🔄 Calling agent.assess_query()...")

            result = await self.agent.assess_query(
                user_query=user_query,
                session_id=self.session_id,
                cube_metadata=self.cube_metadata,
                conversation_context=self.conversation_context
            )

            # Record state transition
            self.state_history.append({
                "timestamp": datetime.now().isoformat(),
                "query": user_query,
                "initial_state": initial_state,
                "final_state": result.state,
                "response_type": result.response_type,
                "success": result.success
            })

            # Display results
            if not self.debug:
                self._display_assessment_result(result)
            else:
                self._display_debug_result(result)

            return result

        except Exception as e:
            print(f"❌ Error during assessment: {str(e)}")
            import traceback
            traceback.print_exc()
            return AgentResponse(
                success=False,
                state=AgentState.ERROR,
                response_type="error",
                data={},
                error=str(e)
            )

    def _display_assessment_result(self, result: AgentResponse):
        """
        Display assessment results in a structured format.

        Args:
            result: AgentResponse to display
        """
        print("\n" + "-"*60)
        print("📊 ASSESSMENT RESULT")
        print("-"*60)

        print(f"✅ Success: {result.success}")
        print(f"🔄 State: {result.state}")
        print(f"📋 Response Type: {result.response_type}")
        print()

        # Display data based on response type
        if result.response_type == "clarification":
            print("❓ CLARIFICATION REQUEST")
            print("-"*40)
            print(f"Question: {result.data.get('clarification_question', 'N/A')}")
            print(f"Ambiguous Aspect: {result.data.get('ambiguous_aspect', 'N/A')}")

            suggestions = result.data.get('suggestions', [])
            if suggestions:
                print(f"\n💡 Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")

        elif result.response_type == "confirmation":
            print("✅ QUERY CONFIRMATION")
            print("-"*40)
            print(f"Message: {result.data.get('confirmation_message', 'N/A')}")

            params = result.data.get('interpreted_parameters', {})
            if params:
                print(f"\n📋 Interpreted Parameters:")
                print(json.dumps(params, indent=2))

        elif result.response_type == "cube_query":
            print("🎯 CUBE QUERY CONSTRUCTED")
            print("-"*40)
            print(f"Description: {result.data.get('query_description', 'N/A')}")

            cube_query = result.data.get('cube_query', {})
            if cube_query:
                print(f"\n🔍 Cube Query:")
                print(json.dumps(cube_query, indent=2))

        elif result.response_type == "error":
            print("❌ ERROR")
            print("-"*40)
            print(f"Error: {result.error}")

        print()

    def _display_debug_result(self, result: AgentResponse):
        """Display minimalistic debug result"""
        if result.response_type == "confirmation":
            params = result.data.get('interpreted_parameters', {})
            print(f"✓ Confirmation ready")
            print(f"  Measures: {params.get('measures', [])}")
            if params.get('dimensions'):
                print(f"  Dimensions: {params.get('dimensions')}")
            if params.get('timeDimensions'):
                time_dims = params['timeDimensions']
                for td in time_dims:
                    print(f"  Time: {td.get('dimension')} (granularity: {td.get('granularity', 'null')})")
        elif result.response_type == "clarification":
            print(f"? Clarification needed: {result.data.get('ambiguous_aspect')}")
        elif result.response_type == "cube_query":
            print(f"✓ Cube query constructed")
        elif result.response_type == "error":
            print(f"✗ Error: {result.error}")
        print()

    def display_conversation_history(self):
        """Display the current conversation history."""
        if not self.conversation_context or not self.conversation_context.messages:
            print("📜 No conversation history yet\n")
            return

        print("\n" + "="*60)
        print("📜 CONVERSATION HISTORY")
        print("="*60)

        for i, message in enumerate(self.conversation_context.messages, 1):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')

            role_emoji = "👤" if role == "user" else "🤖"
            print(f"\n{i}. {role_emoji} {role.upper()} [{timestamp}]")
            print(f"   {content}")

        print()

    def display_state_history(self):
        """Display the state transition history."""
        if not self.state_history:
            print("🔄 No state transitions yet\n")
            return

        print("\n" + "="*60)
        print("🔄 STATE TRANSITION HISTORY")
        print("="*60)

        for i, state in enumerate(self.state_history, 1):
            print(f"\n{i}. [{state['timestamp']}]")
            print(f"   Query: '{state['query']}'")
            print(f"   {state['initial_state']} → {state['final_state']}")
            print(f"   Response: {state['response_type']} (Success: {state['success']})")

        print()

    def display_query_context(self):
        """Display the accumulated query context."""
        if not self.conversation_context or not self.conversation_context.query_context:
            print("📝 No query context accumulated yet\n")
            return

        print("\n" + "="*60)
        print("📝 ACCUMULATED QUERY CONTEXT")
        print("="*60)
        print(json.dumps(self.conversation_context.query_context, indent=2))
        print()

    async def interactive_test_loop(self):
        """
        Run an interactive test loop allowing multiple queries.
        """
        print("\n" + "="*60)
        print("🚀 INTERACTIVE AMBIGUITY AGENT DEBUGGER")
        print("="*60)

        # Initialize agent
        if not self.initialize_agent():
            return False

        # Display sample queries
        self.display_sample_queries()

        print("💭 Enter queries to test the agent's ambiguity detection")
        print("Commands:")
        print("   - Type your query to test")
        print("   - 'history' to see conversation history")
        print("   - 'states' to see state transition history")
        print("   - 'context' to see accumulated query context")
        print("   - 'clear' to start a new session")
        print("   - 'exit' or 'quit' to stop\n")

        while True:
            try:
                # Get user input
                user_input = input("🤔 Your query: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\n👋 Exiting debugger...")
                    break

                elif user_input.lower() == 'history':
                    self.display_conversation_history()
                    continue

                elif user_input.lower() == 'states':
                    self.display_state_history()
                    continue

                elif user_input.lower() == 'context':
                    self.display_query_context()
                    continue

                elif user_input.lower() == 'clear':
                    print("\n🔄 Starting new session...")
                    self.conversation_context = ConversationContext(
                        session_id=f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    self.state_history = []
                    print("✅ Session cleared\n")
                    continue

                # Process query
                result = await self.assess_query_with_debug(user_input)

                # If clarification needed, optionally allow user to respond
                if result.response_type == "clarification":
                    print("\n💬 You can provide clarification or enter a new query")

                print()

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                break

            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()

        return True


async def main():
    """
    Main entry point for the interactive test.
    """
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Interactive debugger for Query Ambiguity Assessor agent"
    )
    parser.add_argument(
        '--model',
        type=str,
        default='openai:gpt-4o',
        help='Model to use (default: openai:gpt-4o)'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Single query to test (non-interactive mode)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable minimalistic debug output (tool calls, prompts, states)'
    )
    parser.add_argument(
        '--use-sample-metadata',
        action='store_true',
        help='Use hardcoded sample metadata instead of fetching from Cube.js API'
    )
    parser.add_argument(
        '--cube-url',
        type=str,
        default='http://localhost:4000',
        help='Cube.js API base URL (default: http://localhost:4000)'
    )
    parser.add_argument(
        '--cube-secret',
        type=str,
        default='baubeach',
        help='Cube.js API secret for JWT generation (default: baubeach)'
    )

    args = parser.parse_args()

    # Create debugger
    debugger = AmbiguityAgentDebugger(
        model=args.model,
        verbose=args.verbose,
        debug=args.debug,
        cube_base_url=args.cube_url,
        cube_api_secret=args.cube_secret,
        use_real_metadata=not args.use_sample_metadata
    )

    # Run in interactive or single-query mode
    if args.query:
        # Single query mode
        print(f"🎯 Testing single query: '{args.query}'\n")

        if not debugger.initialize_agent():
            return False

        result = await debugger.assess_query_with_debug(args.query)

        print("\n" + "="*60)
        print("📊 FINAL RESULT")
        print("="*60)
        print(f"Success: {result.success}")
        print(f"State: {result.state}")
        print(f"Response Type: {result.response_type}")

        if result.error:
            print(f"Error: {result.error}")

        return result.success

    else:
        # Interactive mode
        return await debugger.interactive_test_loop()


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
