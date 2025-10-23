# ABOUTME: Agents package initialization
# ABOUTME: Exports PydanticAI agents for modular orchestration

# Note: query-ambiguity-assessor uses hyphens which aren't valid in Python imports
# Import using importlib to handle hyphenated directory name
import importlib
import sys
from pathlib import Path

# Add agents directory to path
agents_dir = Path(__file__).parent
sys.path.insert(0, str(agents_dir))

# Import from hyphenated directory using importlib
query_ambiguity_module = importlib.import_module('query-ambiguity-assessor')

QueryAmbiguityAssessor = query_ambiguity_module.QueryAmbiguityAssessor
AgentState = query_ambiguity_module.AgentState
AgentResponse = query_ambiguity_module.AgentResponse
CubeMetadata = query_ambiguity_module.CubeMetadata
ConversationContext = query_ambiguity_module.ConversationContext
AgentDependencies = query_ambiguity_module.AgentDependencies

__all__ = [
    "QueryAmbiguityAssessor",
    "AgentState",
    "AgentResponse",
    "CubeMetadata",
    "ConversationContext",
    "AgentDependencies"
]
