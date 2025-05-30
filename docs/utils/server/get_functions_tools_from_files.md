# get_functions_tools_from_files.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/server/get_functions_tools_from_files.py`

## Table of Contents

### Functions

- [`get_function_tools_from_files`](#get_function_tools_from_files)

## Functions

## `get_function_tools_from_files`

```python
def get_function_tools_from_files(mcp)
```

Load functions from Python files in the tools directory and register them with the server

This function scans the tools directory for Python files, imports them, and registers any
functions that do not start with an underscore as tools in the server.
