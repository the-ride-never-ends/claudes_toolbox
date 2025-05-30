import importlib
import inspect
from typing import Callable


from mcp.server.fastmcp import FastMCP


from logger import logger, mcp_logger
from configs import configs
from utils.common_.get_tool_file_paths import get_tool_file_paths


def get_function_tools_from_files(mcp: FastMCP) -> None:
    """
    Load functions from Python files in the tools directory and register them with the server

    This function scans the tools directory for Python files, imports them, and registers any
    functions that do not start with an underscore as tools in the server.
    """
    tool_dir = configs.ROOT_DIR / "tools" / "functions"
    tool_files = get_tool_file_paths(tool_dir)

    for file in tool_files:
        module_name = file.stem
        try:
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
        except Exception as e:
            mcp_logger.error(f"Error loading tool from {file}: {e}")
