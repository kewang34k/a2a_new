"""
Configuration module for Multi-Agent Customer Support System
Centralizes all system settings, constants, and configuration values.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    db_path: str = "support.db"
    enable_foreign_keys: bool = True
    connection_timeout: int = 30
    check_same_thread: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    
    log_directory: str = "logs"
    log_prefix: str = "a2a_coordination"
    log_format: str = "[{timestamp}] {message}"
    timestamp_format: str = "%H:%M:%S.%f"
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    max_log_file_size_mb: int = 10
    max_log_files: int = 5


@dataclass
class AgentConfig:
    """Agent configuration settings."""
    
    router_agent_name: str = "RouterAgent"
    customer_data_agent_name: str = "CustomerDataAgent"
    support_agent_name: str = "SupportAgent"
    
    # Agent behavior settings
    max_query_length: int = 1000
    default_priority: str = "medium"
    default_coordination_type: str = "simple"
    
    # Response limits
    max_customers_display: int = 5
    max_tickets_display: int = 5
    max_ticket_history_display: int = 10


@dataclass
class MCPConfig:
    """MCP (Model Context Protocol) server configuration."""
    
    server_name: str = "customer_support_mcp"
    server_version: str = "1.0.0"
    enable_mcp_tools: bool = True
    
    # Tool limits
    max_customers_per_query: int = 100
    max_tickets_per_query: int = 100


@dataclass
class SystemConfig:
    """System-wide configuration settings."""
    
    system_name: str = "A2A-CoordinationSystem"
    version: str = "1.0.0"
    
    # Paths
    base_directory: Path = field(default_factory=lambda: Path.cwd())
    database_directory: Path = field(default_factory=lambda: Path.cwd())
    logs_directory: Path = field(default_factory=lambda: Path("logs"))
    
    # Performance settings
    max_concurrent_queries: int = 10
    query_timeout_seconds: int = 60
    
    # Feature flags
    enable_interactive_mode: bool = True
    enable_test_scenarios: bool = True
    enable_export_logs: bool = True


class Config:
    """Main configuration class that aggregates all configuration sections."""
    
    def __init__(self):
        """Initialize configuration with defaults or environment variables."""
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self.agent = AgentConfig()
        self.mcp = MCPConfig()
        self.system = SystemConfig()
        
        # Load from environment variables if present
        self._load_from_env()
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Database settings
        if os.getenv("DB_PATH"):
            self.database.db_path = os.getenv("DB_PATH")
        
        # Logging settings
        if os.getenv("LOG_DIRECTORY"):
            self.logging.log_directory = os.getenv("LOG_DIRECTORY")
        
        if os.getenv("ENABLE_FILE_LOGGING"):
            self.logging.enable_file_logging = os.getenv("ENABLE_FILE_LOGGING").lower() == "true"
        
        # System settings
        if os.getenv("MAX_CONCURRENT_QUERIES"):
            self.system.max_concurrent_queries = int(os.getenv("MAX_CONCURRENT_QUERIES"))
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        # Create logs directory
        log_dir = Path(self.logging.log_directory)
        log_dir.mkdir(exist_ok=True)
        
        # Update system paths
        self.system.logs_directory = log_dir
    
    def get_database_path(self) -> str:
        """Get full database path."""
        return str(Path(self.database.db_path))
    
    def get_log_directory(self) -> Path:
        """Get log directory path."""
        return Path(self.logging.log_directory)
    
    def get_log_file_path(self, suffix: str = "") -> Path:
        """Get log file path with optional suffix.
        
        Args:
            suffix: Optional suffix to add to filename
            
        Returns:
            Path to log file
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.logging.log_prefix}_{timestamp}{suffix}.log"
        return self.get_log_directory() / filename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "database": {
                "db_path": self.database.db_path,
                "enable_foreign_keys": self.database.enable_foreign_keys,
                "connection_timeout": self.database.connection_timeout,
            },
            "logging": {
                "log_directory": str(self.logging.log_directory),
                "log_prefix": self.logging.log_prefix,
                "enable_file_logging": self.logging.enable_file_logging,
                "enable_console_logging": self.logging.enable_console_logging,
            },
            "agent": {
                "router_agent_name": self.agent.router_agent_name,
                "customer_data_agent_name": self.agent.customer_data_agent_name,
                "support_agent_name": self.agent.support_agent_name,
                "max_query_length": self.agent.max_query_length,
                "default_priority": self.agent.default_priority,
            },
            "mcp": {
                "server_name": self.mcp.server_name,
                "server_version": self.mcp.server_version,
                "enable_mcp_tools": self.mcp.enable_mcp_tools,
            },
            "system": {
                "system_name": self.system.system_name,
                "version": self.system.version,
                "max_concurrent_queries": self.system.max_concurrent_queries,
                "query_timeout_seconds": self.system.query_timeout_seconds,
            }
        }


