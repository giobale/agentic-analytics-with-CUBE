# ABOUTME: Interactive test for the complete orchestrator pipeline
# ABOUTME: Tests natural language query processing from user input to CUBE results

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from orchestrator import QueryOrchestrator, QueryOrchestratorError


class OrchestratorInteractiveTest:
    """
    Interactive test for the complete orchestrator pipeline.
    Simulates a real user conversation flow with the system.
    """

    def __init__(self):
        """Initialize the test environment."""
        self.orchestrator = None
        self.test_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sample questions based on EventPerformanceOverview YML structure
        self.sample_questions = [
            {
                "question": "Show me the total revenue and tickets sold for each event",
                "description": "Gets revenue metrics (total_order_value, total_tickets_sold) grouped by event name",
                "expected_measures": ["EventPerformanceOverview.total_order_value", "EventPerformanceOverview.total_tickets_sold"],
                "expected_dimensions": ["EventPerformanceOverview.event_name"]
            },
            {
                "question": "Which events have the highest average order value?",
                "description": "Shows average order value by event, useful for identifying premium events",
                "expected_measures": ["EventPerformanceOverview.avg_order_value"],
                "expected_dimensions": ["EventPerformanceOverview.event_name"]
            },
            {
                "question": "What is the payment method breakdown for all events?",
                "description": "Analyzes payment methods used across events",
                "expected_measures": ["EventPerformanceOverview.count"],
                "expected_dimensions": ["EventPerformanceOverview.payment_method"]
            }
        ]

    def run_interactive_test(self):
        """
        Run the complete interactive test workflow.
        """
        print("🚀 ORCHESTRATOR INTERACTIVE TEST")
        print("=" * 50)
        print(f"Test Session ID: {self.test_session_id}")
        print()

        try:
            # Step 1: Initialize orchestrator
            if not self._initialize_orchestrator():
                return False

            # Step 2: Display available questions
            self._display_sample_questions()

            # Step 3: Get user input
            user_query = self._get_user_input()
            if not user_query:
                print("❌ Test cancelled by user")
                return False

            # Step 4: Process query through orchestrator
            result = self._process_user_query(user_query)

            # Step 5: Display results
            self._display_results(result)

            # Step 6: Optional: Continue conversation
            self._handle_follow_up()

            print(f"\n🎉 Interactive test completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _initialize_orchestrator(self) -> bool:
        """
        Initialize the orchestrator and validate all components.

        Returns:
            True if initialization successful
        """
        print("🔧 Initializing Orchestrator...")

        try:
            self.orchestrator = QueryOrchestrator()
            init_result = self.orchestrator.initialize()

            print(f"📊 Initialization Result:")
            print(f"   Success: {init_result['success']}")

            if init_result['success']:
                components = init_result['components']
                print(f"   ✅ CUBE Client: Connected")
                print(f"   ✅ LLM Client: {components['llm_client']['model']}")
                print(f"   ✅ System Prompt: {components['system_prompt']['length']} chars")
                print(f"   ✅ Available Cubes: {components['system_prompt']['metadata']['views_count']} views")
                return True
            else:
                print("❌ Initialization failed:")
                for error in init_result['errors']:
                    print(f"   - {error}")
                return False

        except Exception as e:
            print(f"❌ Initialization error: {str(e)}")
            return False

    def _display_sample_questions(self):
        """Display sample questions to help user get started."""
        print("\n📋 SAMPLE QUESTIONS ABOUT EVENT DATA")
        print("-" * 40)

        for i, sample in enumerate(self.sample_questions, 1):
            print(f"{i}. {sample['question']}")
            print(f"   💡 {sample['description']}")
            print()

        print("💭 Or ask your own question about events, revenue, tickets, or payment methods!")
        print()

    def _get_user_input(self) -> str:
        """
        Get user query input with validation.

        Returns:
            User query string or empty string if cancelled
        """
        print("🤔 ENTER YOUR QUESTION")
        print("-" * 25)

        while True:
            try:
                user_input = input("Your question about events data: ").strip()

                if user_input.lower() in ['exit', 'quit', 'cancel']:
                    return ""

                if len(user_input) < 5:
                    print("⚠️  Please enter a more detailed question (at least 5 characters)")
                    continue

                # Confirm the question
                print(f"\n✅ You asked: '{user_input}'")
                confirm = input("Proceed with this question? (y/n): ").strip().lower()

                if confirm in ['y', 'yes']:
                    return user_input
                else:
                    print("Please enter your question again:")
                    continue

            except KeyboardInterrupt:
                print("\n\n❌ Test cancelled by user")
                return ""

    def _process_user_query(self, user_query: str) -> dict:
        """
        Process user query through the orchestrator pipeline.

        Args:
            user_query: User's natural language question

        Returns:
            Processing result dictionary
        """
        print(f"\n🤖 PROCESSING QUERY")
        print("-" * 20)
        print(f"Query: {user_query}")

        # Process query through orchestrator
        result = self.orchestrator.process_query(user_query)

        print(f"Pipeline Success: {result['success']}")
        print(f"Response Type: {result.get('response_type', 'unknown')}")

        # Display pipeline steps
        if 'pipeline_steps' in result:
            steps = result['pipeline_steps']
            print(f"\n📋 Pipeline Steps:")

            if 'llm_processing' in steps:
                llm_result = steps['llm_processing']
                print(f"   🧠 LLM Processing: {'✅' if llm_result['success'] else '❌'}")
                if llm_result['success']:
                    usage = llm_result.get('usage', {})
                    print(f"      Tokens: {usage.get('total_tokens', 'N/A')}")

            if 'cube_execution' in steps:
                cube_result = steps['cube_execution']
                print(f"   🎯 CUBE Execution: {'✅' if cube_result['success'] else '❌'}")
                if cube_result['success']:
                    print(f"      Rows: {cube_result.get('row_count', 'N/A')}")
                    print(f"      CSV: {cube_result.get('csv_filename', 'N/A')}")

        return result

    def _display_results(self, result: dict):
        """
        Display query processing results in a user-friendly format.

        Args:
            result: Processing result from orchestrator
        """
        print(f"\n📊 QUERY RESULTS")
        print("=" * 30)

        response_type = result.get('response_type')

        if response_type == "data_result":
            # Successful data query
            llm_response = result.get('llm_response', {})

            print(f"🎯 Query Interpretation:")
            print(f"   {llm_response.get('interpretation', 'No interpretation available')}")
            print()

            print(f"📋 Description:")
            print(f"   {llm_response.get('description', 'No description available')}")
            print()

            # Display CUBE query that was executed
            cube_query = llm_response.get('cube_query', {})
            print(f"🔍 Generated CUBE Query:")
            print(f"   Measures: {cube_query.get('measures', [])}")
            print(f"   Dimensions: {cube_query.get('dimensions', [])}")
            if cube_query.get('filters'):
                print(f"   Filters: {cube_query.get('filters', [])}")
            print()

            # Display data results
            cube_data = result.get('cube_data', [])
            print(f"📈 Query Results ({result.get('row_count', 0)} rows):")

            if cube_data:
                # Display first few rows
                max_display_rows = 5
                for i, row in enumerate(cube_data[:max_display_rows]):
                    print(f"   Row {i+1}: {row}")

                if len(cube_data) > max_display_rows:
                    print(f"   ... and {len(cube_data) - max_display_rows} more rows")
            else:
                print("   No data returned")

            print()
            print(f"💾 Full results saved to: {result.get('csv_filename', 'N/A')}")

        elif response_type == "clarification":
            # LLM needs clarification
            llm_response = result.get('llm_response', {})

            print(f"❓ Clarification Needed:")
            print(f"   {llm_response.get('interpretation', 'Need more information')}")
            print()

            questions = llm_response.get('clarification_questions', [])
            if questions:
                print(f"❓ Please clarify:")
                for i, question in enumerate(questions, 1):
                    print(f"   {i}. {question}")
                print()

            suggestions = llm_response.get('suggestions', [])
            if suggestions:
                print(f"💡 Suggestions:")
                for suggestion in suggestions:
                    print(f"   - {suggestion}")

        elif response_type == "cube_error":
            # CUBE execution failed
            print(f"❌ CUBE Query Error:")
            cube_error = result.get('cube_error', {})
            print(f"   Error: {cube_error.get('error', 'Unknown error')}")
            print(f"   Details: {cube_error.get('details', 'No details available')}")

        else:
            # Other error types
            print(f"❌ Processing Error:")
            print(f"   Type: {response_type}")
            print(f"   Error: {result.get('error', 'Unknown error')}")

    def _handle_follow_up(self):
        """Handle follow-up questions or conversation continuation."""
        print(f"\n🔄 FOLLOW-UP OPTIONS")
        print("-" * 25)

        try:
            # Show conversation history
            history = self.orchestrator.get_conversation_history()
            print(f"📜 Conversation: {len(history)} messages in history")

            follow_up = input("\nAsk another question? (y/n): ").strip().lower()

            if follow_up in ['y', 'yes']:
                print("\n" + "="*50)
                follow_up_query = self._get_user_input()

                if follow_up_query:
                    follow_up_result = self._process_user_query(follow_up_query)
                    self._display_results(follow_up_result)

        except KeyboardInterrupt:
            print("\n\n💬 Conversation ended by user")

    def get_orchestrator_status(self):
        """Display current orchestrator status for debugging."""
        if self.orchestrator:
            status = self.orchestrator.get_status()
            print(f"\n🔍 ORCHESTRATOR STATUS")
            print("-" * 30)
            print(json.dumps(status, indent=2))


def main():
    """
    Run the interactive orchestrator test.
    """
    print("🎯 Starting Interactive Orchestrator Test")
    print("This test will walk you through the complete query pipeline.\n")

    test = OrchestratorInteractiveTest()
    success = test.run_interactive_test()

    if not success:
        print("\n🔍 Use test.get_orchestrator_status() for debugging information")
        return False

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)