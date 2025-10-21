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
from cube_query_validator import CubeQueryValidator, CubeQueryValidatorError
from cube_metadata_fetcher import CubeMetadataFetcher, CubeMetadataFetcherError

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
                 max_conversation_messages: int = 6,
                 view_yml_path: Optional[str] = None,
                 max_validation_retries: int = 2,
                 use_dynamic_metadata: bool = True):
        """
        Initialize the query orchestrator.

        Args:
            openai_api_key: OpenAI API key (defaults to env var)
            cube_base_url: CUBE API base URL
            cube_api_secret: CUBE API secret
            max_conversation_messages: Maximum conversation history to maintain
            view_yml_path: Path to view YML file for validation (auto-detected if None)
            max_validation_retries: Maximum retries for LLM to fix invalid parameters
            use_dynamic_metadata: If True, fetch metadata from Cube API; if False, use static YAML
        """
        # Store configuration
        self.cube_base_url = cube_base_url
        self.cube_api_secret = cube_api_secret
        self.use_dynamic_metadata = use_dynamic_metadata

        # Initialize components
        self.conversation_manager = ConversationManager(max_conversation_messages)
        self.llm_client = LLMClient(api_key=openai_api_key)
        self.cube_client = CubeClient(base_url=cube_base_url, api_secret=cube_api_secret)

        # Cache configuration
        self.cache_dir = os.getenv("CACHE_DIR", "/app/cache")
        self.system_prompt_cache_file = os.path.join(self.cache_dir, "system_prompt.txt")
        self.system_prompt_metadata_file = os.path.join(self.cache_dir, "system_prompt_metadata.json")

        # Initialize metadata fetcher (will be set up during initialization)
        self.metadata_fetcher = None

        # Initialize system prompt generator (will be configured during initialization)
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'system-prompt-generator')
        self.system_prompt_base_path = system_prompt_path
        self.context_manager = None

        # Validation configuration
        self.max_validation_retries = max_validation_retries
        self.view_yml_path = view_yml_path or os.path.join(
            os.path.dirname(__file__),
            'system-prompt-generator',
            'my-cube-views',
            'event_performance_overview.yml'
        )
        self.query_validator = None

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

            # Initialize metadata fetcher if using dynamic metadata
            if self.use_dynamic_metadata:
                try:
                    self.metadata_fetcher = CubeMetadataFetcher(
                        base_url=self.cube_base_url,
                        jwt_token=self.cube_client.jwt_token,
                        cache_dir=self.cache_dir
                    )

                    # Fetch metadata from Cube API
                    metadata_result = self.metadata_fetcher.fetch_metadata(use_cache=True)

                    if metadata_result["success"]:
                        initialization_result["components"]["metadata_fetcher"] = {
                            "success": True,
                            "source": metadata_result["source"],
                            "timestamp": metadata_result["timestamp"]
                        }
                        print(f"✅ Metadata fetched from {metadata_result['source']}")
                    else:
                        initialization_result["errors"].append(f"Metadata fetch failed: {metadata_result.get('error')}")
                        initialization_result["components"]["metadata_fetcher"] = {
                            "success": False,
                            "error": metadata_result.get("error")
                        }
                        # Don't fail initialization, will fallback to YAML
                        print(f"⚠️  Metadata fetch failed, will use static YAML fallback")
                        self.use_dynamic_metadata = False

                except Exception as e:
                    initialization_result["errors"].append(f"Metadata fetcher initialization failed: {str(e)}")
                    initialization_result["components"]["metadata_fetcher"] = {
                        "success": False,
                        "error": str(e)
                    }
                    # Fallback to static YAML
                    self.use_dynamic_metadata = False
                    print(f"⚠️  Metadata fetcher failed, using static YAML fallback")

            # Initialize context manager with metadata fetcher
            self.context_manager = ContextManager(
                base_path=self.system_prompt_base_path,
                cube_metadata_fetcher=self.metadata_fetcher if self.use_dynamic_metadata else None
            )

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

            # Initialize query validator
            try:
                if self.use_dynamic_metadata and self.metadata_fetcher:
                    # Use dynamic metadata for validator
                    print(f"🔍 DEBUG: Initializing query validator with dynamic metadata")
                    # Get metadata for the primary view (EventPerformanceOverview)
                    view_metadata = self.metadata_fetcher.get_view_metadata('EventPerformanceOverview')

                    if view_metadata.get('success'):
                        # Convert to validator-compatible format
                        # Strip cube prefix from field names (EventPerformanceOverview.revenues -> revenues)
                        measures_without_prefix = []
                        for measure in view_metadata['measures']:
                            field_name = measure['name']
                            # Remove prefix if present
                            if '.' in field_name:
                                field_name = field_name.split('.', 1)[1]
                            measures_without_prefix.append({
                                'name': field_name,
                                'title': measure.get('title', ''),
                                'description': measure.get('description', '')
                            })

                        dimensions_without_prefix = []
                        for dimension in view_metadata['dimensions']:
                            field_name = dimension['name']
                            # Remove prefix if present
                            if '.' in field_name:
                                field_name = field_name.split('.', 1)[1]
                            dimensions_without_prefix.append({
                                'name': field_name,
                                'title': dimension.get('title', ''),
                                'description': dimension.get('description', ''),
                                'type': dimension.get('type', '')  # Include type for time dimension validation
                            })

                        validator_metadata = {
                            'name': view_metadata['view'],
                            'title': view_metadata.get('title', ''),
                            'description': view_metadata.get('description', ''),
                            'measures': measures_without_prefix,
                            'dimensions': dimensions_without_prefix
                        }

                        self.query_validator = CubeQueryValidator(metadata_dict=validator_metadata)
                        schema_summary = self.query_validator.get_schema_summary()
                        print(f"✅ Query validator initialized with dynamic metadata")
                        print(f"   Cube: {schema_summary['cube_name']}")
                        print(f"   Measures: {len(schema_summary['measures'])} ({', '.join(schema_summary['measures'][:3])}...)")
                        print(f"   Dimensions: {len(schema_summary['dimensions'])} ({', '.join(schema_summary['dimensions'][:3])}...)")
                        initialization_result["components"]["query_validator"] = {
                            "success": True,
                            "source": "dynamic_metadata",
                            "schema_summary": schema_summary
                        }
                    else:
                        # Fallback to YAML if metadata fetch failed
                        print(f"⚠️  Failed to get view metadata: {view_metadata.get('error')}")
                        print(f"🔍 DEBUG: Falling back to YAML validator")
                        self.query_validator = CubeQueryValidator(view_yml_path=self.view_yml_path)
                        schema_summary = self.query_validator.get_schema_summary()
                        print(f"✅ Query validator initialized from YAML (fallback)")
                        initialization_result["components"]["query_validator"] = {
                            "success": True,
                            "source": "yaml_fallback",
                            "view_yml_path": self.view_yml_path,
                            "schema_summary": schema_summary
                        }
                else:
                    # Use static YAML validator
                    print(f"🔍 DEBUG: Initializing query validator with YAML: {self.view_yml_path}")
                    self.query_validator = CubeQueryValidator(view_yml_path=self.view_yml_path)
                    schema_summary = self.query_validator.get_schema_summary()
                    print(f"✅ Query validator initialized successfully from YAML")
                    print(f"   Cube: {schema_summary['cube_name']}")
                    print(f"   Measures: {len(schema_summary['measures'])} ({', '.join(schema_summary['measures'][:3])}...)")
                    print(f"   Dimensions: {len(schema_summary['dimensions'])} ({', '.join(schema_summary['dimensions'][:3])}...)")
                    initialization_result["components"]["query_validator"] = {
                        "success": True,
                        "source": "yaml",
                        "view_yml_path": self.view_yml_path,
                        "schema_summary": schema_summary
                    }
            except Exception as e:
                print(f"❌ Query validator initialization failed: {str(e)}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
                initialization_result["errors"].append(f"Query validator initialization failed: {str(e)}")
                initialization_result["components"]["query_validator"] = {
                    "success": False,
                    "error": str(e)
                }
                # Don't block orchestrator initialization, continue without validator
                self.query_validator = None

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
                # Validate and execute CUBE query with retry logic
                cube_query = llm_response.get("cube_query")

                print(f"🔍 DEBUG: Starting cube query validation and execution")
                print(f"   Query validator available: {self.query_validator is not None}")
                print(f"   Cube query: {json.dumps(cube_query, indent=2)}")

                # Try to validate and execute query with retries
                validation_attempts = 0
                query_executed_successfully = False

                while validation_attempts <= self.max_validation_retries and not query_executed_successfully:
                    # Validate query parameters
                    if self.query_validator:
                        print(f"🔍 DEBUG: Validating query (attempt {validation_attempts + 1})...")
                        validation_result = self.query_validator.validate_query(cube_query)
                        processing_result["pipeline_steps"][f"validation_attempt_{validation_attempts + 1}"] = validation_result

                        if not validation_result["valid"]:
                            # Query has invalid parameters
                            if validation_attempts < self.max_validation_retries:
                                # Generate correction prompt for LLM
                                correction_prompt = self.query_validator.generate_correction_prompt(
                                    validation_result,
                                    user_query
                                )

                                # Ask LLM to fix the query
                                print(f"  ⚠️  Query validation failed (attempt {validation_attempts + 1}), asking LLM to correct...")
                                retry_result = self.llm_client.process_query(
                                    user_query=correction_prompt,
                                    system_prompt=self.system_prompt,
                                    conversation_messages=[]  # Fresh context for correction
                                )

                                processing_result["pipeline_steps"][f"llm_correction_attempt_{validation_attempts + 1}"] = retry_result

                                if retry_result["success"] and retry_result["response"].get("response_type") == "cube_query":
                                    # Update cube_query with corrected version
                                    cube_query = retry_result["response"].get("cube_query")
                                    llm_response = retry_result["response"]
                                    validation_attempts += 1
                                else:
                                    # LLM failed to correct, break retry loop
                                    break
                            else:
                                # Max retries reached
                                processing_result.update({
                                    "success": False,
                                    "response_type": "validation_error",
                                    "error": "Query validation failed after maximum retries",
                                    "validation_result": validation_result,
                                    "llm_response": llm_response
                                })
                                return processing_result
                        else:
                            # Validation passed, proceed with execution
                            query_executed_successfully = True
                    else:
                        # No validator, proceed directly
                        query_executed_successfully = True

                    # Execute query if validation passed
                    if query_executed_successfully:
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
                                "row_count": cube_result["row_count"],
                                "validation_attempts": validation_attempts + 1
                            })
                        else:
                            # Check if it's a schema error that could be fixed with retry
                            if "not found" in cube_result.get("error", "").lower():
                                # This might be a validation issue that slipped through
                                if validation_attempts < self.max_validation_retries:
                                    query_executed_successfully = False
                                    validation_attempts += 1
                                else:
                                    processing_result.update({
                                        "success": False,
                                        "response_type": "cube_error",
                                        "error": "CUBE query execution failed",
                                        "llm_response": llm_response,
                                        "cube_error": cube_result
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

            # Update cache
            self._save_system_prompt_cache(self.system_prompt, prompt_result["metadata"])

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

    def refresh_cube_metadata(self) -> Dict[str, Any]:
        """
        Refresh Cube metadata from API and regenerate system prompt.
        This method is called when the user manually triggers a metadata refresh.

        Returns:
            Refresh result with status and details
        """
        if not self.use_dynamic_metadata or not self.metadata_fetcher:
            return {
                "success": False,
                "error": "Dynamic metadata is not enabled",
                "details": "Orchestrator is configured to use static YAML files"
            }

        try:
            # Clear metadata cache
            self.metadata_fetcher.clear_cache()
            print("🔄 Cleared metadata cache")

            # Fetch fresh metadata from Cube API
            metadata_result = self.metadata_fetcher.fetch_metadata(use_cache=False)

            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to fetch metadata from Cube API",
                    "details": metadata_result.get("error")
                }

            print(f"✅ Fetched fresh metadata from Cube API")

            # Get metadata summary
            summary = self.metadata_fetcher.get_summary()

            # Regenerate system prompt with new metadata
            prompt_result = self.context_manager.generate_system_prompt()
            self.system_prompt = prompt_result["system_prompt"]

            # Save to cache
            self._save_system_prompt_cache(self.system_prompt, prompt_result["metadata"])

            print(f"✅ Regenerated system prompt with {prompt_result['metadata']['views_count']} views")

            # Refresh query validator with new metadata
            try:
                view_metadata = self.metadata_fetcher.get_view_metadata('EventPerformanceOverview')
                if view_metadata.get('success'):
                    # Strip cube prefix from field names
                    measures_without_prefix = []
                    for measure in view_metadata['measures']:
                        field_name = measure['name']
                        if '.' in field_name:
                            field_name = field_name.split('.', 1)[1]
                        measures_without_prefix.append({
                            'name': field_name,
                            'title': measure.get('title', ''),
                            'description': measure.get('description', '')
                        })

                    dimensions_without_prefix = []
                    for dimension in view_metadata['dimensions']:
                        field_name = dimension['name']
                        if '.' in field_name:
                            field_name = field_name.split('.', 1)[1]
                        dimensions_without_prefix.append({
                            'name': field_name,
                            'title': dimension.get('title', ''),
                            'description': dimension.get('description', ''),
                            'type': dimension.get('type', '')  # Include type for time dimension validation
                        })

                    validator_metadata = {
                        'name': view_metadata['view'],
                        'title': view_metadata.get('title', ''),
                        'description': view_metadata.get('description', ''),
                        'measures': measures_without_prefix,
                        'dimensions': dimensions_without_prefix
                    }
                    self.query_validator = CubeQueryValidator(metadata_dict=validator_metadata)
                    print(f"✅ Query validator refreshed with new metadata")
                else:
                    print(f"⚠️  Failed to refresh validator: {view_metadata.get('error')}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to refresh query validator: {str(e)}")

            return {
                "success": True,
                "metadata_summary": summary,
                "system_prompt_metadata": prompt_result["metadata"],
                "system_prompt_length": len(self.system_prompt),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to refresh metadata: {str(e)}",
                "details": "An unexpected error occurred during metadata refresh"
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