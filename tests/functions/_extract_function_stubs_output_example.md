# Function and Class stubs from '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/functions/find_orphaned_files.py'

Files last updated: 1751429147.9140825

Stub file last updated: 2025-07-05 11:52:24

## _extract_imports

```python
def _extract_imports(content: str, current_file: Path) -> list[tuple[str, bool, int, list[str]]]:
    """
    Extract all imported modules from a Python file.

Returns a list of tuples: (module_name, is_relative, level, imported_names)
where:
- module_name is the module being imported from (can be empty for "from . import x")
- is_relative is True for relative imports
- level is the number of dots for relative imports
- imported_names is a list of names being imported (for "from X import Y" style)
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## _resolve_import_to_paths

```python
def _resolve_import_to_paths(import_info: tuple[str, bool, int, list[str]], current_dir: Path, root_path: Path) -> list[Path]:
    """
    Given import information, resolve to possible file paths.

Args:
    import_info: (module_name, is_relative, level, imported_names)
    current_dir: Directory of the importing file
    root_path: Project root directory

Returns:
    List of possible paths for the imported module
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## find_orphaned_files

```python
def find_orphaned_files(root_path: str, exclude_patterns: list[str] = _COMMON_VENV_PATTERNS, save_file_path: str | None = None) -> list[str]:
    """
    Search through a Python codebase and identify files not imported by any other file,
excluding files and directories based on glob patterns via the glob module.

Args:
    root_path: Root directory to search.
    exclude_patterns: List of glob patterns relative to root_path. Patterns with '**' recurse,
        others match files/directories accordingly. Defaults to a list of common virtual environment patterns:
        ['venv/**', '.venv/**', 'env/**', '.env/**', 'virtualenv/**', '.virtualenv/**', 
        'pyenv/**', '.pyenv/**', 'conda/**', '.conda/**', '__pycache__/**', '*.egg-info/**'].
    save_file_path: If provided, the list of orphaned files will be saved to this file path.

Returns:
    Sorted list of absolute paths for Python files not imported by any other file.

Raises:
    FileNotFoundError: If root_path does not exist.
    ValueError: If root_path is not a directory or if the number of orphaned files exceeds a threshold (1000).
    OSError: If there are permission issues accessing files.
    TypeError: If exclude_patterns is not a list of strings when provided.
    IOError: If unable to write the list of orphaned files to the specified save_file_path.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A
