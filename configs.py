"""
Server configuration settings.
"""
from __version__ import __version__


from dataclasses import dataclass, field
from functools import cached_property
import logging
import os
from pathlib import Path
from typing import LiteralString

try:
    import yaml
except ImportError:
    raise ImportError("Please install PyYAML to use this module: pip install pyyaml")

_ROOT_DIR = Path(__file__).parent


class InitializationError(Exception):
    """When a fatal error occurs during the initialization of the server."""

@dataclass
class Configs:
    """
    Configuration settings for the MCP server.

    Attributes:
        verbose: Enable verbose output
        log_level: The log level for the server and logger.
        host: Host for the server
        port: Port for the server
        reload: Enable auto-reload

    Properties:
        VERSION: The current version of the program.
        ROOT_DIR: The root directory of the project.
        LLM_API_KEY: The API key for the LLM service.
        PROJECT_NAME: The name of the project.
        OPERATING_SYSTEM: The operating system of the server.
        REQUIREMENTS_FILE_PATHS: List of paths for requirements.txt files.
    """
    verbose: bool = field(default=True, metadata={"description": "Enable verbose output"})
    log_level: int = field(default=logging.DEBUG, metadata={"description": "The log level for the server and logger."})
    host: str = field(default="0.0.0.0", metadata={"description": "Host for the server"})
    port: int = field(default=8000, metadata={"description": "Port for the server"})
    reload: bool = field(default=True, metadata={"description": "Enable auto-reload"})
    tool_timeout: int = field(default=60, metadata={"description": "Timeout for tool execution in seconds"})
    load_from_paths_csv: bool = field(default=False, metadata={"description": "Load from paths CSV"})
    update_readme_when_settings_are_changed: bool = field(default=False, metadata={"description": "Update examples in README when settings are changed"})
    search_dir: Path = field(default_factory=lambda: Path(__file__).parent, metadata={"description": "Directory to search for tools"})

    @property
    def VERSION(self) -> LiteralString:
        """The current version of the program."""
        return __version__

    @property
    def ROOT_DIR(self) -> Path:
        """The root directory of the project."""
        return Path(__file__).parent

    @property
    def LLM_API_KEY(self) -> str:
        """The API key for the LLM service."""
        return os.getenv("LLM_API_KEY", "your_api_key_here")

    @property
    def PROJECT_NAME(self) -> str:
        """The name of the project."""
        return os.getenv("PROJECT_NAME", "claudes_toolbox")

    @property
    def OPERATING_SYSTEM(self) -> str:
        """The operating system of the server."""
        match os.name:
            case "nt":
                return "Windows"
            case "posix":
                return "Linux"
            case _:
                raise ValueError(f"Unsupported operating system: {os.name}")

    @cached_property
    def REQUIREMENTS_FILE_PATHS(self) -> list[Path]:
        """List of paths for requirements.txt files."""
        _paths = [
            path for path in self.ROOT_DIR.glob("**/requirements.txt")
            if path.is_file() and path.name == "requirements.txt" and path.exists()
        ]
        return _paths

    def __getitem__(self, key: str) -> str:
        """Get the value of a configuration setting by its key."""
        if hasattr(self, key.lower()):
            return getattr(self, key)
        else:
            raise KeyError(f"Configuration key '{key}' not found.")

    def __setitem__(self, key: str, value: str) -> None:
        """Set the value of a configuration setting by its key."""
        if hasattr(self, key.lower()):
            setattr(self, key, value)
        else:
            raise KeyError(f"Configuration key '{key}' not found.")


# Load the YAML file and parse it into the dataclass
try:
    with open(_ROOT_DIR / "configs.yaml", "r") as f:
        data = yaml.safe_load(f)
except FileNotFoundError as e:
    raise InitializationError(f"Configuration file not found: {e}") from e
except yaml.error.YAMLError as e:
    raise InitializationError(f"YAML error: {e}") from e
except Exception as e:
    raise InitializationError(f"Unexpected error loading configuration: {e}") from e

try:
    configs = Configs(**data)
except Exception as e:
    raise InitializationError(f"Unexpected error parsing configs: {e}") from e