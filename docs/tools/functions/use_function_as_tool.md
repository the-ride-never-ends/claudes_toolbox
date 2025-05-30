# use_function_as_tool.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/functions/use_function_as_tool.py`

## Module Description

Use a function in this folder as an MCP tool.

Hacky way to get around MCP's 129 tool limit.

## Table of Contents

### Functions

- [`_call_function_and_return_results`](#_call_function_and_return_results)
- [`_verify_tool_call`](#_verify_tool_call)
- [`use_function_as_tool`](#use_function_as_tool)

## Functions

## `_call_function_and_return_results`

```python
def _call_function_and_return_results(function_name, function, args_dict=None, kwargs_dict=None)
```

Call a function with the provided arguments and return the result.

## `_verify_tool_call`

```python
def _verify_tool_call(function_name, functions_docstring)
```

Verify that the function exists in the tools directory and that its docstring matches the provided docstring.
    This is to make sure the LLM didn't hallucinate the function or its docstring.

## `use_function_as_tool`

```python
def use_function_as_tool(function_name, functions_docstring, args_dict=None, kwargs_dict=None)
```

Use a function in this folder as a tool.

**Parameters:**

- `function_name (str)` (`Any`): The name of the function to use as a tool.

- `functions_docstring (str)` (`Any`): The docstring of the function to use as a tool.

- `args_dict (dict[str, Any])` (`Any`): A dictionary of positional arguments to pass to the function.
  The order of the keys must match the order of the function's arguments.

- `kwargs_dict (dict[str, Any])` (`Any`): A dictionary of keyword arguments to pass to the function.

**Returns:**

- `dict[(str, Any)]`: A dictionary with the following:
        - The name of the function.
        - The result of the function call, if any.

**Raises:**

- `FileNotFoundError`: If the function is not found in the tools directory.
ImportError: If the module for the function cannot be imported.
AttributeError: If the function isn't in the module or isn't callable.
ValueError: If there is an error calling the function.
