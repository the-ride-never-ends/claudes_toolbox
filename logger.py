from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import sys
from typing import Any, Annotated as Ann, Callable

try:
    from pydantic import validate_call, Field, PositiveInt, ValidationError, AfterValidator as AV

except ImportError:
    raise ImportError(
        "Pydantic is required for this module. Please install it with 'pip install pydantic'."
    )

from configs import configs, Configs


# TODO Figure out why this throws import errors when it's imported during unit tests.
# from utils.mcp_print import mcp_print
def mcp_print(input: Any) -> None:
    """
    Prints the input to the console.
    This is needed because print() won't log to an MCP debug file.

    Args:
        input: The input to print.
    """
    print(input, file=sys.stderr)

@validate_call
def get_logger(name: str,
                log_file_name: str = 'app.log',
                level:         Ann[PositiveInt, Field(gt=0)] = logging.INFO,
                max_size:      Ann[PositiveInt, Field(gt=0)] = 5*1024*1024,
                backup_count:  Ann[PositiveInt, Field(gt=0)] = 3
                ) -> logging.Logger:
    """Sets up a logger with both file and console handlers.

    Args:
        name: Name of the logger.
        log_file_name: Name of the log file. Defaults to 'app.log'.
        level: Logging level. Defaults to logging.INFO.
        max_size: Maximum size of the log file before it rotates. Defaults to 5MB.
        backup_count: Number of backup files to keep. Defaults to 3.

    Returns:
        Configured logger.

    Example:
        # Usage
        logger = get_logger(__name__)
    """
    if not log_file_name.strip():
        raise ValueError("log_file_name cannot be empty or whitespace")

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    console_handler = logging.StreamHandler()

    # Create 'logs' directory in the current working directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_file_path = os.path.join(logs_dir, log_file_name)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=max_size, backupCount=backup_count)

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


class McpLogger:
    """
    Custom logger for MCP server.
    Since MCP servers log to a specific log file, 
        and since it relies on the print command to log messages, 
        we need to create a custom logger to enforce formatting.
    """

    def __init__(self, 
                configs: Configs = None, 
                resources: dict[str, Callable] = None
                ) -> None:
        self.configs = configs
        self.resources = resources

        self.log_level: int = self.configs.log_level or logging.DEBUG
        if resources:
            try:
                self._print: Callable = self.resources['print']
            except KeyError:
                pass # Default to the built-in print function

    def _print(self, message: str) -> None:
        """Prints a message to the console and log file.

        Args:
            message: The message to print.
        """
        print(message) # , file=sys.stderr

    def _format_message(self, level_name: str, message: str) -> str:
        """Formats the log message with a timestamp and level name."""
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{time} [mcp-logger] [{level_name}] {message}"

    def info(self, message: str):
        """Logs an info message."""
        if self.log_level <= logging.INFO:
            self._print(self._format_message("INFO", message))

    def warning(self, message: str):
        """Logs a warning message."""
        if self.log_level <= logging.WARNING:
            self._print(self._format_message("WARNING", message))

    def error(self, message: str):
        """Logs an error message."""
        if self.log_level <= logging.ERROR:
            self._print(self._format_message("ERROR", message))

    def debug(self, message: str):
        """Logs a debug message."""
        if self.log_level <= logging.DEBUG:
            self._print(self._format_message("DEBUG", message))

    def critical(self, message: str):
        """Logs a critical message."""
        if self.log_level <= logging.CRITICAL:
            self._print(self._format_message("CRITICAL", message))

    def exception(self, message: str, exc_info: bool = True):
        """Logs an exception message."""
        if self.log_level <= logging.ERROR:
            error_message = message
            if exc_info:
                error_message += f"\n{traceback.format_exc()}"
            self._print(self._format_message("EXCEPTION", error_message))
    
    def __call__(self, message: str) -> None:
        """
        Allows the logger to be called like a function.
        This is primarily to prevent programming errors
        where the logger is not called with a message.
        """
        self.warning(f"""
        WARNING: McpLogger instance called instead of one of its methods.
        You probably meant to call one of them, so you should change your code to do that!
        message:\n{message}\n{traceback.format_exc()}
        """)


# Instantiate the logger singletons.
try:
    logger = get_logger(__name__, log_file_name=f'{configs.PROJECT_NAME}.log', level=configs.log_level)
except ValidationError as e:
    raise TypeError(f"Invalid argument types were passed to logger: {e}") from e

resources = {"print": mcp_print}

try:
    mcp_logger = McpLogger(configs=configs, resources=resources)
except Exception as e:
    raise RuntimeError(f"Failed to instantiate McpLogger: {e}") from e