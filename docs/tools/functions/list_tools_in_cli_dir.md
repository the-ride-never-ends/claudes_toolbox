# list_tools_in_cli_dir.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/functions/list_tools_in_cli_dir.py`

## Table of Contents

### Functions

- [`_get_program_name_from`](#_get_program_name_from)
- [`_get_name_and_help_menu`](#_get_name_and_help_menu)
- [`_has_argparse_parser`](#_has_argparse_parser)
- [`_find_program_entry_point`](#_find_program_entry_point)
- [`list_tools_in_cli_dir`](#list_tools_in_cli_dir)

## Functions

## `_get_program_name_from`

```python
def _get_program_name_from(help_output)
```

## `_get_name_and_help_menu`

```python
def _get_name_and_help_menu(file, run_as_module=False, timeout=10)
```

## `_has_argparse_parser`

```python
def _has_argparse_parser(content)
```

## `_find_program_entry_point`

```python
def _find_program_entry_point(entrance_dir)
```

## `list_tools_in_cli_dir`

```python
def list_tools_in_cli_dir(get_help_menu=True)
```

Lists all working argparse-based CLI tool files in the tools/cli directory.

**Parameters:**

- `get_help_menu (bool)` (`Any`): If True, gets the tool's docstring. Defaults to True.

**Returns:**

- `list[dict[(str, str)]]`: List of dictionaries containing Python filenames (without .py extension).
        If `get_help_menu` is True, each dictionary will also contain the tool's help menu.
    If no working tools are found, returns an empty list.
