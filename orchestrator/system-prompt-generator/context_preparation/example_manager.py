# ABOUTME: Manager for query examples and natural language to CUBE API patterns
# ABOUTME: Loads and validates successful queries and NL patterns for LLM context

from typing import Dict, List, Any, Optional
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from file_loader import FileLoader


class ExampleManager:
    """
    Manager for loading and organizing query examples and patterns.
    Handles successful queries, natural language patterns, and ambiguous query examples.
    """

    def __init__(self, examples_path: str):
        """
        Initialize the example manager with examples directory path.

        Args:
            examples_path: Path to the examples directory
        """
        self.examples_path = Path(examples_path)
        self.file_loader = FileLoader()

        # Example file names
        self.successful_queries_file = "successful_queries.yaml"
        self.nl_patterns_file = "nl_to_cube_patterns.yaml"
        self.ambiguous_examples_file = "ambiguous_query_examples.yaml"

    def load_all_examples(self) -> Dict[str, Any]:
        """
        Load all example files and return organized examples context.

        Returns:
            Dictionary containing all examples and patterns
        """
        examples_context = {
            'successful_queries': self._load_successful_queries(),
            'nl_patterns': self._load_nl_patterns(),
            'ambiguous_examples': self._load_ambiguous_examples(),
            'metadata': {
                'examples_loaded': True,
                'examples_path': str(self.examples_path)
            }
        }

        return examples_context

    def _load_successful_queries(self) -> List[Dict[str, Any]]:
        """
        Load successful query examples.

        Returns:
            List of successful query examples
        """
        try:
            file_path = self.examples_path / self.successful_queries_file

            if not file_path.exists():
                return self._get_default_successful_queries()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content.get('queries', [])

        except Exception as e:
            print(f"Warning: Failed to load successful queries: {str(e)}")
            return self._get_default_successful_queries()

    def _load_nl_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load natural language to CUBE API patterns.

        Returns:
            Dictionary of pattern categories
        """
        try:
            file_path = self.examples_path / self.nl_patterns_file

            if not file_path.exists():
                return self._get_default_nl_patterns()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content.get('patterns', {})

        except Exception as e:
            print(f"Warning: Failed to load NL patterns: {str(e)}")
            return self._get_default_nl_patterns()

    def _load_ambiguous_examples(self) -> List[Dict[str, Any]]:
        """
        Load ambiguous query examples and responses.

        Returns:
            List of ambiguous query examples
        """
        try:
            file_path = self.examples_path / self.ambiguous_examples_file

            if not file_path.exists():
                return self._get_default_ambiguous_examples()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content.get('ambiguous_queries', [])

        except Exception as e:
            print(f"Warning: Failed to load ambiguous examples: {str(e)}")
            return self._get_default_ambiguous_examples()

    def _get_default_successful_queries(self) -> List[Dict[str, Any]]:
        """
        Get default successful query examples.

        Returns:
            List of default successful queries
        """
        return [
            {
                "name": "Event Revenue and Sales Metrics",
                "natural_language": "Show me revenue and ticket sales for each event",
                "cube_query": {
                    "measures": [
                        "EventPerformanceOverview.total_order_value",
                        "EventPerformanceOverview.total_tickets_sold"
                    ],
                    "dimensions": [
                        "EventPerformanceOverview.name",
                        "EventPerformanceOverview.start_date"
                    ]
                },
                "description": "Basic revenue and sales metrics grouped by event"
            },
            {
                "name": "Top Performing Events",
                "natural_language": "Which events generated the most revenue?",
                "cube_query": {
                    "measures": ["EventPerformanceOverview.total_order_value"],
                    "dimensions": ["EventPerformanceOverview.name"],
                    "order": {"EventPerformanceOverview.total_order_value": "desc"},
                    "limit": 10
                },
                "description": "Top 10 events by revenue with sorting and limiting"
            }
        ]

    def _get_default_nl_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get default natural language patterns.

        Returns:
            Dictionary of default NL patterns
        """
        return {
            "temporal": [
                {
                    "phrase": "last month",
                    "cube_filter": {
                        "time_dimension": {
                            "dateRange": ["2024-08-01", "2024-08-31"]
                        }
                    }
                },
                {
                    "phrase": "this year",
                    "cube_filter": {
                        "time_dimension": {
                            "dateRange": "This year"
                        }
                    }
                }
            ],
            "aggregation": [
                {
                    "phrase": "total revenue",
                    "cube_measure": "total_order_value"
                },
                {
                    "phrase": "number of tickets sold",
                    "cube_measure": "total_tickets_sold"
                }
            ],
            "grouping": [
                {
                    "phrase": "by event",
                    "cube_dimension": "name"
                },
                {
                    "phrase": "by month",
                    "cube_dimension": "start_date",
                    "granularity": "month"
                }
            ]
        }

    def _get_default_ambiguous_examples(self) -> List[Dict[str, Any]]:
        """
        Get default ambiguous query examples.

        Returns:
            List of default ambiguous examples
        """
        return [
            {
                "ambiguous_query": "Show me performance",
                "clarification_response": {
                    "type": "clarification_needed",
                    "message": "I need clarification to provide accurate results:",
                    "questions": [
                        "What type of performance are you interested in? (revenue, attendance, sales)",
                        "What time period should I analyze?",
                        "How would you like the results grouped?"
                    ],
                    "suggestions": [
                        "Show event revenue performance for last month",
                        "Show ticket sales performance by event name"
                    ]
                }
            },
            {
                "ambiguous_query": "What are the numbers?",
                "clarification_response": {
                    "type": "clarification_needed",
                    "message": "I need more specific information:",
                    "questions": [
                        "Which metrics are you looking for?",
                        "For what time period?",
                        "What level of detail do you need?"
                    ],
                    "suggestions": [
                        "Show total revenue for all events",
                        "Show monthly ticket sales numbers"
                    ]
                }
            }
        ]

    def find_similar_queries(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Find similar successful queries based on user input.

        Args:
            user_query: User's natural language query

        Returns:
            List of similar successful queries
        """
        successful_queries = self._load_successful_queries()
        similar_queries = []

        # Simple keyword matching (can be enhanced with NLP)
        user_words = set(user_query.lower().split())

        for query in successful_queries:
            nl_text = query.get('natural_language', '').lower()
            query_words = set(nl_text.split())

            # Calculate simple word overlap
            overlap = len(user_words.intersection(query_words))
            if overlap > 0:
                query_copy = query.copy()
                query_copy['similarity_score'] = overlap / len(user_words.union(query_words))
                similar_queries.append(query_copy)

        # Sort by similarity score
        similar_queries.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return similar_queries[:3]  # Return top 3 similar queries

    def get_pattern_suggestions(self, user_query: str) -> Dict[str, List[str]]:
        """
        Get pattern suggestions based on user query.

        Args:
            user_query: User's natural language query

        Returns:
            Dictionary of relevant patterns
        """
        nl_patterns = self._load_nl_patterns()
        suggestions = {}

        query_lower = user_query.lower()

        for category, patterns in nl_patterns.items():
            matching_patterns = []
            for pattern in patterns:
                phrase = pattern.get('phrase', '').lower()
                if any(word in query_lower for word in phrase.split()):
                    matching_patterns.append(pattern)

            if matching_patterns:
                suggestions[category] = matching_patterns

        return suggestions

    def validate_examples(self) -> List[str]:
        """
        Validate all example files and return any issues found.

        Returns:
            List of validation issues
        """
        issues = []

        # Check if examples directory exists
        if not self.examples_path.exists():
            issues.append(f"Examples directory not found: {self.examples_path}")
            return issues

        # Validate successful queries
        try:
            successful_queries = self._load_successful_queries()
            for i, query in enumerate(successful_queries):
                if not query.get('name'):
                    issues.append(f"Successful query {i} missing name")
                if not query.get('cube_query'):
                    issues.append(f"Successful query {i} missing cube_query")
        except Exception as e:
            issues.append(f"Error validating successful queries: {str(e)}")

        # Validate NL patterns
        try:
            nl_patterns = self._load_nl_patterns()
            for category, patterns in nl_patterns.items():
                for i, pattern in enumerate(patterns):
                    if not pattern.get('phrase'):
                        issues.append(f"NL pattern {category}[{i}] missing phrase")
        except Exception as e:
            issues.append(f"Error validating NL patterns: {str(e)}")

        return issues


class ExampleManagerError(Exception):
    """Custom exception for example manager errors."""
    pass