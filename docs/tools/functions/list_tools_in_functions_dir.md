# list_tools_in_functions_dir.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/functions/list_tools_in_functions_dir.py`

## Table of Contents

### Functions

- [`list_tools_in_functions_dir`](#list_tools_in_functions_dir)

## Functions

## `list_tools_in_functions_dir`

```python
def list_tools_in_functions_dir(get_docstring=True)
```

Lists all function-based tool files in the tools directory, excluding itself.

**Parameters:**

- `get_docstring (bool)` (`Any`): If True, gets the tool's docstring. Defaults to True.

**Returns:**

- `list[dict[(str, str)]]`: List of dictionaries containing Python filenames (without .py extension).
        If `get_docstring` is True, each dictionary will also contain the tool's docstring.