# System constants
class Constants:
    """System-wide constants."""
    
    # Customer status values
    CUSTOMER_STATUS_ACTIVE = "active"
    CUSTOMER_STATUS_DISABLED = "disabled"
    CUSTOMER_STATUSES = [CUSTOMER_STATUS_ACTIVE, CUSTOMER_STATUS_DISABLED]
    
    # Ticket status values
    TICKET_STATUS_OPEN = "open"
    TICKET_STATUS_IN_PROGRESS = "in_progress"
    TICKET_STATUS_RESOLVED = "resolved"
    TICKET_STATUSES = [TICKET_STATUS_OPEN, TICKET_STATUS_IN_PROGRESS, TICKET_STATUS_RESOLVED]
    
    # Priority levels
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH]
    
    # Coordination types
    COORDINATION_SIMPLE = "simple"
    COORDINATION_SEQUENTIAL = "sequential"
    COORDINATION_PARALLEL = "parallel"
    COORDINATION_NEGOTIATION = "negotiation"
    COORDINATION_TYPES = [
        COORDINATION_SIMPLE,
        COORDINATION_SEQUENTIAL,
        COORDINATION_PARALLEL,
        COORDINATION_NEGOTIATION
    ]
    
    # Intent types
    INTENT_GET_CUSTOMER_DATA = "get_customer_data"
    INTENT_LIST_CUSTOMERS = "list_customers"
    INTENT_UPDATE_DATA = "update_data"
    INTENT_GET_HISTORY = "get_history"
    INTENT_SUPPORT_REQUEST = "support_request"
    INTENT_ACCOUNT_MANAGEMENT = "account_management"
    INTENT_BILLING_ISSUE = "billing_issue"
    INTENT_COMPLEX_QUERY = "complex_query"
    
    # Agent names
    AGENT_ROUTER = "RouterAgent"
    AGENT_CUSTOMER_DATA = "CustomerDataAgent"
    AGENT_SUPPORT = "SupportAgent"
    
    # Query keywords for intent detection
    KEYWORDS_GET_CUSTOMER = ["get customer", "customer information", "customer info", "customer id"]
    KEYWORDS_LIST_CUSTOMERS = ["list customers", "show customers", "all customers"]
    KEYWORDS_UPDATE = ["update", "change", "modify"]
    KEYWORDS_TICKET_HISTORY = ["ticket history", "show tickets", "my tickets", "ticket status"]
    KEYWORDS_SUPPORT = ["help", "support", "issue", "problem", "need assistance"]
    KEYWORDS_ACCOUNT = ["upgrade", "downgrade", "cancel", "subscription"]
    KEYWORDS_BILLING = ["billing", "charged", "refund", "payment"]
    KEYWORDS_URGENT = ["urgent", "immediately", "asap", "critical", "emergency"]
    KEYWORDS_HIGH_PRIORITY = ["charged twice", "can't login", "website down"]
    
    # Response messages
    MSG_SUCCESS = "Operation completed successfully"
    MSG_ERROR = "An error occurred while processing your request"
    MSG_NOT_FOUND = "The requested resource was not found"
    MSG_INVALID_INPUT = "Invalid input provided"
    MSG_TIMEOUT = "Request timed out"
    
    # Display separators
    SEPARATOR_LINE = "=" * 80
    SEPARATOR_DASH = "-" * 80


# Global configuration instance
_config_instance: Config = None


def get_config() -> Config:
    """Get global configuration instance (singleton pattern).
    
    Returns:
        Global Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """Reload configuration from environment variables."""
    global _config_instance
    _config_instance = Config()
    return _config_instance


def get_constants() -> Constants:
    """Get constants instance.
    
    Returns:
        Constants instance
    """
    return Constants()


# Convenience functions for common config access
def get_database_path() -> str:
    """Get database path from config."""
    return get_config().get_database_path()


def get_log_directory() -> Path:
    """Get log directory from config."""
    return get_config().get_log_directory()


def get_log_file_path(suffix: str = "") -> Path:
    """Get log file path from config."""
    return get_config().get_log_file_path(suffix)
