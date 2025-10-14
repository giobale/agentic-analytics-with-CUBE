# ABOUTME: Validator for Cube.js queries against cube/view schemas
# ABOUTME: Parses view YML files and validates that query parameters exist in the schema

import yaml
from typing import Dict, List, Any, Optional, Set
from pathlib import Path


class CubeQueryValidator:
    """
    Validates Cube.js queries against cube/view schemas.
    Ensures all measures, dimensions, and other parameters exist in the schema.
    """

    def __init__(self, view_yml_path: str):
        """
        Initialize validator with a view YML file.

        Args:
            view_yml_path: Path to the cube view YML file
        """
        self.view_yml_path = view_yml_path
        self.schema = self._load_schema()
        self.cube_name = self._extract_cube_name()
        self.available_measures = self._extract_measures()
        self.available_dimensions = self._extract_dimensions()
        self.available_time_dimensions = self._extract_time_dimensions()

    def _load_schema(self) -> Dict[str, Any]:
        """Load and parse the YML schema file."""
        try:
            with open(self.view_yml_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            # Handle cubes array structure
            if 'cubes' in content and isinstance(content['cubes'], list):
                return content['cubes'][0] if content['cubes'] else {}

            return content
        except Exception as e:
            raise CubeQueryValidatorError(f"Failed to load schema from {self.view_yml_path}: {str(e)}")

    def _extract_cube_name(self) -> str:
        """Extract the cube/view name from schema."""
        return self.schema.get('name', 'Unknown')

    def _extract_measures(self) -> Set[str]:
        """Extract all available measure names from schema."""
        measures = set()
        for measure in self.schema.get('measures', []):
            if isinstance(measure, dict):
                measure_name = measure.get('name')
                if measure_name:
                    measures.add(measure_name)
        return measures

    def _extract_dimensions(self) -> Set[str]:
        """Extract all available dimension names from schema."""
        dimensions = set()
        for dimension in self.schema.get('dimensions', []):
            if isinstance(dimension, dict):
                dim_name = dimension.get('name')
                if dim_name:
                    dimensions.add(dim_name)
        return dimensions

    def _extract_time_dimensions(self) -> Set[str]:
        """Extract time-type dimensions from schema."""
        time_dimensions = set()
        for dimension in self.schema.get('dimensions', []):
            if isinstance(dimension, dict):
                if dimension.get('type') == 'time':
                    dim_name = dimension.get('name')
                    if dim_name:
                        time_dimensions.add(dim_name)
        return time_dimensions

    def validate_query(self, cube_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a cube query against the schema.

        Args:
            cube_query: The cube query to validate

        Returns:
            Validation result with status and detailed errors
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "invalid_measures": [],
            "invalid_dimensions": [],
            "invalid_time_dimensions": [],
            "suggestions": {}
        }

        # Validate measures
        measures = cube_query.get('measures', [])
        if measures:
            for measure in measures:
                # Extract measure name (remove cube prefix if present)
                measure_name = self._extract_field_name(measure)

                if measure_name not in self.available_measures:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Measure '{measure}' does not exist in cube '{self.cube_name}'"
                    )
                    validation_result["invalid_measures"].append(measure)

                    # Suggest closest match
                    suggestion = self._find_closest_match(measure_name, self.available_measures)
                    if suggestion:
                        validation_result["suggestions"][measure] = f"{self.cube_name}.{suggestion}"

        # Validate dimensions
        dimensions = cube_query.get('dimensions', [])
        if dimensions:
            for dimension in dimensions:
                # Extract dimension name (remove cube prefix if present)
                dim_name = self._extract_field_name(dimension)

                if dim_name not in self.available_dimensions:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Dimension '{dimension}' does not exist in cube '{self.cube_name}'"
                    )
                    validation_result["invalid_dimensions"].append(dimension)

                    # Suggest closest match
                    suggestion = self._find_closest_match(dim_name, self.available_dimensions)
                    if suggestion:
                        validation_result["suggestions"][dimension] = f"{self.cube_name}.{suggestion}"

        # Validate time dimensions
        time_dimensions = cube_query.get('timeDimensions', [])
        if time_dimensions:
            for time_dim in time_dimensions:
                if isinstance(time_dim, dict):
                    dimension = time_dim.get('dimension', '')
                    dim_name = self._extract_field_name(dimension)

                    if dim_name not in self.available_time_dimensions:
                        validation_result["valid"] = False
                        validation_result["errors"].append(
                            f"Time dimension '{dimension}' does not exist or is not a time type in cube '{self.cube_name}'"
                        )
                        validation_result["invalid_time_dimensions"].append(dimension)

                        # Suggest closest match from time dimensions
                        suggestion = self._find_closest_match(dim_name, self.available_time_dimensions)
                        if suggestion:
                            validation_result["suggestions"][dimension] = f"{self.cube_name}.{suggestion}"

        # Validate filters
        filters = cube_query.get('filters', [])
        if filters:
            for filter_obj in filters:
                if isinstance(filter_obj, dict):
                    member = filter_obj.get('member', '')
                    member_name = self._extract_field_name(member)

                    # Check if member exists in measures or dimensions
                    if (member_name not in self.available_measures and
                        member_name not in self.available_dimensions):
                        validation_result["warnings"].append(
                            f"Filter member '{member}' does not exist in cube '{self.cube_name}'"
                        )

        return validation_result

    def _extract_field_name(self, field: str) -> str:
        """
        Extract the field name from a fully qualified name.

        Args:
            field: Field name, potentially with cube prefix (e.g., "CubeName.field_name")

        Returns:
            Just the field name without prefix
        """
        if '.' in field:
            return field.split('.', 1)[1]
        return field

    def _find_closest_match(self, query: str, candidates: Set[str], max_distance: int = 3) -> Optional[str]:
        """
        Find the closest matching field name using Levenshtein distance.

        Args:
            query: The query string to match
            candidates: Set of candidate strings
            max_distance: Maximum edit distance to consider

        Returns:
            Closest match or None
        """
        if not candidates:
            return None

        query_lower = query.lower()
        best_match = None
        best_distance = float('inf')

        for candidate in candidates:
            candidate_lower = candidate.lower()
            distance = self._levenshtein_distance(query_lower, candidate_lower)

            if distance < best_distance and distance <= max_distance:
                best_distance = distance
                best_match = candidate

        return best_match

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def get_schema_summary(self) -> Dict[str, Any]:
        """
        Get a summary of available measures and dimensions.

        Returns:
            Dictionary with schema information
        """
        return {
            "cube_name": self.cube_name,
            "measures": sorted(list(self.available_measures)),
            "dimensions": sorted(list(self.available_dimensions)),
            "time_dimensions": sorted(list(self.available_time_dimensions)),
            "measure_count": len(self.available_measures),
            "dimension_count": len(self.available_dimensions),
            "time_dimension_count": len(self.available_time_dimensions)
        }

    def generate_correction_prompt(self, validation_result: Dict[str, Any], original_query: str) -> str:
        """
        Generate a prompt to ask the LLM to correct invalid parameters.

        Args:
            validation_result: Result from validate_query
            original_query: The user's original natural language query

        Returns:
            Prompt string for LLM to fix the query
        """
        if validation_result["valid"]:
            return ""

        prompt_parts = [
            f"Your previous cube query contained invalid parameters for the '{self.cube_name}' cube.",
            "\nErrors found:"
        ]

        # Add error details
        for error in validation_result["errors"]:
            prompt_parts.append(f"  - {error}")

        # Add suggestions
        if validation_result["suggestions"]:
            prompt_parts.append("\nSuggested corrections:")
            for invalid, suggestion in validation_result["suggestions"].items():
                prompt_parts.append(f"  - Replace '{invalid}' with '{suggestion}'")

        # Add available schema info
        prompt_parts.append(f"\nAvailable measures in '{self.cube_name}':")
        prompt_parts.append(f"  {', '.join(sorted(self.available_measures))}")

        prompt_parts.append(f"\nAvailable dimensions in '{self.cube_name}':")
        prompt_parts.append(f"  {', '.join(sorted(self.available_dimensions))}")

        if self.available_time_dimensions:
            prompt_parts.append(f"\nAvailable time dimensions in '{self.cube_name}':")
            prompt_parts.append(f"  {', '.join(sorted(self.available_time_dimensions))}")

        prompt_parts.append(f"\nPlease regenerate the cube query for the user's question: \"{original_query}\"")
        prompt_parts.append("Use ONLY the measures and dimensions listed above.")
        prompt_parts.append("\nIMPORTANT: Respond with a complete JSON response in this exact format:")
        prompt_parts.append('{')
        prompt_parts.append('  "response_type": "cube_query",')
        prompt_parts.append('  "cube_query": {')
        prompt_parts.append(f'    "measures": ["{self.cube_name}.measure_name"],')
        prompt_parts.append(f'    "dimensions": ["{self.cube_name}.dimension_name"],')
        prompt_parts.append('    "timeDimensions": [{')
        prompt_parts.append(f'      "dimension": "{self.cube_name}.time_dimension_name",')
        prompt_parts.append('      "granularity": "day",')
        prompt_parts.append('      "dateRange": ["2020-01-01", "2020-01-31"]  // OR use "Last month", "This year", etc.')
        prompt_parts.append('    }]')
        prompt_parts.append('  },')
        prompt_parts.append('  "description": "<description of what the query does>",')
        prompt_parts.append('  "confidence_score": 0.9')
        prompt_parts.append('}')
        prompt_parts.append(f"\nREMEMBER:")
        prompt_parts.append(f"1. ALL field names must be prefixed with '{self.cube_name}.' (e.g., '{self.cube_name}.tickets_sold')")
        prompt_parts.append('2. For dateRange, use either:')
        prompt_parts.append('   - Array format: ["YYYY-MM-DD", "YYYY-MM-DD"]')
        prompt_parts.append('   - Valid string: "Today", "Yesterday", "This week", "This month", "This year", "Last 7 days", "Last 30 days", "Last week", "Last month", "Last year"')
        prompt_parts.append('   - For "all time" queries: OMIT the timeDimensions field entirely')
        prompt_parts.append('3. DO NOT use invalid strings like "all time", "All time", "january 2020", etc.')

        return "\n".join(prompt_parts)


class CubeQueryValidatorError(Exception):
    """Custom exception for cube query validator errors."""
    pass
