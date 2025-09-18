# ABOUTME: File system utilities for loading templates and configuration files
# ABOUTME: Provides safe file reading and validation for the LLM integration system

from typing import Dict, List, Any, Optional
import os
import yaml
import json
from pathlib import Path


class FileLoader:
    """
    Utility class for safe file loading operations.
    Handles text files, YAML, and JSON with proper error handling.
    """

    def __init__(self):
        """Initialize the file loader."""
        pass

    def load_text_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Load a text file and return its contents.

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)

        Returns:
            File contents as string
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileLoaderError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()

        except UnicodeDecodeError as e:
            raise FileLoaderError(f"Encoding error reading {file_path}: {str(e)}")
        except Exception as e:
            raise FileLoaderError(f"Failed to load text file {file_path}: {str(e)}")

    def load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a YAML file and return parsed content.

        Args:
            file_path: Path to the YAML file

        Returns:
            Parsed YAML content as dictionary
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileLoaderError(f"YAML file not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)

            if content is None:
                return {}

            return content

        except yaml.YAMLError as e:
            raise FileLoaderError(f"YAML parsing error in {file_path}: {str(e)}")
        except Exception as e:
            raise FileLoaderError(f"Failed to load YAML file {file_path}: {str(e)}")

    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a JSON file and return parsed content.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON content as dictionary
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileLoaderError(f"JSON file not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.load(file)

            return content

        except json.JSONDecodeError as e:
            raise FileLoaderError(f"JSON parsing error in {file_path}: {str(e)}")
        except Exception as e:
            raise FileLoaderError(f"Failed to load JSON file {file_path}: {str(e)}")

    def list_files_in_directory(self, directory_path: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory matching a pattern.

        Args:
            directory_path: Path to the directory
            pattern: File pattern to match (default: all files)

        Returns:
            List of file paths matching the pattern
        """
        try:
            directory = Path(directory_path)

            if not directory.exists():
                raise FileLoaderError(f"Directory not found: {directory_path}")

            if not directory.is_dir():
                raise FileLoaderError(f"Path is not a directory: {directory_path}")

            files = list(directory.glob(pattern))
            return [str(file) for file in files if file.is_file()]

        except Exception as e:
            raise FileLoaderError(f"Failed to list files in {directory_path}: {str(e)}")

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileLoaderError(f"File not found: {file_path}")

            return file_path.stat().st_size

        except Exception as e:
            raise FileLoaderError(f"Failed to get file size for {file_path}: {str(e)}")

    def get_file_modified_time(self, file_path: str) -> float:
        """
        Get file modification time as timestamp.

        Args:
            file_path: Path to the file

        Returns:
            Modification time as timestamp
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileLoaderError(f"File not found: {file_path}")

            return file_path.stat().st_mtime

        except Exception as e:
            raise FileLoaderError(f"Failed to get modification time for {file_path}: {str(e)}")

    def ensure_directory_exists(self, directory_path: str) -> None:
        """
        Ensure a directory exists, create it if it doesn't.

        Args:
            directory_path: Path to the directory
        """
        try:
            directory = Path(directory_path)
            directory.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            raise FileLoaderError(f"Failed to create directory {directory_path}: {str(e)}")

    def load_template_with_variables(self, template_path: str, variables: Dict[str, str]) -> str:
        """
        Load a text template and replace variables.

        Args:
            template_path: Path to the template file
            variables: Dictionary of variables to replace in the template

        Returns:
            Template content with variables replaced
        """
        try:
            template_content = self.load_text_file(template_path)

            # Simple variable replacement using string formatting
            for key, value in variables.items():
                placeholder = "{" + key + "}"
                template_content = template_content.replace(placeholder, str(value))

            return template_content

        except Exception as e:
            raise FileLoaderError(f"Failed to process template {template_path}: {str(e)}")


class FileLoaderError(Exception):
    """Custom exception for file loading errors."""
    pass