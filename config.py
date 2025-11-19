"""
Configuration management for the multi-agent system.
Handles environment variables and API keys.
"""

import os
from typing import Optional
from pathlib import Path


class Config:
    """Configuration manager for the multi-agent system."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Try to load from .env file if it exists
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)
        except ImportError:
            pass  # python-dotenv not installed

        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))

        # Database Configuration
        self.database_path = os.getenv('DATABASE_PATH', 'support.db')

        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

    def validate(self) -> bool:
        """Validate that required configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.openai_api_key:
            return False
        return True

    def get_openai_client(self):
        """Get configured OpenAI client.

        Returns:
            OpenAI client instance

        Raises:
            ValueError: If API key is not configured
        """
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable "
                "or create a .env file with your API key."
            )

        try:
            from openai import OpenAI
            return OpenAI(api_key=self.openai_api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Please run: pip install openai"
            )

    def set_api_key(self, api_key: str):
        """Set OpenAI API key programmatically.

        Args:
            api_key: OpenAI API key
        """
        self.openai_api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance.

    Returns:
        Config instance
    """
    return config
