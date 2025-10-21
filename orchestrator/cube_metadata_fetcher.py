# ABOUTME: Fetches and caches Cube.js metadata from /v1/meta API
# ABOUTME: Provides dynamic access to measures, dimensions, and descriptions from Cube semantic layer

import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class CubeMetadataFetcher:
    """
    Fetches metadata from Cube.js /v1/meta API endpoint.
    Provides structured access to cubes, views, measures, and dimensions.
    """

    def __init__(self,
                 base_url: str = "http://localhost:4000",
                 jwt_token: Optional[str] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the metadata fetcher.

        Args:
            base_url: Cube.js API base URL
            jwt_token: JWT token for authentication
            cache_dir: Directory to cache metadata (optional)
        """
        self.base_url = base_url
        self.jwt_token = jwt_token
        self.cache_dir = cache_dir
        self.metadata = None
        self.metadata_timestamp = None

        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
            self.cache_file = os.path.join(cache_dir, "cube_metadata.json")
        else:
            self.cache_file = None

    def fetch_metadata(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Fetch metadata from Cube.js API.

        Args:
            use_cache: If True, load from cache if available

        Returns:
            Dictionary containing fetch result and metadata
        """
        # Try to load from cache first if requested
        if use_cache and self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    self.metadata = cached_data.get('metadata')
                    self.metadata_timestamp = cached_data.get('timestamp')
                    return {
                        "success": True,
                        "source": "cache",
                        "metadata": self.metadata,
                        "timestamp": self.metadata_timestamp
                    }
            except Exception as e:
                print(f"Warning: Failed to load metadata cache: {str(e)}")

        # Fetch from API
        try:
            headers = {'Content-Type': 'application/json'}
            if self.jwt_token:
                headers['Authorization'] = f'Bearer {self.jwt_token}'

            response = requests.get(
                f"{self.base_url}/cubejs-api/v1/meta",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            self.metadata = response.json()
            self.metadata_timestamp = datetime.now().isoformat()

            # Save to cache
            if self.cache_file:
                self._save_to_cache()

            return {
                "success": True,
                "source": "api",
                "metadata": self.metadata,
                "timestamp": self.metadata_timestamp
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to fetch metadata from Cube API: {str(e)}",
                "details": "Check that Cube.js is running and accessible"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error fetching metadata: {str(e)}"
            }

    def _save_to_cache(self) -> bool:
        """Save metadata to cache file."""
        if not self.cache_file or not self.metadata:
            return False

        try:
            cache_data = {
                "metadata": self.metadata,
                "timestamp": self.metadata_timestamp
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Warning: Failed to save metadata cache: {str(e)}")
            return False

    def get_view_metadata(self, view_name: str) -> Dict[str, Any]:
        """
        Extract metadata for a specific view or cube.

        Args:
            view_name: Name of the view/cube to extract

        Returns:
            Dictionary with view metadata including measures and dimensions
        """
        if not self.metadata:
            return {
                "success": False,
                "error": "Metadata not loaded. Call fetch_metadata() first."
            }

        # Look for the view/cube in metadata
        cubes = self.metadata.get('cubes', [])
        target_cube = None

        # Prefer views first
        for cube in cubes:
            if cube.get('name') == view_name:
                # Check if it's a view
                if cube.get('type') == 'view' or cube.get('isView'):
                    target_cube = cube
                    break
                # Store as fallback if it's a regular cube
                if target_cube is None:
                    target_cube = cube

        if not target_cube:
            return {
                "success": False,
                "error": f"View/cube '{view_name}' not found in metadata",
                "available_cubes": [c.get('name') for c in cubes]
            }

        # Extract measures
        measures = []
        for measure in target_cube.get('measures', []):
            measures.append({
                "name": measure.get('name'),
                "title": measure.get('title', ''),
                "description": measure.get('description', measure.get('title', ''))
            })

        # Extract dimensions
        dimensions = []
        for dimension in target_cube.get('dimensions', []):
            dimensions.append({
                "name": dimension.get('name'),
                "title": dimension.get('title', ''),
                "description": dimension.get('description', dimension.get('title', '')),
                "type": dimension.get('type', '')  # Include type for time dimension validation
            })

        return {
            "success": True,
            "view": view_name,
            "type": target_cube.get('type', 'cube'),
            "title": target_cube.get('title', view_name),
            "description": target_cube.get('description', ''),
            "measures": measures,
            "dimensions": dimensions,
            "measures_count": len(measures),
            "dimensions_count": len(dimensions)
        }

    def get_all_views_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata for all views and cubes.

        Returns:
            Dictionary containing all views/cubes with their metadata
        """
        if not self.metadata:
            return {
                "success": False,
                "error": "Metadata not loaded. Call fetch_metadata() first."
            }

        cubes = self.metadata.get('cubes', [])
        all_views = []

        for cube in cubes:
            cube_name = cube.get('name')
            view_data = self.get_view_metadata(cube_name)
            if view_data.get('success'):
                all_views.append(view_data)

        return {
            "success": True,
            "views": all_views,
            "views_count": len(all_views),
            "timestamp": self.metadata_timestamp
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of available cubes/views.

        Returns:
            Summary information about the metadata
        """
        if not self.metadata:
            return {
                "success": False,
                "error": "Metadata not loaded. Call fetch_metadata() first."
            }

        cubes = self.metadata.get('cubes', [])
        views = [c for c in cubes if c.get('type') == 'view' or c.get('isView')]
        regular_cubes = [c for c in cubes if c.get('type') != 'view' and not c.get('isView')]

        return {
            "success": True,
            "total_cubes": len(cubes),
            "views_count": len(views),
            "cubes_count": len(regular_cubes),
            "view_names": [v.get('name') for v in views],
            "cube_names": [c.get('name') for c in regular_cubes],
            "timestamp": self.metadata_timestamp
        }

    def clear_cache(self) -> bool:
        """Clear the metadata cache file."""
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                self.metadata = None
                self.metadata_timestamp = None
                return True
            except Exception as e:
                print(f"Warning: Failed to clear cache: {str(e)}")
                return False
        return False


class CubeMetadataFetcherError(Exception):
    """Custom exception for metadata fetcher errors."""
    pass
