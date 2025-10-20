# ABOUTME: Main orchestrator for LLM integration context preparation
# ABOUTME: Coordinates YML parsing, business config, and prompt building for OpenAI API calls
# ABOUTME: Supports both dynamic Cube metadata fetching and static YAML fallback

from typing import Dict, List, Optional, Any
import os
from pathlib import Path

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, '..', 'utils'))

from yml_parser import YMLParser
from prompt_builder import PromptBuilder
from business_config import BusinessConfig
from example_manager import ExampleManager
from file_loader import FileLoader


class ContextManager:
    """
    Main orchestrator for generating system prompts for LLM integration.
    Coordinates all context preparation components to build comprehensive prompts.
    Supports both dynamic Cube metadata fetching and static YAML fallback.
    """

    def __init__(self,
                 base_path: Optional[str] = None,
                 cube_metadata_fetcher: Optional[Any] = None):
        """
        Initialize the context manager with base path configuration.

        Args:
            base_path: Base directory path for the llm-integration folder
            cube_metadata_fetcher: Optional CubeMetadataFetcher instance for dynamic metadata
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent

        self.base_path = Path(base_path)
        self.views_path = self.base_path / "my-cube-views"
        self.templates_path = self.base_path / "templates"
        self.config_path = self.base_path / "config"

        # Initialize components
        self.yml_parser = YMLParser()
        self.business_config = BusinessConfig(str(self.config_path))
        self.example_manager = ExampleManager(str(self.templates_path / "examples"))
        self.prompt_builder = PromptBuilder(str(self.templates_path))
        self.file_loader = FileLoader()

        # Dynamic metadata support
        self.cube_metadata_fetcher = cube_metadata_fetcher
        self.use_dynamic_metadata = cube_metadata_fetcher is not None

    def generate_system_prompt(self, user_query_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive system prompt for OpenAI API integration.

        Args:
            user_query_context: Optional context about the user's query for enhanced prompt generation

        Returns:
            Dictionary containing the complete system prompt and metadata
        """
        try:
            # Step 1: Load business configuration
            business_context = self.business_config.load_business_context()

            # Step 2: Parse all YML view files
            view_specifications = self._parse_cube_views()

            # Step 3: Load query examples and patterns
            examples_context = self.example_manager.load_all_examples()

            # Step 4: Build the complete system prompt
            system_prompt = self.prompt_builder.build_system_prompt({
                'business_context': business_context,
                'view_specifications': view_specifications,
                'examples_context': examples_context,
                'user_query_context': user_query_context
            })

            return {
                'system_prompt': system_prompt,
                'metadata': {
                    'views_count': len(view_specifications),
                    'examples_count': len(examples_context.get('successful_queries', [])),
                    'business_entities': len(business_context.get('entities', [])),
                    'generation_timestamp': self._get_timestamp()
                }
            }

        except Exception as e:
            raise ContextManagerError(f"Failed to generate system prompt: {str(e)}")

    def _parse_cube_views(self) -> List[Dict[str, Any]]:
        """
        Parse cube views from either dynamic Cube metadata or static YML files.

        Returns:
            List of parsed view specifications
        """
        # Try dynamic metadata first if available
        if self.use_dynamic_metadata and self.cube_metadata_fetcher:
            try:
                view_specifications = self._fetch_dynamic_cube_views()
                if view_specifications:
                    print(f"✅ Loaded {len(view_specifications)} views from Cube metadata API")
                    return view_specifications
                else:
                    print("⚠️  No views found in Cube metadata, falling back to YAML files")
            except Exception as e:
                print(f"⚠️  Failed to fetch dynamic metadata: {str(e)}, falling back to YAML files")

        # Fallback to static YAML parsing
        return self._parse_static_yaml_views()

    def _fetch_dynamic_cube_views(self) -> List[Dict[str, Any]]:
        """
        Fetch view specifications from Cube metadata API.

        Returns:
            List of view specifications in the same format as YAML parser
        """
        view_specifications = []

        # Get all views metadata
        all_views_result = self.cube_metadata_fetcher.get_all_views_metadata()

        if not all_views_result.get('success'):
            raise ContextManagerError(f"Failed to fetch views metadata: {all_views_result.get('error')}")

        # Convert Cube metadata format to view specification format
        for view_data in all_views_result.get('views', []):
            view_spec = {
                'name': view_data.get('view'),
                'title': view_data.get('title', view_data.get('view')),
                'description': view_data.get('description', ''),
                'type': view_data.get('type', 'cube'),
                'measures': [],
                'dimensions': []
            }

            # Add measures with descriptions
            for measure in view_data.get('measures', []):
                view_spec['measures'].append({
                    'name': measure.get('name'),
                    'title': measure.get('title', measure.get('name')),
                    'description': measure.get('description', '')
                })

            # Add dimensions with descriptions
            for dimension in view_data.get('dimensions', []):
                view_spec['dimensions'].append({
                    'name': dimension.get('name'),
                    'title': dimension.get('title', dimension.get('name')),
                    'description': dimension.get('description', '')
                })

            view_specifications.append(view_spec)

        return view_specifications

    def _parse_static_yaml_views(self) -> List[Dict[str, Any]]:
        """
        Parse all YML files in the my-cube-views directory (legacy/fallback).

        Returns:
            List of parsed view specifications
        """
        view_specifications = []

        if not self.views_path.exists():
            return view_specifications

        yml_files = list(self.views_path.glob("*.yml")) + list(self.views_path.glob("*.yaml"))

        for yml_file in yml_files:
            try:
                parsed_view = self.yml_parser.parse_view_file(str(yml_file))
                if parsed_view:
                    view_specifications.append(parsed_view)
            except Exception as e:
                # Log warning but continue processing other files
                print(f"Warning: Failed to parse {yml_file}: {str(e)}")

        return view_specifications

    def validate_context_setup(self) -> Dict[str, Any]:
        """
        Validate that all required files and configurations are properly set up.

        Returns:
            Dictionary containing validation results and status
        """
        validation_results = {
            'status': 'valid',
            'issues': [],
            'warnings': []
        }

        # Check required directories
        required_dirs = [self.views_path, self.templates_path, self.config_path]
        for directory in required_dirs:
            if not directory.exists():
                validation_results['issues'].append(f"Missing directory: {directory}")
                validation_results['status'] = 'invalid'

        # Check for YML view files
        if self.views_path.exists():
            yml_files = list(self.views_path.glob("*.yml")) + list(self.views_path.glob("*.yaml"))
            if not yml_files:
                validation_results['warnings'].append("No YML view files found in my-cube-views directory")

        # Validate business configuration
        try:
            self.business_config.validate_configuration()
        except Exception as e:
            validation_results['issues'].append(f"Business configuration error: {str(e)}")
            validation_results['status'] = 'invalid'

        # Validate examples
        try:
            self.example_manager.validate_examples()
        except Exception as e:
            validation_results['issues'].append(f"Examples validation error: {str(e)}")
            validation_results['status'] = 'invalid'

        return validation_results

    def get_available_views(self) -> List[str]:
        """
        Get list of available view names from parsed YML files.

        Returns:
            List of view names
        """
        view_specifications = self._parse_cube_views()
        return [view.get('name', 'unnamed') for view in view_specifications]

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime
        return datetime.now().isoformat()


class ContextManagerError(Exception):
    """Custom exception for context manager errors."""
    pass