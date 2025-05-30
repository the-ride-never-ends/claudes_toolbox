# get_tool_file_paths.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/common_/get_tool_file_paths.py`

## Table of Contents

### Functions

- [`get_tool_file_paths`](#get_tool_file_paths)

## Functions

## `get_tool_file_paths`

```python
def get_tool_file_paths(tool_dir)
```

Load Python tool files from a directory.

This function finds all Python files in a specified directory that don't
start with an underscore.

**Parameters:**

- `tool_dir (Path)` (`Any`): Directory path to search for tool files.

**Returns:**

- `list[Path]`: List of Path objects for each tool file found.

**Raises:**

- `FileNotFoundError`: If the directory doesn't exist or no valid tool files
are found in the directory.
