# ABOUTME: Enhanced prompt builder with ambiguity handling for LLM integration
# ABOUTME: Constructs comprehensive system prompts using templates, business context, and examples

from typing import Dict, List, Any, Optional
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_loader import FileLoader


class PromptBuilder:
    """
    Enhanced prompt builder that constructs comprehensive system prompts.
    Handles template loading, context integration, and ambiguity handling instructions.
    """

    def __init__(self, templates_path: str):
        """
        Initialize the prompt builder with templates directory path.

        Args:
            templates_path: Path to the templates directory
        """
        self.templates_path = Path(templates_path)
        self.file_loader = FileLoader()

        # Template file names
        self.base_template = "system_prompt_base.txt"
        self.business_template = "business_context.txt"
        self.api_instructions = "cube_api_instructions.txt"
        self.ambiguity_instructions = "ambiguity_instructions.txt"

    def build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build complete system prompt using all available context.

        Args:
            context: Dictionary containing all context components

        Returns:
            Complete system prompt string
        """
        try:
            # Load base template
            base_template = self._load_template(self.base_template)

            # Prepare all context sections
            sections = {
                'business_context': self._build_business_context(context.get('business_context', {})),
                'view_specifications': self._build_view_specifications(context.get('view_specifications', [])),
                'cube_api_instructions': self._load_template(self.api_instructions),
                'successful_queries': self._build_examples_section(context.get('examples_context', {})),
                'nl_patterns': self._build_patterns_section(context.get('examples_context', {})),
                'ambiguity_instructions': self._load_template(self.ambiguity_instructions)
            }

            # Replace placeholders in base template
            system_prompt = base_template.format(**sections)

            return system_prompt

        except Exception as e:
            raise PromptBuilderError(f"Failed to build system prompt: {str(e)}")

    def _load_template(self, template_name: str) -> str:
        """
        Load a template file.

        Args:
            template_name: Name of the template file

        Returns:
            Template content as string
        """
        template_path = self.templates_path / template_name

        if not template_path.exists():
            return f"# Template {template_name} not found"

        return self.file_loader.load_text_file(str(template_path))

    def _build_business_context(self, business_context: Dict[str, Any]) -> str:
        """
        Build the business context section.

        Args:
            business_context: Business context data

        Returns:
            Formatted business context string
        """
        try:
            domain_info = business_context.get('domain_info', {})

            # Load business context template
            template = self._load_template(self.business_template)

            # Prepare template variables
            variables = {
                'business_name': domain_info.get('business_name', 'Event Management System'),
                'business_description': domain_info.get('business_description', ''),
                'domain': domain_info.get('domain', 'event_management'),
                'entities_section': self._format_entities(domain_info.get('entities', [])),
                'metrics_section': self._format_metrics(domain_info.get('key_metrics', [])),
                'common_questions_section': self._format_questions(domain_info.get('common_questions', []))
            }

            return template.format(**variables)

        except Exception as e:
            return f"# Business context error: {str(e)}"

    def _build_view_specifications(self, view_specifications: List[Dict[str, Any]]) -> str:
        """
        Build the view specifications section.

        Args:
            view_specifications: List of parsed view specifications

        Returns:
            Formatted view specifications string
        """
        if not view_specifications:
            return "# No view specifications available"

        sections = ["# CUBE VIEW SPECIFICATIONS\n"]

        for view in view_specifications:
            view_name = view.get('name', 'Unknown View')
            description = view.get('description', 'No description available')

            sections.append(f"## {view_name}")
            sections.append(f"**Description**: {description}\n")

            # Add dimensions
            dimensions = view.get('dimensions', [])
            if dimensions:
                sections.append("**Available Dimensions:**")
                for dim in dimensions:
                    dim_name = dim.get('name', 'unknown')
                    dim_desc = dim.get('description', '')
                    if dim_desc:
                        sections.append(f"- `{view_name}.{dim_name}`: {dim_desc}")
                    else:
                        sections.append(f"- `{view_name}.{dim_name}`")
                sections.append("")

            # Add measures
            measures = view.get('measures', [])
            if measures:
                sections.append("**Available Measures:**")
                for measure in measures:
                    measure_name = measure.get('name', 'unknown')
                    measure_desc = measure.get('description', '')
                    if measure_desc:
                        sections.append(f"- `{view_name}.{measure_name}`: {measure_desc}")
                    else:
                        sections.append(f"- `{view_name}.{measure_name}`")
                sections.append("")

        return "\n".join(sections)

    def _build_examples_section(self, examples_context: Dict[str, Any]) -> str:
        """
        Build the successful queries examples section.

        Args:
            examples_context: Examples context data

        Returns:
            Formatted examples string
        """
        successful_queries = examples_context.get('successful_queries', [])

        if not successful_queries:
            return "# No successful query examples available"

        sections = ["# SUCCESSFUL QUERY EXAMPLES\n"]

        for example in successful_queries:
            name = example.get('name', 'Unnamed Query')
            nl_query = example.get('natural_language', '')
            cube_query = example.get('cube_query', {})
            description = example.get('description', '')

            sections.append(f"## {name}")
            if description:
                sections.append(f"**Purpose**: {description}")

            sections.append(f"**Natural Language**: \"{nl_query}\"")
            sections.append("**CUBE Query**:")
            sections.append("```json")
            sections.append(self._format_json(cube_query))
            sections.append("```\n")

        return "\n".join(sections)

    def _build_patterns_section(self, examples_context: Dict[str, Any]) -> str:
        """
        Build the natural language patterns section.

        Args:
            examples_context: Examples context data

        Returns:
            Formatted patterns string
        """
        nl_patterns = examples_context.get('nl_patterns', {})

        if not nl_patterns:
            return "# No natural language patterns available"

        sections = ["# NATURAL LANGUAGE PATTERNS\n"]

        for category, patterns in nl_patterns.items():
            sections.append(f"## {category.title()} Patterns")

            for pattern in patterns:
                phrase = pattern.get('phrase', '')
                if phrase:
                    sections.append(f"- \"{phrase}\" → {self._describe_pattern(pattern)}")

            sections.append("")

        return "\n".join(sections)

    def _format_entities(self, entities: List[Dict[str, Any]]) -> str:
        """Format business entities for template."""
        if not entities:
            return "No entities defined"

        formatted = []
        for entity in entities:
            name = entity.get('name', 'Unknown')
            description = entity.get('description', '')
            formatted.append(f"**{name}**: {description}")

        return "\n".join(formatted)

    def _format_metrics(self, metrics: List[Dict[str, Any]]) -> str:
        """Format key metrics for template."""
        if not metrics:
            return "No metrics defined"

        formatted = []
        for metric in metrics:
            name = metric.get('name', 'Unknown')
            description = metric.get('description', '')
            formatted.append(f"**{name}**: {description}")

        return "\n".join(formatted)

    def _format_questions(self, questions: List[str]) -> str:
        """Format common questions for template."""
        if not questions:
            return "No common questions defined"

        return "\n".join([f"- {question}" for question in questions])

    def _describe_pattern(self, pattern: Dict[str, Any]) -> str:
        """Describe a natural language pattern."""
        if 'cube_measure' in pattern:
            return f"measure: {pattern['cube_measure']}"
        elif 'cube_dimension' in pattern:
            return f"dimension: {pattern['cube_dimension']}"
        elif 'cube_filter' in pattern:
            return "filter/time dimension"
        elif 'cube_operator' in pattern:
            return f"operator: {pattern['cube_operator']}"
        else:
            return "pattern mapping"

    def _format_json(self, data: Any) -> str:
        """Format data as JSON string."""
        import json
        try:
            return json.dumps(data, indent=2)
        except Exception:
            return str(data)

    def build_context_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a summary of the context for debugging/validation.

        Args:
            context: Context data

        Returns:
            Summary of context components
        """
        return {
            'business_context': {
                'has_domain_info': bool(context.get('business_context', {}).get('domain_info')),
                'entities_count': len(context.get('business_context', {}).get('domain_info', {}).get('entities', [])),
                'metrics_count': len(context.get('business_context', {}).get('domain_info', {}).get('key_metrics', []))
            },
            'view_specifications': {
                'views_count': len(context.get('view_specifications', [])),
                'total_dimensions': sum(len(view.get('dimensions', [])) for view in context.get('view_specifications', [])),
                'total_measures': sum(len(view.get('measures', [])) for view in context.get('view_specifications', []))
            },
            'examples_context': {
                'successful_queries': len(context.get('examples_context', {}).get('successful_queries', [])),
                'pattern_categories': len(context.get('examples_context', {}).get('nl_patterns', {})),
                'ambiguous_examples': len(context.get('examples_context', {}).get('ambiguous_examples', []))
            }
        }

    def validate_prompt_components(self, context: Dict[str, Any]) -> List[str]:
        """
        Validate that all required prompt components are available.

        Args:
            context: Context data to validate

        Returns:
            List of validation issues
        """
        issues = []

        # Check business context
        business_context = context.get('business_context', {})
        if not business_context.get('domain_info'):
            issues.append("Missing business domain information")

        # Check view specifications
        view_specs = context.get('view_specifications', [])
        if not view_specs:
            issues.append("No view specifications available")

        # Check examples
        examples = context.get('examples_context', {})
        if not examples.get('successful_queries'):
            issues.append("No successful query examples available")

        # Check template files
        required_templates = [self.base_template, self.api_instructions, self.ambiguity_instructions]
        for template in required_templates:
            template_path = self.templates_path / template
            if not template_path.exists():
                issues.append(f"Missing template file: {template}")

        return issues


class PromptBuilderError(Exception):
    """Custom exception for prompt builder errors."""
    pass