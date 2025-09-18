# ABOUTME: Parser for CUBE view YML files in my-cube-views directory
# ABOUTME: Validates and extracts semantic layer specifications from YML files

from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path


class YMLParser:
    """
    Parser for CUBE semantic layer view YML files.
    Handles validation and extraction of view specifications.
    """

    def __init__(self):
        """Initialize the YML parser with validation rules."""
        self.required_view_fields = ['name']  # Make sql optional for views
        self.optional_view_fields = ['description', 'dimensions', 'measures', 'joins']

    def parse_view_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single YML view file and extract specifications.

        Args:
            file_path: Path to the YML file to parse

        Returns:
            Parsed view specification dictionary or None if parsing fails
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise YMLParserError(f"File not found: {file_path}")

            if not file_path.suffix.lower() in ['.yml', '.yaml']:
                raise YMLParserError(f"Invalid file extension: {file_path.suffix}")

            with open(file_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)

            if not content:
                raise YMLParserError("Empty YML file")

            # Parse and validate the view specification
            parsed_view = self._parse_view_content(content, str(file_path))
            return parsed_view

        except yaml.YAMLError as e:
            raise YMLParserError(f"YAML parsing error in {file_path}: {str(e)}")
        except Exception as e:
            raise YMLParserError(f"Failed to parse {file_path}: {str(e)}")

    def _parse_view_content(self, content: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Parse and validate the content of a YML view file.

        Args:
            content: Parsed YAML content
            file_path: Path to the file being parsed (for error reporting)

        Returns:
            Validated and structured view specification
        """
        # Handle different YML structure possibilities
        view_spec = content

        # If the YML has a 'views' or 'view' key, extract the first view
        if 'views' in content and isinstance(content['views'], list) and content['views']:
            view_spec = content['views'][0]
        elif 'view' in content:
            view_spec = content['view']

        # Handle CUBE view format with cubes array
        if 'cubes' in view_spec:
            # Extract dimensions and measures from cubes includes
            dimensions_list = []
            measures_list = []

            for cube in view_spec.get('cubes', []):
                includes = cube.get('includes', [])
                for include in includes:
                    if isinstance(include, dict):
                        field_name = include.get('name', include.get('alias', 'unknown'))
                        alias = include.get('alias', field_name)
                    else:
                        field_name = str(include)
                        alias = field_name

                    # Classify as dimension or measure based on common patterns
                    if any(term in field_name.lower() for term in ['total_', 'avg_', 'count', 'value']):
                        measures_list.append({'name': alias, 'type': 'number', 'sql': field_name})
                    else:
                        dimensions_list.append({'name': alias, 'type': 'string', 'sql': field_name})

            # Update view_spec with extracted dimensions and measures
            view_spec['dimensions'] = dimensions_list
            view_spec['measures'] = measures_list

        # Validate required fields
        self._validate_required_fields(view_spec, file_path)

        # Extract and structure the view information
        parsed_view = {
            'name': view_spec['name'],
            'file_path': file_path,
            'sql': view_spec.get('sql', ''),
            'description': view_spec.get('description', ''),
            'dimensions': self._parse_dimensions(view_spec.get('dimensions', [])),
            'measures': self._parse_measures(view_spec.get('measures', [])),
            'joins': self._parse_joins(view_spec.get('joins', [])),
            'metadata': {
                'file_name': Path(file_path).name,
                'has_sql': bool(view_spec.get('sql')),
                'dimension_count': len(view_spec.get('dimensions', [])),
                'measure_count': len(view_spec.get('measures', []))
            }
        }

        return parsed_view

    def _validate_required_fields(self, view_spec: Dict[str, Any], file_path: str) -> None:
        """
        Validate that all required fields are present in the view specification.

        Args:
            view_spec: View specification dictionary
            file_path: Path to the file being validated
        """
        missing_fields = []
        for field in self.required_view_fields:
            if field not in view_spec or not view_spec[field]:
                missing_fields.append(field)

        if missing_fields:
            raise YMLParserError(f"Missing required fields in {file_path}: {missing_fields}")

    def _parse_dimensions(self, dimensions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and structure dimension definitions.

        Args:
            dimensions: Raw dimensions list from YML

        Returns:
            Structured dimensions list
        """
        parsed_dimensions = []

        for dim in dimensions:
            if isinstance(dim, dict):
                parsed_dim = {
                    'name': dim.get('name', ''),
                    'type': dim.get('type', 'string'),
                    'sql': dim.get('sql', ''),
                    'description': dim.get('description', ''),
                    'primary_key': dim.get('primary_key', False)
                }
                parsed_dimensions.append(parsed_dim)
            elif isinstance(dim, str):
                # Handle simple string dimension names
                parsed_dimensions.append({
                    'name': dim,
                    'type': 'string',
                    'sql': '',
                    'description': '',
                    'primary_key': False
                })

        return parsed_dimensions

    def _parse_measures(self, measures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and structure measure definitions.

        Args:
            measures: Raw measures list from YML

        Returns:
            Structured measures list
        """
        parsed_measures = []

        for measure in measures:
            if isinstance(measure, dict):
                parsed_measure = {
                    'name': measure.get('name', ''),
                    'type': measure.get('type', 'number'),
                    'sql': measure.get('sql', ''),
                    'description': measure.get('description', ''),
                    'aggregation': measure.get('type', 'sum')
                }
                parsed_measures.append(parsed_measure)
            elif isinstance(measure, str):
                # Handle simple string measure names
                parsed_measures.append({
                    'name': measure,
                    'type': 'number',
                    'sql': '',
                    'description': '',
                    'aggregation': 'sum'
                })

        return parsed_measures

    def _parse_joins(self, joins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse and structure join definitions.

        Args:
            joins: Raw joins list from YML

        Returns:
            Structured joins list
        """
        parsed_joins = []

        for join in joins:
            if isinstance(join, dict):
                parsed_join = {
                    'name': join.get('name', ''),
                    'sql': join.get('sql', ''),
                    'relationship': join.get('relationship', 'belongs_to'),
                    'description': join.get('description', '')
                }
                parsed_joins.append(parsed_join)

        return parsed_joins

    def parse_multiple_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Parse all YML files in a directory.

        Args:
            directory_path: Path to directory containing YML files

        Returns:
            List of parsed view specifications
        """
        directory = Path(directory_path)

        if not directory.exists():
            raise YMLParserError(f"Directory not found: {directory_path}")

        yml_files = list(directory.glob("*.yml")) + list(directory.glob("*.yaml"))
        parsed_views = []

        for yml_file in yml_files:
            try:
                parsed_view = self.parse_view_file(str(yml_file))
                if parsed_view:
                    parsed_views.append(parsed_view)
            except YMLParserError as e:
                # Log warning but continue with other files
                print(f"Warning: {str(e)}")

        return parsed_views

    def validate_view_specification(self, view_spec: Dict[str, Any]) -> List[str]:
        """
        Validate a parsed view specification and return any issues found.

        Args:
            view_spec: Parsed view specification

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check for required fields
        if not view_spec.get('name'):
            issues.append("View name is required")

        if not view_spec.get('sql') and not view_spec.get('dimensions'):
            issues.append("View must have either SQL or dimensions defined")

        # Validate dimensions
        for dim in view_spec.get('dimensions', []):
            if not dim.get('name'):
                issues.append("Dimension name is required")

        # Validate measures
        for measure in view_spec.get('measures', []):
            if not measure.get('name'):
                issues.append("Measure name is required")

        return issues


class YMLParserError(Exception):
    """Custom exception for YML parsing errors."""
    pass