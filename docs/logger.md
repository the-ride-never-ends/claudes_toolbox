# logger.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/logger.py`

## Table of Contents

### Functions

- [`mcp_print`](#mcp_print)
- [`get_logger`](#get_logger)

### Classes

- [`McpLogger`](#mcplogger)

## Functions

## `mcp_print`

```python
def mcp_print(input)
```

Prints the input to the console.
This is needed because print() won't log to an MCP debug file.

**Parameters:**

- `input` (`Any`): The input to print.

## `get_logger`

```python
def get_logger(name, log_file_name='app.log', level=logging.INFO, max_size=5 * 1024 * 1024, backup_count=3)
```

Sets up a logger with both file and console handlers.

**Parameters:**

- `name` (`str`): Name of the logger.

- `log_file_name` (`str`): Name of the log file. Defaults to 'app.log'.

- `level` (`int`): Logging level. Defaults to logging.INFO.

- `max_size` (`int`): Maximum size of the log file before it rotates. Defaults to 5MB.

- `backup_count` (`int`): Number of backup files to keep. Defaults to 3.

**Returns:**

- `logging.Logger`: Configured logger.

**Examples:**

```python
# Usage
    logger = get_logger(__name__)
```

## Classes

## `McpLogger`

```python
class McpLogger(object)
```

Custom logger for MCP server.
Since MCP servers log to a specific log file, 
    and since it relies on the print command to log messages, 
    we need to create a custom logger to enforce formatting.

**Methods:**

- [`_format_message`](#_format_message)
- [`_print`](#_print)
- [`critical`](#critical)
- [`debug`](#debug)
- [`error`](#error)
- [`exception`](#exception)
- [`info`](#info)
- [`warning`](#warning)

**Special Methods:**

- [`__call__`](#__call__)

### `_format_message`

```python
def _format_message(self, level_name, message)
```

Formats the log message with a timestamp and level name.

### `_print`

```python
def _print(self, message)
```

Prints a message to the console and log file.

**Parameters:**

- `message` (`str`): The message to print.

### `critical`

```python
def critical(self, message)
```

Logs a critical message.

### `debug`

```python
def debug(self, message)
```

Logs a debug message.

### `error`

```python
def error(self, message)
```

Logs an error message.

### `exception`

```python
def exception(self, message, exc_info=True)
```

Logs an exception message.

### `info`

```python
def info(self, message)
```

Logs an info message.

### `warning`

```python
def warning(self, message)
```

Logs a warning message.

### `__call__`

```python
def __call__(self, message)
```

Allows the logger to be called like a function.
This is primarily to prevent programming errors
where the logger is not called with a message.
