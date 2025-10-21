# ABOUTME: Metadata tools for accessing cube schema information
# ABOUTME: Provides functions to query available measures, dimensions, and validate field names

from typing import List, Dict, Any
from ..schemas import AgentDependencies


def get_available_measures(deps: AgentDependencies) -> Dict[str, Any]:
    """
    Get list of available measures from cube metadata.

    Args:
        deps: Agent dependencies containing cube metadata

    Returns:
        Dictionary with measure names and details
    """
    measures = deps.cube_metadata.measures
    return {
        "count": len(measures),
        "measures": [
            {
                "name": m.get("name", ""),
                "title": m.get("title", ""),
                "description": m.get("description", "")
            }
            for m in measures
        ],
        "measure_names": [m.get("name", "") for m in measures]
    }


def get_available_dimensions(deps: AgentDependencies) -> Dict[str, Any]:
    """
    Get list of available dimensions from cube metadata.

    Args:
        deps: Agent dependencies containing cube metadata

    Returns:
        Dictionary with dimension names and details
    """
    dimensions = deps.cube_metadata.dimensions
    return {
        "count": len(dimensions),
        "dimensions": [
            {
                "name": d.get("name", ""),
                "title": d.get("title", ""),
                "description": d.get("description", ""),
                "type": d.get("type", "string")
            }
            for d in dimensions
        ],
        "dimension_names": [d.get("name", "") for d in dimensions]
    }


def get_time_dimensions(deps: AgentDependencies) -> Dict[str, Any]:
    """
    Get list of time dimensions from cube metadata.

    Args:
        deps: Agent dependencies containing cube metadata

    Returns:
        Dictionary with time dimension names and details
    """
    dimensions = deps.cube_metadata.dimensions
    time_dims = [d for d in dimensions if d.get("type") == "time"]

    return {
        "count": len(time_dims),
        "time_dimensions": [
            {
                "name": d.get("name", ""),
                "title": d.get("title", ""),
                "description": d.get("description", "")
            }
            for d in time_dims
        ],
        "time_dimension_names": [d.get("name", "") for d in time_dims]
    }


def validate_measure_exists(deps: AgentDependencies, measure_name: str) -> Dict[str, Any]:
    """
    Validate that a measure exists in the cube metadata.

    Args:
        deps: Agent dependencies containing cube metadata
        measure_name: Name of the measure to validate

    Returns:
        Dictionary with validation result
    """
    valid_measures = deps.cube_metadata.get_measure_names()

    exists = measure_name in valid_measures

    return {
        "measure_name": measure_name,
        "exists": exists,
        "valid_measures": valid_measures,
        "message": f"Measure '{measure_name}' {'exists' if exists else 'does not exist'} in cube metadata"
    }


def validate_dimension_exists(deps: AgentDependencies, dimension_name: str) -> Dict[str, Any]:
    """
    Validate that a dimension exists in the cube metadata.

    Args:
        deps: Agent dependencies containing cube metadata
        dimension_name: Name of the dimension to validate

    Returns:
        Dictionary with validation result
    """
    valid_dimensions = deps.cube_metadata.get_dimension_names()

    exists = dimension_name in valid_dimensions

    return {
        "dimension_name": dimension_name,
        "exists": exists,
        "valid_dimensions": valid_dimensions,
        "message": f"Dimension '{dimension_name}' {'exists' if exists else 'does not exist'} in cube metadata"
    }
