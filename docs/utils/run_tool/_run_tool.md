# _run_tool.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/run_tool/_run_tool.py`

## Table of Contents

### Functions

- [`run_tool`](#run_tool)
- [`return_results`](#return_results)

### Classes

- [`_RunTool`](#_runtool)

## Functions

## `run_tool`

```python
def run_tool(*args, **kwargs)
```

Run a tool with the given arguments and keyword arguments.

This function can run both function tools and command line tools.

**Parameters:**

- `*args` (`Any`): Positional arguments to pass to the tool

- `**kwargs` (`Any`): Keyword arguments to pass to the tool

**Returns:**

- `CallToolResultType`: A CallToolResult object containing the result of the tool call.

## `return_results`

```python
def return_results(input)
```

Return the result of a tool call.

**Parameters:**

- `input` (`Any`): The result of the tool call, can be an arbitrary type or an exception.

**Returns:**

- `CallToolResultType`: A CallToolResultType object containing the result.

## Classes

## `_RunTool`

```python
class _RunTool(object)
```

**Methods:**

- [`_run_cli_tool`](#_run_cli_tool)
- [`_run_func_tool`](#_run_func_tool)
- [`result`](#result)

**Special Methods:**

- [`__call__`](#__call__)

### `_run_cli_tool`

```python
def _run_cli_tool(self, cmd_list, func_name)
```

Run a command line tool with the given command and function name.

**Parameters:**

- `cmd_list` (`list[str]`): The command to run.

- `func_name` (`str`): The name of the command line tool that called this.

**Returns:**

- `CallToolResultType`: A CallToolResultType object containing the result of the command.

### `_run_func_tool`

```python
def _run_func_tool(self, func, *args, **kwargs)
```

Run a function tool with the given function and arguments.

This can be used to run both synchronous and asynchronous functions.

**Parameters:**

- `func` (`Callable`): The function to execute.

- `*args` (`Any`): Positional arguments to pass to the function.

- `**kwargs` (`Any`): Keyword arguments to pass to the function.

**Returns:**

- `CallToolResultType`: The result of the function execution wrapped in a CallToolResultType.

### `result`

```python
def result(self, result)
```

Format the result of a tool call.

**Parameters:**

- `result` (`Any`): The result of the tool call, can be an arbitrary type or an exception.

**Returns:**

- `CallToolResultType`: A CallToolResultType object containing the result.

### `__call__`

```python
def __call__(self, *args, **kwargs)
```

Route to the appropriate tool caller based on the given arguments and keyword arguments.
