# ABOUTME: Main orchestrator for natural language to CUBE query processing
# ABOUTME: Coordinates system prompt generation, LLM interaction, conversation memory, and CUBE execution

import sys
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # For development: Load .env file from the project root
    # For containers: Use environment variables passed by Docker Compose
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    # In containers, this will use environment variables set by Docker Compose
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables only.")

# Add system-prompt-generator to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'system-prompt-generator'))

from conversation_manager import ConversationManager, ConversationManagerError
from llm_client import LLMClient, LLMClientError
from cube_client import CubeClient, CubeClientError

# Import system prompt generator
try:
    from system_prompt_generator.context_preparation.context_manager import ContextManager
except ImportError:
    # Fallback import path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'system-prompt-generator', 'context_preparation'))
    from context_manager import ContextManager


class QueryOrchestrator:
    """
    Main orchestrator for natural language to CUBE query processing.
    Coordinates all components to provide a complete query processing pipeline.
    """

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 cube_base_url: str = "http://localhost:4000",
                 cube_api_secret: str = "baubeach",
                 max_conversation_messages: int = 6):
        """
        Initialize the query orchestrator.

        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            cube_base_url: CUBE API base URL
            cube_api_secret: CUBE API secret
            max_conversation_messages: Maximum conversation history to maintain
        """
        # Initialize components
        self.conversation_manager = ConversationManager(max_conversation_messages)
        self.llm_client = LLMClient(api_key=openai_api_key)
        self.cube_client = CubeClient(base_url=cube_base_url, api_secret=cube_api_secret)

        # Initialize system prompt generator
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'system-prompt-generator')
        self.context_manager = ContextManager(system_prompt_path)

        # Cache configuration
        self.cache_dir = os.getenv("CACHE_DIR", "/app/cache")
        self.system_prompt_cache_file = os.path.join(self.cache_dir, "system_prompt.txt")
        self.system_prompt_metadata_file = os.path.join(self.cache_dir, "system_prompt_metadata.json")

        # Orchestrator state
        self.is_initialized = False
        self.system_prompt = None
        self.system_prompt_metadata = None
        self.initialization_errors = []

    def _load_cached_system_prompt(self) -> Dict[str, Any]:
        """
        Load system prompt from cache if available.

        Returns:
            Result dictionary with success status and loaded content
        """
        try:
            if os.path.exists(self.system_prompt_cache_file):
                with open(self.system_prompt_cache_file, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()

                # Load metadata if available
                if os.path.exists(self.system_prompt_metadata_file):
                    with open(self.system_prompt_metadata_file, 'r', encoding='utf-8') as f:
                        self.system_prompt_metadata = json.load(f)
                else:
                    self.system_prompt_metadata = {
                        "loaded_from_cache": True,
                        "cache_file": self.system_prompt_cache_file
                    }

                return {
                    "success": True,
                    "source": "cache",
                    "length": len(self.system_prompt),
                    "metadata": self.system_prompt_metadata
                }
            else:
                return {
                    "success": False,
                    "source": "cache",
                    "error": "Cache file not found"
                }
        except Exception as e:
            return {
                "success": False,
                "source": "cache",
                "error": f"Failed to load cached system prompt: {str(e)}"
            }

    def _save_system_prompt_cache(self, system_prompt: str, metadata: Dict[str, Any]) -> bool:
        """
        Save system prompt to cache.

        Args:
            system_prompt: The system prompt text
            metadata: Metadata about the system prompt

        Returns:
            True if saved successfully
        """
        try:
            # Ensure cache directory exists
            os.makedirs(self.cache_dir, exist_ok=True)

            # Save system prompt
            with open(self.system_prompt_cache_file, 'w', encoding='utf-8') as f:
                f.write(system_prompt)

            # Save metadata
            cache_metadata = {
                **metadata,
                "cached_at": datetime.now().isoformat(),
                "cache_file": self.system_prompt_cache_file
            }

            with open(self.system_prompt_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(cache_metadata, f, indent=2)

            self.system_prompt_metadata = cache_metadata
            return True

        except Exception as e:
            print(f"Warning: Failed to save system prompt cache: {str(e)}")
            return False

    def reload_system_prompt_cache(self) -> Dict[str, Any]:
        """
        Manually reload system prompt from cache.

        Returns:
            Reload result with status information
        """
        result = self._load_cached_system_prompt()

        if result["success"]:
            return {
                "success": True,
                "message": "System prompt reloaded from cache",
                "length": len(self.system_prompt),
                "metadata": self.system_prompt_metadata,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Failed to reload system prompt from cache",
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize all components and generate system prompt.

        Returns:
            Initialization result with status and component details
        """
        initialization_result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "errors": []
        }

        try:
            # Initialize CUBE client
            cube_init = self.cube_client.initialize()
            initialization_result["components"]["cube_client"] = cube_init

            if not cube_init["success"]:
                initialization_result["errors"].append(f"CUBE initialization failed: {cube_init['error']}")

            # Validate LLM client
            llm_valid = self.llm_client.validate_api_key()
            initialization_result["components"]["llm_client"] = {
                "success": llm_valid,
                "model": self.llm_client.model
            }

            if not llm_valid:
                initialization_result["errors"].append("OpenAI API key validation failed")

            # Load or generate system prompt
            try:
                # First, try to load from cache
                cache_result = self._load_cached_system_prompt()

                if cache_result["success"]:
                    # Successfully loaded from cache
                    initialization_result["components"]["system_prompt"] = {
                        "success": True,
                        "source": "cache",
                        "length": len(self.system_prompt),
                        "metadata": cache_result["metadata"]
                    }
                else:
                    # Cache failed, generate new system prompt
                    prompt_result = self.context_manager.generate_system_prompt()
                    self.system_prompt = prompt_result["system_prompt"]

                    # Save to cache for future use
                    self._save_system_prompt_cache(self.system_prompt, prompt_result["metadata"])

                    initialization_result["components"]["system_prompt"] = {
                        "success": True,
                        "source": "generated",
                        "length": len(self.system_prompt),
                        "metadata": prompt_result["metadata"],
                        "cached": True
                    }

            except Exception as e:
                initialization_result["errors"].append(f"System prompt initialization failed: {str(e)}")
                initialization_result["components"]["system_prompt"] = {
                    "success": False,
                    "error": str(e)
                }

            # Overall success determination
            self.is_initialized = (
                cube_init["success"] and
                llm_valid and
                self.system_prompt is not None
            )

            initialization_result["success"] = self.is_initialized
            self.initialization_errors = initialization_result["errors"]

            return initialization_result

        except Exception as e:
            initialization_result["errors"].append(f"Unexpected initialization error: {str(e)}")
            return initialization_result

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a natural language query through the complete pipeline.

        Args:
            user_query: User's natural language question

        Returns:
            Complete processing result with LLM response and CUBE data if applicable
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Orchestrator not initialized",
                "details": "Call initialize() first",
                "initialization_errors": self.initialization_errors
            }

        processing_result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "pipeline_steps": {}
        }

        try:
            # Step 1: Add user message to conversation
            self.conversation_manager.add_user_message(user_query)
            processing_result["pipeline_steps"]["conversation_updated"] = True

            # Step 2: Get conversation messages for LLM
            conversation_messages = self.conversation_manager.get_openai_messages(self.system_prompt)
            processing_result["pipeline_steps"]["conversation_prepared"] = {
                "message_count": len(conversation_messages)
            }

            # Step 3: Process query with LLM
            llm_result = self.llm_client.process_query(
                user_query=user_query,
                system_prompt=self.system_prompt,
                conversation_messages=conversation_messages
            )

            processing_result["pipeline_steps"]["llm_processing"] = llm_result

            if not llm_result["success"]:
                processing_result["error"] = "LLM processing failed"
                processing_result["details"] = llm_result.get("response", {})
                return processing_result

            llm_response = llm_result["response"]

            # Step 4: Add LLM response to conversation
            self.conversation_manager.add_assistant_message(llm_response)

            # Step 5: Handle different response types
            response_type = llm_response.get("response_type")

            if response_type == "cube_query":
                # Execute CUBE query
                cube_query = llm_response.get("cube_query")
                cube_result = self.cube_client.execute_query(cube_query, user_query)

                processing_result["pipeline_steps"]["cube_execution"] = cube_result

                if cube_result["success"]:
                    processing_result.update({
                        "success": True,
                        "response_type": "data_result",
                        "llm_response": llm_response,
                        "cube_data": cube_result["data"],
                        "csv_filename": cube_result["csv_filename"],
                        "csv_path": cube_result["csv_path"],
                        "row_count": cube_result["row_count"]
                    })
                else:
                    processing_result.update({
                        "success": False,
                        "response_type": "cube_error",
                        "error": "CUBE query execution failed",
                        "llm_response": llm_response,
                        "cube_error": cube_result
                    })

            elif response_type == "clarification_needed":
                processing_result.update({
                    "success": True,
                    "response_type": "clarification",
                    "llm_response": llm_response,
                    "clarification_questions": llm_response.get("clarification_questions", []),
                    "suggestions": llm_response.get("suggestions", [])
                })

            elif response_type == "error":
                processing_result.update({
                    "success": False,
                    "response_type": "llm_error",
                    "error": "LLM reported an error",
                    "llm_response": llm_response
                })

            else:
                processing_result.update({
                    "success": False,
                    "response_type": "unknown",
                    "error": f"Unknown response type: {response_type}",
                    "llm_response": llm_response
                })

            return processing_result

        except Exception as e:
            processing_result.update({
                "success": False,
                "error": f"Pipeline processing failed: {str(e)}",
                "details": "Unexpected error in query processing pipeline"
            })
            return processing_result

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get current conversation history.

        Returns:
            List of conversation messages
        """
        return self.conversation_manager.export_conversation()

    def clear_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_manager.clear_conversation()

    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status and component health.

        Returns:
            Status information for all components
        """
        return {
            "orchestrator": {
                "initialized": self.is_initialized,
                "initialization_errors": self.initialization_errors,
                "has_system_prompt": self.system_prompt is not None
            },
            "conversation": self.conversation_manager.get_conversation_context(),
            "cube_client": self.cube_client.get_connection_status(),
            "llm_client": {
                "model": self.llm_client.model,
                "api_key_configured": bool(self.llm_client.api_key)
            },
            "timestamp": datetime.now().isoformat()
        }

    def regenerate_system_prompt(self) -> Dict[str, Any]:
        """
        Regenerate system prompt (useful when YML files are updated).

        Returns:
            Prompt regeneration result
        """
        try:
            prompt_result = self.context_manager.generate_system_prompt()
            self.system_prompt = prompt_result["system_prompt"]

            return {
                "success": True,
                "new_prompt_length": len(self.system_prompt),
                "metadata": prompt_result["metadata"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to regenerate system prompt: {str(e)}"
            }

    def get_available_cubes(self) -> List[str]:
        """
        Get list of available CUBE cubes.

        Returns:
            List of cube names
        """
        return self.cube_client.get_available_cubes()

    def validate_cube_query(self, cube_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a CUBE query without executing it.

        Args:
            cube_query: CUBE query to validate

        Returns:
            Validation result
        """
        return self.cube_client.validate_cube_query(cube_query)


class QueryOrchestratorError(Exception):
    """Custom exception for query orchestrator errors."""
    pass