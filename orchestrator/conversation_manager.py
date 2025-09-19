# ABOUTME: Manages conversation history and message formatting for LLM interactions
# ABOUTME: Tracks last 6 messages and formats them for OpenAI API compatibility

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class ConversationManager:
    """
    Manages conversation history for natural language query processing.
    Maintains the last 6 messages for context in LLM interactions.
    """

    def __init__(self, max_messages: int = 6):
        """
        Initialize conversation manager.

        Args:
            max_messages: Maximum number of messages to keep in history (default: 6)
        """
        self.max_messages = max_messages
        self.conversation_history: List[Dict[str, Any]] = []

    def add_user_message(self, message: str, timestamp: Optional[str] = None) -> None:
        """
        Add a user message to the conversation history.

        Args:
            message: User's natural language query
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        user_message = {
            "role": "user",
            "content": message,
            "timestamp": timestamp
        }

        self.conversation_history.append(user_message)
        self._trim_history()

    def add_assistant_message(self, llm_response: Dict[str, Any], timestamp: Optional[str] = None) -> None:
        """
        Add an assistant response to the conversation history.

        Args:
            llm_response: LLM response dictionary
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        # Format assistant message based on response type
        if llm_response.get("response_type") == "cube_query":
            content = f"I found data for your query: {llm_response.get('interpretation', '')}"
        elif llm_response.get("response_type") == "clarification_needed":
            content = f"I need clarification: {llm_response.get('interpretation', '')}"
        elif llm_response.get("response_type") == "error":
            content = f"Error occurred: {llm_response.get('interpretation', '')}"
        else:
            content = llm_response.get('interpretation', 'Response processed')

        assistant_message = {
            "role": "assistant",
            "content": content,
            "timestamp": timestamp,
            "response_data": llm_response
        }

        self.conversation_history.append(assistant_message)
        self._trim_history()

    def get_openai_messages(self, system_prompt: str) -> List[Dict[str, str]]:
        """
        Format conversation history for OpenAI API.

        Args:
            system_prompt: System prompt for the LLM

        Returns:
            List of messages formatted for OpenAI API
        """
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (excluding response_data for API)
        for message in self.conversation_history:
            openai_message = {
                "role": message["role"],
                "content": message["content"]
            }
            messages.append(openai_message)

        return messages

    def get_conversation_context(self) -> Dict[str, Any]:
        """
        Get conversation context for debugging and logging.

        Returns:
            Dictionary containing conversation metadata
        """
        return {
            "message_count": len(self.conversation_history),
            "max_messages": self.max_messages,
            "has_history": len(self.conversation_history) > 0,
            "last_message_timestamp": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
            "conversation_summary": self._generate_summary()
        }

    def clear_conversation(self) -> None:
        """Clear all conversation history."""
        self.conversation_history = []

    def export_conversation(self) -> List[Dict[str, Any]]:
        """
        Export full conversation history for persistence or analysis.

        Returns:
            Complete conversation history
        """
        return self.conversation_history.copy()

    def import_conversation(self, history: List[Dict[str, Any]]) -> None:
        """
        Import conversation history from external source.

        Args:
            history: Conversation history to import
        """
        self.conversation_history = history[-self.max_messages:] if history else []

    def get_last_cube_query(self) -> Optional[Dict[str, Any]]:
        """
        Get the last successful CUBE query from conversation history.

        Returns:
            Last CUBE query or None if not found
        """
        for message in reversed(self.conversation_history):
            if (message.get("role") == "assistant" and
                message.get("response_data", {}).get("response_type") == "cube_query"):
                return message.get("response_data", {}).get("cube_query")
        return None

    def get_conversation_topics(self) -> List[str]:
        """
        Extract main topics from conversation history.

        Returns:
            List of topics discussed
        """
        topics = []
        for message in self.conversation_history:
            if message.get("role") == "user":
                # Simple keyword extraction (can be enhanced with NLP)
                content = message.get("content", "").lower()
                if "revenue" in content:
                    topics.append("revenue")
                if "event" in content:
                    topics.append("events")
                if "ticket" in content:
                    topics.append("tickets")
                if "sales" in content:
                    topics.append("sales")

        return list(set(topics))  # Remove duplicates

    def _trim_history(self) -> None:
        """Keep only the last max_messages in history."""
        if len(self.conversation_history) > self.max_messages:
            self.conversation_history = self.conversation_history[-self.max_messages:]

    def _generate_summary(self) -> str:
        """
        Generate a brief summary of the conversation.

        Returns:
            Conversation summary string
        """
        if not self.conversation_history:
            return "No conversation history"

        user_messages = [msg for msg in self.conversation_history if msg.get("role") == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg.get("role") == "assistant"]

        topics = self.get_conversation_topics()
        topic_str = ", ".join(topics) if topics else "general queries"

        return f"{len(user_messages)} user queries, {len(assistant_messages)} responses about {topic_str}"

    def validate_conversation_integrity(self) -> List[str]:
        """
        Validate conversation history for any issues.

        Returns:
            List of validation issues found
        """
        issues = []

        for i, message in enumerate(self.conversation_history):
            # Check required fields
            if "role" not in message:
                issues.append(f"Message {i} missing 'role' field")
            if "content" not in message:
                issues.append(f"Message {i} missing 'content' field")
            if "timestamp" not in message:
                issues.append(f"Message {i} missing 'timestamp' field")

            # Check role validity
            if message.get("role") not in ["user", "assistant"]:
                issues.append(f"Message {i} has invalid role: {message.get('role')}")

        return issues


class ConversationManagerError(Exception):
    """Custom exception for conversation manager errors."""
    pass