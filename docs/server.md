# server.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/server.py`

## Module Description

An MCP server for serving CLI programs and utility functions to LLMs.

## Table of Contents

### Functions

- [`debug_mode`](#debug_mode)

### Classes

- [`ClaudesToolboxServer`](#claudestoolboxserver)
- [`TotalTools`](#totaltools)
- [`CliTools`](#clitools)

## Functions

## `debug_mode`

```python
def debug_mode()
```

## Classes

## `ClaudesToolboxServer`

```python
class ClaudesToolboxServer(object)
```

Organizing class for the MCP server and its CLI tools.

**Methods:**

- [`_install_tool_dependencies_to_shared_venv`](#_install_tool_dependencies_to_shared_venv)
- [`_run_tool`](#_run_tool)
- [`_sanitize_tool_inputs`](#_sanitize_tool_inputs)
- [`_turn_argparse_help_into_docstring`](#_turn_argparse_help_into_docstring)
- [`_validate_tool_paths`](#_validate_tool_paths)
- [`load_tools`](#load_tools)
- [`register_tools`](#register_tools)
- [`run`](#run)
- [`setup`](#setup)

### `_install_tool_dependencies_to_shared_venv`

```python
def _install_tool_dependencies_to_shared_venv(self)
```

Install tool dependencies to the server's shared virtual environment.

### `_run_tool`

```python
def _run_tool(self, cmd, tool_name)
```

### `_sanitize_tool_inputs`

```python
def _sanitize_tool_inputs(self, *args, **kwargs)
```

Sanitize CLI tool inputs to prevent various injection attacks.

**Parameters:**

- `args` (`Any`): Positional arguments.

- `kwargs` (`Any`): Keyword arguments.

**Raises:**

- `ValueError`: If any of the inputs are invalid.

### `_turn_argparse_help_into_docstring`

```python
def _turn_argparse_help_into_docstring(self, help_message)
```

Converts command-line argument documentation to Google-style docstring.

**Parameters:**

- `help_message (str)` (`Any`): The help message from argparse.

### `_validate_tool_paths`

```python
def _validate_tool_paths(self)
```

Validate the tool paths.

### `load_tools`

```python
def load_tools(self)
```

Get the attributes of a tool.

### `register_tools`

```python
def register_tools(self)
```

Register tools with the server.

### `run`

```python
def run(self)
```

Run the server.

### `setup`

```python
def setup(self)
```

Setup the server and tools, and install dependencies.

## `TotalTools`

```python
class TotalTools(object)
```

**Methods:**

- [`__call__`](#__call__)

### `__call__`

```python
def __call__(self)
```

## `CliTools`

```python
class CliTools(object)
```

A class to organize CLI tools.

**Methods:**

- [`_add_parameters`](#_add_parameters)
- [`_build_cli_command`](#_build_cli_command)
- [`_get_finished_cli_tool_paths`](#_get_finished_cli_tool_paths)
- [`_get_tool_path`](#_get_tool_path)
- [`_register_cli_tools`](#_register_cli_tools)
- [`_verify_cli_paths`](#_verify_cli_paths)
- [`codebase_search`](#codebase_search)
- [`documentation_generator`](#documentation_generator)
- [`lint_a_python_codebase`](#lint_a_python_codebase)
- [`run_tests_and_save_their_results`](#run_tests_and_save_their_results)
- [`test_generator`](#test_generator)

### `_add_parameters`

```python
def _add_parameters(self, cmd, **kwargs)
```

Add parameters to the command.
NOTE Because positional arguments are assigned a value when passed to the calling function,
we can treat them as keyword arguments as long as we call them first.

### `_build_cli_command`

```python
def _build_cli_command(self, tool_name, *args, **kwargs)
```

Build the command for the CLI tool.

### `_get_finished_cli_tool_paths`

```python
def _get_finished_cli_tool_paths(self)
```

### `_get_tool_path`

```python
def _get_tool_path(self, tool_name)
```

### `_register_cli_tools`

```python
def _register_cli_tools(self)
```

Register the tools with the server.

### `_verify_cli_paths`

```python
def _verify_cli_paths(self)
```

Verify that the CLI paths are correct.

### `codebase_search`

```python
def codebase_search(self, pattern, path='.', case_insensitive=False, whole_word=False, regex=False, extensions=None, exclude=None, max_depth=None, context=0, format='text', output=None, compact=False, group_by_file=False, summary=False)
```

Search codebase for patterns with structured output.

**Parameters:**

- `pattern` (`str`): The pattern to search for.

- `path` (`str`): The path to search in. Defaults to current directory.

- `case_insensitive` (`bool`): Perform case-insensitive search. Defaults to False.

- `whole_word` (`bool`): Match whole words only. Defaults to False.

- `regex` (`bool`): Interpret pattern as a regular expression. Defaults to False.

- `extensions` (`str`): Comma-separated list of file extensions to search (e.g., 'py,txt'). Defaults to None.

- `exclude` (`str`): Comma-separated list of glob patterns to exclude (e.g., '*.git*,*node_modules*'). Defaults to None.

- `max_depth` (`int`): Maximum directory depth to search. Defaults to None.

- `context` (`int`): Number of lines of context to include before and after matches. Defaults to 0.

- `format` (`str`): Output format (text or json). Defaults to "text".

- `output` (`str`): Write output to file instead of stdout. Defaults to None.

- `compact` (`bool`): Use compact output format (one line per match). Defaults to False.

- `group_by_file` (`bool`): Group results by file. Defaults to False.

- `summary` (`bool`): Include summary information in output. Defaults to False.

**Returns:**

- `CallToolResult`: Command output containing search results.

### `documentation_generator`

```python
def documentation_generator(self, input, output='docs', docstring_style='google', ignore=None, inheritance=True)
```

Generate documentation from Python source code.

**Parameters:**

- `input` (`str`): Path to Python file or directory to generate documentation from.

- `output` (`str`): Path to output directory for documentation. Defaults to "docs".

- `docstring_style` (`str`): Docstring style to parse (google, numpy, or rest). Defaults to "google".

- `ignore` (`list[str]`): Paths to ignore when generating documentation. Defaults to None.

- `inheritance` (`bool`): Enable enhanced inheritance documentation with class hierarchies. Defaults to True.

**Returns:**

- `CallToolResult`: Command output from the documentation generator.

### `lint_a_python_codebase`

```python
def lint_a_python_codebase(self, path='.', patterns=None, exclude=None, no_blank=False, no_trailing=False, no_newlines=False, dry_run=False, verbose=False)
```

Fix common linting issues in Python codebases.

**Parameters:**

- `path` (`str`): Target directory to process. Defaults to current directory.

- `patterns` (`list[str]`): File patterns to match. Defaults to None, which uses '**/*.py'.

- `exclude` (`list[str]`): Directories to exclude. Defaults to None, which uses ['.venv', '.git', '__pycache__'].

- `no_blank` (`bool`): Don't fix blank lines with whitespace. Defaults to False.

- `no_trailing` (`bool`): Don't fix trailing whitespace. Defaults to False.

- `no_newlines` (`bool`): Don't ensure files end with a newline. Defaults to False.

- `dry_run` (`bool`): Don't make any changes, just show what would be done. Defaults to False.

- `verbose` (`bool`): Print detailed information for each file. Defaults to False.

**Returns:**

- `CallToolResult`: Command output from the linting tool.

### `run_tests_and_save_their_results`

```python
def run_tests_and_save_their_results(self, path='.', check_all=False, mypy=False, flake8=False, lint_only=False, respect_gitignore=False)
```

Run unit tests, type checking, and linting for a specified Python project.

**Parameters:**

- `path` (`str`): Path to the project directory. Defaults to current directory.

- `check_all` (`bool`): Run tests, type checking, linting, and corner cutting checks. Defaults to False.

- `mypy` (`bool`): Run mypy type checking. Defaults to False.

- `flake8` (`bool`): Run flake8 linting. Defaults to False.

- `lint_only` (`bool`): Run only type checking and linting (no tests). Defaults to False.

- `respect_gitignore` (`bool`): Ignore files/folders listed in .gitignore during linting. Defaults to False.

**Returns:**

- `CallToolResult`: Command output containing test and linting results.

### `test_generator`

```python
def test_generator(self, name, description, test_parameter_json, output_dir='tests', harness='unittest')
```

Generate test files based on JSON input.

**Parameters:**

- `name` (`str`): Test name.

- `description` (`str`): A short description of the test.

- `test_parameter_json` (`str`): The file path to the test parameters JSON file.

- `output_dir` (`str`): Path to output directory for tests. Defaults to "tests".

- `harness` (`str`): Which python testing harness to use. Defaults to "unittest".

**Returns:**

- `CallToolResult`: Command output from the test generator.
