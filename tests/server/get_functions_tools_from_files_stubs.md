# Function and Class stubs from '/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/server/get_functions_tools_from_files.py'

Files last updated: 1752457479.577458

Stub file last updated: 2025-07-13 18:45:12

## _get_tool_file_paths

```python
def _get_tool_file_paths(tool_dir: Path) -> list[Path]:
    """
    Load Python tool files from a directory.

This function finds all Python files in a specified directory that don't
start with an underscore.

Args:
    tool_dir (Path): Directory path to search for tool files.

Returns:
    list[Path]: List of Path objects for each tool file found.

Raises:
    FileNotFoundError: If the directory doesn't exist or no valid tool files 
        are found in the directory.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## _tool_wrapper

```python
def _tool_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that wraps tool functions to ensure proper output handling.

This wrapper performs the following operations:
- Truncates string outputs that exceed the maximum length limit
- Converts results to repr() format to ensure JSON serialization compatibility
- Preserves original function metadata through functools.wraps

Args:
    func: The function to be wrapped as a tool
    
Returns:
    Callable: The wrapped function with output processing applied
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A

## get_function_tools_from_files

```python
def get_function_tools_from_files(mcp: FastMCP) -> FastMCP:
    """
    Load and register function tools from Python files in the tools directory.

This function scans the tools/functions directory for Python files, imports each module,
and registers qualifying functions as MCP tools. Functions are registered if they:
- Have the same name as their containing file (e.g., 'example.py' contains 'example()')
- Are actual functions (not classes or other objects)
- Don't start with an underscore (not private)
- Have a docstring (used as the tool description)

Each registered function is wrapped to handle output truncation and JSON serialization.

Args:
    mcp (FastMCP): The FastMCP server instance to register tools with.

Returns:
    FastMCP: The same FastMCP instance with all discovered function tools registered.

Raises:
    FileNotFoundError: If the tools directory doesn't exist or contains no valid files.
    """
```
* **Async:** False
* **Method:** False
* **Class:** N/A
