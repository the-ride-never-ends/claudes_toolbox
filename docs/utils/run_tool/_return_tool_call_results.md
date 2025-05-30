# _return_tool_call_results.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/run_tool/_return_tool_call_results.py`

## Table of Contents

### Functions

- [`return_tool_call_results`](#return_tool_call_results)

## Functions

## `return_tool_call_results`

```python
def return_tool_call_results(content, error=False)
```

Returns a CallToolResult object for tool call response.

**Parameters:**

- `content` (`TextContent`): The content of the tool call result.

- `error` (`bool`): Whether the tool call resulted in an error. Defaults to False.

**Returns:**

- `CallToolResult`: The formatted result object containing the content and error status.
