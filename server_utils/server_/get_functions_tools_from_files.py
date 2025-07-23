import importlib
import inspect
from pathlib import Path
from typing import Any, Callable
import traceback

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError


from logger import logger, mcp_logger
from configs import configs

def _get_tool_file_paths(tool_dir: Path) -> list[Path]:
    """Load Python tool files from a directory.

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
    if not tool_dir.exists():
        logger.warning(f"Tools directory not found at {tool_dir}")
        raise FileNotFoundError(f"Tools directory not found at {tool_dir}")

    # Find all Python files that don't start with underscore
    tool_files = [
        file for file in tool_dir.glob("*.py") 
        if file.is_file() 
        and not file.name.startswith("_")
    ]

    if not tool_files:
        logger.warning(f"No tool files found in {tool_dir}")
        raise FileNotFoundError(f"No tool files found in {tool_dir}")
    return tool_files


from functools import wraps
_MAX_OUTPUT_LENGTH = 20_000
_TRUNCATED_OUTPUT_LENGTH = 19_000

from mcp.types import CallToolResult, TextContent

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
    @wraps(func)
    def wrapped_tool(*args, **kwargs):
        logger.debug(f"Running tool '{func.__name__}' with args: {args}, kwargs: {kwargs}")
        error_msg = None
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Exception occurred while running tool '{func.__name__}': {e}\n{traceback.format_exc()}"
            logger.error(error_msg)
            mcp_logger.exception(error_msg)
        finally:
            if isinstance(result, str):
                if len(result) >= _MAX_OUTPUT_LENGTH:
                    # Truncate large outputs
                    result = result[:_TRUNCATED_OUTPUT_LENGTH] + "..."

            # Make sure results serialize correctly.
                # repr makes sure the results don't break JSON serialization
            result = repr(result) if error_msg is None else repr(error_msg)
            return result
    return wrapped_tool


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
    tool_dir = configs.ROOT_DIR / "tools" / "functions"
    tool_files = _get_tool_file_paths(tool_dir)

    try:
        for file in tool_files:
            module_name = file.stem
            try:
                # Skip files that start with an underscore
                if module_name.startswith("_"):
                    continue
                # Import the module using its relative path
                module = importlib.import_module(f"tools.functions.{module_name}")

                # Find all functions in the module that don't start with underscore
                for name in dir(module):
                    item = getattr(module, name)
                    #mcp_logger.debug(f"Checking item '{name}' in module '{module_name}'")

                    # Skip imports.
                        # We check this by making the name of the file the same as the function name
                    if name != module_name:
                        continue

                    # Make sure it's a function (as opposed to a class, coroutine, etc.)
                    # and that it's not private
                    if inspect.isfunction(item) and not name.startswith("_"):
                        # Load and register the function as a tool
                        func = item
                        tool_name =  name
                        tool_desc = func.__doc__ 
                        if not tool_desc:
                            logger.warning(f"Function '{name}' in module '{module_name}' has no docstring. Skipping.")
                            continue

                        # 

                        mcp.add_tool(func, name=tool_name, description=tool_desc)
                        mcp_logger.info(f"Registered tool: {tool_name}")

            except ImportError as e:
                mcp_logger.error(f"Error importing module {module_name}: {e}")
            except ValidationError as e:
                mcp_logger.error(f"Validation error for tool {module_name}: {e}")
            except Exception as e:
                import traceback
                mcp_logger.error(f"Unexpected error loading tool from {file}: {e}\n{traceback.format_exc()}")

    finally:
        return mcp