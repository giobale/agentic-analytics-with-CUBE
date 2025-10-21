# ABOUTME: Context management tools for maintaining query state
# ABOUTME: Provides functions to update, retrieve, and clear query context during conversation

from typing import Dict, Any
from ..schemas import AgentDependencies


def update_query_context(deps: AgentDependencies, key: str, value: Any) -> Dict[str, Any]:
    """
    Update the query context with new information from clarifications.

    Args:
        deps: Agent dependencies containing conversation context
        key: Context key to update
        value: Value to store

    Returns:
        Dictionary with update confirmation
    """
    deps.conversation_context.update_context(key, value)

    return {
        "success": True,
        "key": key,
        "value": value,
        "message": f"Updated query context: {key} = {value}",
        "current_context": deps.conversation_context.query_context
    }


def get_query_context(deps: AgentDependencies) -> Dict[str, Any]:
    """
    Get the current query context.

    Args:
        deps: Agent dependencies containing conversation context

    Returns:
        Dictionary with current query context
    """
    return {
        "query_context": deps.conversation_context.query_context,
        "context_keys": list(deps.conversation_context.query_context.keys()),
        "message": "Retrieved current query context"
    }


def clear_query_context(deps: AgentDependencies) -> Dict[str, Any]:
    """
    Clear the query context (used when query is rejected).

    Args:
        deps: Agent dependencies containing conversation context

    Returns:
        Dictionary with clear confirmation
    """
    deps.conversation_context.query_context = {}

    return {
        "success": True,
        "message": "Query context cleared",
        "query_context": {}
    }
