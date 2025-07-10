import importlib
import inspect
from pathlib import Path
from typing import Callable


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


def get_function_tools_from_files(mcp: FastMCP) -> FastMCP:
    """
    Load functions from Python files in the tools directory and register them with the server

    This function scans the tools directory for Python files, imports them, and registers any
    functions that do not start with an underscore as tools in the server.
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
                    if name not in module_name:
                        continue

                    # Make sure it's a function (as opposed to a class, coroutine, etc.)
                    # and that it's not private
                    if inspect.isfunction(item) and not name.startswith("_"):
                        tool_name =  name
                        tool_desc = item.__doc__ 
                        if not tool_desc:
                            logger.warning(f"Function '{name}' in module '{module_name}' has no docstring. Skipping.")
                            continue

                        # Load and register the function as a tool
                        func: Callable = getattr(module, name)

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
                continue
    finally:
        return mcp