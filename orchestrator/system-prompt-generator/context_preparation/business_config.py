# ABOUTME: Manager for business domain configuration and entity definitions
# ABOUTME: Loads and validates business context for semantic layer integration

from typing import Dict, List, Any, Optional
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from file_loader import FileLoader


class BusinessConfig:
    """
    Manager for business domain configuration.
    Handles loading and validation of business entities, relationships, and context.
    """

    def __init__(self, config_path: str):
        """
        Initialize the business configuration manager.

        Args:
            config_path: Path to the configuration directory
        """
        self.config_path = Path(config_path)
        self.file_loader = FileLoader()

        # Configuration file names
        self.business_domain_file = "business_domain.yaml"
        self.prompt_settings_file = "prompt_settings.yaml"
        self.ambiguity_config_file = "ambiguity_config.yaml"

    def load_business_context(self) -> Dict[str, Any]:
        """
        Load complete business context configuration.

        Returns:
            Dictionary containing business domain information
        """
        business_context = {
            'domain_info': self._load_business_domain(),
            'prompt_settings': self._load_prompt_settings(),
            'ambiguity_rules': self._load_ambiguity_config(),
            'metadata': {
                'config_loaded': True,
                'config_path': str(self.config_path)
            }
        }

        return business_context

    def _load_business_domain(self) -> Dict[str, Any]:
        """
        Load business domain configuration.

        Returns:
            Business domain configuration
        """
        try:
            file_path = self.config_path / self.business_domain_file

            if not file_path.exists():
                return self._get_default_business_domain()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content

        except Exception as e:
            print(f"Warning: Failed to load business domain config: {str(e)}")
            return self._get_default_business_domain()

    def _load_prompt_settings(self) -> Dict[str, Any]:
        """
        Load prompt configuration settings.

        Returns:
            Prompt settings configuration
        """
        try:
            file_path = self.config_path / self.prompt_settings_file

            if not file_path.exists():
                return self._get_default_prompt_settings()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content

        except Exception as e:
            print(f"Warning: Failed to load prompt settings: {str(e)}")
            return self._get_default_prompt_settings()

    def _load_ambiguity_config(self) -> Dict[str, Any]:
        """
        Load ambiguity detection and handling configuration.

        Returns:
            Ambiguity configuration
        """
        try:
            file_path = self.config_path / self.ambiguity_config_file

            if not file_path.exists():
                return self._get_default_ambiguity_config()

            content = self.file_loader.load_yaml_file(str(file_path))
            return content

        except Exception as e:
            print(f"Warning: Failed to load ambiguity config: {str(e)}")
            return self._get_default_ambiguity_config()

    def _get_default_business_domain(self) -> Dict[str, Any]:
        """
        Get default business domain configuration.

        Returns:
            Default business domain configuration
        """
        return {
            "business_name": "Event Management System",
            "business_description": "A comprehensive event management platform that tracks events, ticket sales, orders, and customer interactions.",
            "domain": "event_management",
            "entities": [
                {
                    "name": "Events",
                    "description": "Core entity representing events with details like name, dates, venue, and pricing",
                    "key_attributes": ["name", "start_date", "end_date", "venue", "status"],
                    "relationships": ["has_many_orders", "has_many_tickets"]
                },
                {
                    "name": "Orders",
                    "description": "Purchase transactions containing order details, amounts, and customer information",
                    "key_attributes": ["order_value", "quantity", "order_date", "status"],
                    "relationships": ["belongs_to_event", "belongs_to_customer"]
                },
                {
                    "name": "Customers",
                    "description": "Individuals or organizations purchasing tickets and attending events",
                    "key_attributes": ["name", "email", "registration_date", "total_purchases"],
                    "relationships": ["has_many_orders"]
                },
                {
                    "name": "Tickets",
                    "description": "Individual tickets sold for events with pricing and category information",
                    "key_attributes": ["ticket_type", "price", "quantity_sold", "availability"],
                    "relationships": ["belongs_to_event"]
                }
            ],
            "key_metrics": [
                {
                    "name": "Total Revenue",
                    "description": "Sum of all order values for events",
                    "calculation": "SUM(order_value)"
                },
                {
                    "name": "Tickets Sold",
                    "description": "Total number of tickets sold across all events",
                    "calculation": "SUM(quantity)"
                },
                {
                    "name": "Event Performance",
                    "description": "Revenue and attendance metrics grouped by event",
                    "calculation": "Revenue and ticket sales per event"
                }
            ],
            "common_questions": [
                "Which events are performing best in terms of revenue?",
                "How many tickets have been sold for each event?",
                "What is the total revenue for a specific time period?",
                "Which customers are the highest spenders?",
                "What are the monthly sales trends?"
            ]
        }

    def _get_default_prompt_settings(self) -> Dict[str, Any]:
        """
        Get default prompt configuration settings.

        Returns:
            Default prompt settings
        """
        return {
            "max_prompt_length": 4000,
            "include_examples": True,
            "include_business_context": True,
            "include_view_specifications": True,
            "include_api_instructions": True,
            "ambiguity_handling": True,
            "response_format": "structured_json",
            "confidence_threshold": 0.7,
            "max_clarification_questions": 3,
            "include_metadata": True
        }

    def _get_default_ambiguity_config(self) -> Dict[str, Any]:
        """
        Get default ambiguity detection configuration.

        Returns:
            Default ambiguity configuration
        """
        return {
            "ambiguity_triggers": [
                {
                    "type": "missing_time_range",
                    "keywords": ["show", "get", "find"],
                    "missing_elements": ["time", "date", "period", "when"],
                    "clarification": "What time period are you interested in?"
                },
                {
                    "type": "unclear_grouping",
                    "keywords": ["by", "group", "break down"],
                    "missing_elements": ["dimension", "category"],
                    "clarification": "How would you like the data grouped or categorized?"
                },
                {
                    "type": "ambiguous_metrics",
                    "keywords": ["performance", "numbers", "data", "metrics"],
                    "missing_elements": ["specific_measure"],
                    "clarification": "Which specific metrics are you looking for?"
                }
            ],
            "confidence_scoring": {
                "has_specific_measure": 0.3,
                "has_time_context": 0.2,
                "has_grouping_context": 0.2,
                "matches_known_patterns": 0.3
            },
            "minimum_confidence": 0.6,
            "clarification_templates": {
                "general": "I need more information to provide accurate results. Could you specify:",
                "time_missing": "What time period should I analyze?",
                "metric_missing": "Which metrics are you interested in?",
                "grouping_missing": "How would you like the results organized?"
            }
        }

    def get_business_entities(self) -> List[Dict[str, Any]]:
        """
        Get list of business entities with their descriptions.

        Returns:
            List of business entities
        """
        domain_info = self._load_business_domain()
        return domain_info.get('entities', [])

    def get_key_metrics(self) -> List[Dict[str, Any]]:
        """
        Get list of key business metrics.

        Returns:
            List of key metrics
        """
        domain_info = self._load_business_domain()
        return domain_info.get('key_metrics', [])

    def get_common_questions(self) -> List[str]:
        """
        Get list of common business questions.

        Returns:
            List of common questions
        """
        domain_info = self._load_business_domain()
        return domain_info.get('common_questions', [])

    def validate_configuration(self) -> List[str]:
        """
        Validate business configuration and return any issues.

        Returns:
            List of validation issues
        """
        issues = []

        # Check if config directory exists
        if not self.config_path.exists():
            issues.append(f"Configuration directory not found: {self.config_path}")
            return issues

        # Validate business domain
        try:
            domain_info = self._load_business_domain()
            if not domain_info.get('business_name'):
                issues.append("Business name is required in business domain config")
            if not domain_info.get('entities'):
                issues.append("At least one business entity is required")
        except Exception as e:
            issues.append(f"Error validating business domain: {str(e)}")

        # Validate prompt settings
        try:
            prompt_settings = self._load_prompt_settings()
            required_settings = ['max_prompt_length', 'confidence_threshold']
            for setting in required_settings:
                if setting not in prompt_settings:
                    issues.append(f"Missing required prompt setting: {setting}")
        except Exception as e:
            issues.append(f"Error validating prompt settings: {str(e)}")

        return issues


class BusinessConfigError(Exception):
    """Custom exception for business configuration errors."""
    pass