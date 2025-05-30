# use_cli_program_as_tool.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/functions/use_cli_program_as_tool.py`

## Table of Contents

### Functions

- [`_normalize_program_name`](#_normalize_program_name)
- [`_get_program_name_from`](#_get_program_name_from)
- [`_has_argparse_parser`](#_has_argparse_parser)
- [`_validate_program_name`](#_validate_program_name)
- [`_run_python_command`](#_run_python_command)
- [`_run_python_command_or_module`](#_run_python_command_or_module)
- [`_find_program_entry_point`](#_find_program_entry_point)
- [`use_cli_program_as_tool`](#use_cli_program_as_tool)

## Functions

## `_normalize_program_name`

```python
def _normalize_program_name(program_name)
```

Normalize the program name to ensure consistent matching.

## `_get_program_name_from`

```python
def _get_program_name_from(help_output)
```

## `_has_argparse_parser`

```python
def _has_argparse_parser(content)
```

## `_validate_program_name`

```python
def _validate_program_name(program_name)
```

Validate the program name to ensure the LLM didn't put in anything unexpected.

## `_run_python_command`

```python
def _run_python_command(file, python_cmd='python', cli_arguments=[], timeout=10)
```

## `_run_python_command_or_module`

```python
def _run_python_command_or_module(target_path, run_as_module=False, python_cmd='python', cli_arguments=[], timeout=30)
```

## `_find_program_entry_point`

```python
def _find_program_entry_point(entrance_dir)
```

Same as in list_tools_in_cli_dir - you'll need to copy this function

## `use_cli_program_as_tool`

```python
def use_cli_program_as_tool(program_name, cli_arguments=[])
```

Run a argparse-based CLI tool files in the tools/cli directory.
WARNING: This function does not validate the CLI program's authenticity, functionality, or security.
It is the user's and LLM's responsibility to ensure that the program is safe to run.

**Parameters:**

- `program_name (str)` (`Any`): The name of the program.

- `cli_arguments (list[str], optional)` (`Any`): Command-line arguments to pass to the tool, if it takes any.
  If not provided, defaults to an empty list, which is equivalent to running the tool without any arguments.
  e.g. 'python tools/cli/my_tool.py'.

**Returns:**

- `dict[(str, str)]`: A dictionary containing the following:
        - 'name': The program_name argument.
        - 'results': The output of the tool when run with the provided arguments.
    If an error occurs, the dictionary will contain:
        - 'name': The program_name argument.
        - 'path': The path to the tool file.
        - 'help_menu': The tool's help menu, if available.
        - 'error': The name of the error that occured.
        - 'error_msg': A string describing the error that occurred.

**Raises:**

- `FileNotFoundError`: If the program is not found in the tools directory.
ValueError: If the program_name argument is invalid.
Exception: If there is an error running the program or parsing its output.
