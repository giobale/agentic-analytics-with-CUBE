# ABOUTME: OpenAI API client for natural language to CUBE query processing
# ABOUTME: Handles LLM interactions with system prompts and conversation history

from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None


class LLMClient:
    """
    OpenAI API client for processing natural language queries.
    Converts user questions to CUBE API queries using system prompts.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4)
        """
        if openai is None:
            raise LLMClientError("OpenAI package not installed. Install with: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMClientError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def process_query(self,
                     user_query: str,
                     system_prompt: str,
                     conversation_messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process user query using OpenAI API.

        Args:
            user_query: User's natural language question
            system_prompt: System prompt with CUBE context
            conversation_messages: Previous conversation messages

        Returns:
            Structured response dictionary with expected format
        """
        try:
            # Prepare messages for OpenAI API
            messages = conversation_messages.copy()
            messages.append({"role": "user", "content": user_query})

            # Call OpenAI API
            try:
                # Try with JSON format first
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,  # Low temperature for consistent responses
                    max_tokens=2000,
                    response_format={"type": "json_object"}  # Ensure JSON response
                )
            except Exception as json_error:
                if "response_format" in str(json_error):
                    # Fallback: call without JSON format constraint
                    print("⚠️  JSON response format not supported, falling back to regular format")
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=2000
                    )
                else:
                    raise json_error

            # Extract and parse response
            response_content = response.choices[0].message.content
            parsed_response = json.loads(response_content)

            # Validate and normalize response format
            normalized_response = self._normalize_response(parsed_response, user_query)

            return {
                "success": True,
                "response": normalized_response,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }

        except json.JSONDecodeError as e:
            return self._create_error_response(f"Invalid JSON response from LLM: {str(e)}", user_query)
        except Exception as e:
            return self._create_error_response(f"LLM API error: {str(e)}", user_query)

    def _normalize_response(self, llm_response: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """
        Normalize LLM response to expected format.

        Args:
            llm_response: Raw LLM response
            user_query: Original user query

        Returns:
            Normalized response dictionary
        """
        # Expected format based on your specification
        normalized = {
            "response_type": llm_response.get("response_type", "error"),
            "interpretation": llm_response.get("interpretation", "Processing your query..."),
            "confidence_score": llm_response.get("confidence_score", 0.5)
        }

        response_type = normalized["response_type"]

        if response_type == "cube_query":
            normalized.update({
                "cube_query": llm_response.get("cube_query", {}),
                "description": llm_response.get("description", "Query processed successfully")
            })

            # Validate cube_query structure
            cube_query = normalized["cube_query"]
            if not cube_query.get("measures") and not cube_query.get("dimensions"):
                return self._create_error_response("Invalid cube query: missing measures and dimensions", user_query)

        elif response_type == "clarification_needed":
            normalized.update({
                "clarification_questions": llm_response.get("clarification_questions", []),
                "suggestions": llm_response.get("suggestions", [])
            })

        elif response_type == "error":
            normalized.update({
                "description": llm_response.get("description", "An error occurred processing your query")
            })

        else:
            # Unknown response type, convert to error
            return self._create_error_response(f"Unknown response type: {response_type}", user_query)

        return normalized

    def _create_error_response(self, error_message: str, user_query: str) -> Dict[str, Any]:
        """
        Create standardized error response.

        Args:
            error_message: Error description
            user_query: Original user query

        Returns:
            Error response dictionary
        """
        return {
            "success": False,
            "response": {
                "response_type": "error",
                "interpretation": "I encountered an issue processing your request",
                "description": error_message,
                "confidence_score": 0.0,
                "original_query": user_query
            },
            "timestamp": datetime.now().isoformat()
        }

    def validate_api_key(self) -> bool:
        """
        Validate OpenAI API key by making a simple test call.

        Returns:
            True if API key is valid
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available OpenAI models.

        Returns:
            List of model names
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id]
        except Exception:
            return ["gpt-4", "gpt-3.5-turbo"]  # Fallback to common models

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for text.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4

    def create_test_query(self) -> Dict[str, Any]:
        """
        Create a test query for validation.

        Returns:
            Test query response
        """
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond with valid JSON."},
            {"role": "user", "content": "Say hello in JSON format with response_type, interpretation, and confidence_score fields."}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=test_messages,
                temperature=0.1,
                max_tokens=100,
                response_format={"type": "json_object"}
            )

            return {
                "success": True,
                "test_response": response.choices[0].message.content,
                "model": self.model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass