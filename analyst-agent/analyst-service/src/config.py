# ABOUTME: Configuration management and environment variable handling for the Data Analyst Agent
# ABOUTME: Provides centralized configuration loading, validation, and logging setup

# Set matplotlib backend before any imports to prevent macOS GUI threading issues
import matplotlib
matplotlib.use('Agg')

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the Data Analyst Agent."""

    def __init__(self):
        """Initialize configuration with validation."""
        self._load_config()
        self._validate_config()
        self._setup_logging()

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        try:
            # OpenAI Configuration
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4.1')

            # Debug Configuration
            self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
            self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

            # File Configuration
            self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
            self.allowed_file_types = os.getenv('ALLOWED_FILE_TYPES', 'csv,xlsx,xls').split(',')

            # Output Configuration
            self.output_dir = os.getenv('OUTPUT_DIR', './results')
            self.graph_output_dir = os.getenv('GRAPH_OUTPUT_DIR', './results')

            # Frontend Debug Configuration
            self.frontend_debug = os.getenv('FRONTEND_DEBUG', 'false').lower() == 'true'
            self.frontend_log_level = os.getenv('FRONTEND_LOG_LEVEL', 'INFO').upper()
            self.show_analysis_progress = os.getenv('SHOW_ANALYSIS_PROGRESS', 'false').lower() == 'true'
            self.log_request_ids = os.getenv('LOG_REQUEST_IDS', 'false').lower() == 'true'

            logging.debug("Configuration loaded successfully from environment variables")

        except Exception as e:
            logging.error(f"Failed to load configuration: {str(e)}")
            raise RuntimeError(f"Configuration loading failed: {str(e)}")

    def _validate_config(self) -> None:
        """Validate critical configuration values."""
        try:
            validation_errors = []

            # Validate OpenAI API Key
            if not self.openai_api_key:
                validation_errors.append("OPENAI_API_KEY is required but not set")

            if not self.openai_api_key or not self.openai_api_key.strip():
                validation_errors.append("OPENAI_API_KEY cannot be empty")

            # Validate log level
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.log_level not in valid_log_levels:
                validation_errors.append(f"LOG_LEVEL must be one of {valid_log_levels}")

            # Validate frontend log level
            if self.frontend_log_level not in valid_log_levels:
                validation_errors.append(f"FRONTEND_LOG_LEVEL must be one of {valid_log_levels}")

            # Validate file size limit
            if self.max_file_size_mb <= 0:
                validation_errors.append("MAX_FILE_SIZE_MB must be a positive integer")

            # Validate file types
            if not self.allowed_file_types:
                validation_errors.append("ALLOWED_FILE_TYPES cannot be empty")

            # Validate model name
            if not self.openai_model or not self.openai_model.strip():
                validation_errors.append("OPENAI_MODEL cannot be empty")

            if validation_errors:
                error_msg = "Configuration validation failed: " + "; ".join(validation_errors)
                logging.error(error_msg)
                raise ValueError(error_msg)

            logging.debug("Configuration validation completed successfully")

        except Exception as e:
            logging.error(f"Configuration validation failed: {str(e)}")
            raise

    def _setup_logging(self) -> None:
        """Setup logging configuration based on environment settings."""
        try:
            # Check if root logger already has handlers (configured by frontend)
            root_logger = logging.getLogger()

            if not root_logger.handlers:
                # Configure logging format
                log_format = '[%(name)s] %(asctime)s - %(levelname)s - %(message)s'

                # Set log level
                numeric_level = getattr(logging, self.log_level)

                # Configure root logger
                logging.basicConfig(
                    level=numeric_level,
                    format=log_format,
                    handlers=[
                        logging.StreamHandler()
                    ]
                )
                logging.info(f"[CONFIG] Logging configured with level: {self.log_level}")
            else:
                # Logging already configured (likely by frontend), just set level
                numeric_level = getattr(logging, self.log_level)
                root_logger.setLevel(numeric_level)
                logging.debug(f"[CONFIG] Using existing logging configuration, level set to: {self.log_level}")

            # Create output directories if they don't exist
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.graph_output_dir, exist_ok=True)

            logging.debug(f"[CONFIG] Debug mode: {self.debug}")

        except Exception as e:
            print(f"Failed to setup logging: {str(e)}")
            raise RuntimeError(f"Logging setup failed: {str(e)}")

    def get_openai_config(self) -> dict:
        """Get OpenAI configuration dictionary."""
        return {
            'api_key': self.openai_api_key,
            'model': self.openai_model
        }

    def get_file_config(self) -> dict:
        """Get file handling configuration dictionary."""
        return {
            'max_size_mb': self.max_file_size_mb,
            'allowed_types': self.allowed_file_types,
            'output_dir': self.output_dir,
            'graph_output_dir': self.graph_output_dir
        }

    def is_file_allowed(self, filename: str) -> bool:
        """Check if file type is allowed based on extension."""
        if not filename:
            return False

        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return file_extension in self.allowed_file_types

    def validate_file_size(self, file_size_bytes: int) -> bool:
        """Validate file size against configured limits."""
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        return file_size_bytes <= max_size_bytes

    def get_frontend_config(self) -> dict:
        """Get frontend debugging configuration dictionary."""
        return {
            'debug': self.frontend_debug,
            'log_level': self.frontend_log_level,
            'show_progress': self.show_analysis_progress,
            'log_request_ids': self.log_request_ids
        }

    def __str__(self) -> str:
        """String representation of configuration (excluding sensitive data)."""
        return f"""
Configuration:
- OpenAI Model: {self.openai_model}
- Debug Mode: {self.debug}
- Log Level: {self.log_level}
- Frontend Debug: {self.frontend_debug}
- Frontend Log Level: {self.frontend_log_level}
- Show Analysis Progress: {self.show_analysis_progress}
- Log Request IDs: {self.log_request_ids}
- Max File Size: {self.max_file_size_mb}MB
- Allowed File Types: {', '.join(self.allowed_file_types)}
- Output Directory: {self.output_dir}
- Graph Output Directory: {self.graph_output_dir}
"""


# Global configuration instance
config = Config()