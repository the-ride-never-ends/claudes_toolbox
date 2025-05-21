import importlib
import inspect
from utils.common_.get_tool_file_paths import get_tool_file_paths


from mcp.server.fastmcp import FastMCP


from logger import logger, mcp_logger
from configs import configs

def get_cli_tools_from_files(mcp: FastMCP) -> None:
    """
    Load CLI tools from Python files in the tools directory and register them with the server.
    The CLI tools should all be argparse-based and have a function called `main` that takes the same arguments as the CLI tool.
    """
    # Get all Python files in the CLI tools directory
    cli_tool_dir = configs.ROOT_DIR / "tools" / "cli"
    try:
        tool_files = get_tool_file_paths(cli_tool_dir)
    except FileNotFoundError as e:
        logger.error(f"Error loading CLI tool files: {e}")
        return

    for file in tool_files:
        module_name = file.stem
        try:
            # Import the module using its relative path
            module = importlib.import_module(f"tools.cli.{module_name}")

            # Find all the files called "main" or have a function called "main"
            for name in dir(module):
                item = getattr(module, name)
                if inspect.isfunction(item) and name == "main":
                    tool_name = f"{module_name}_{name}" if name != module_name else name
                    tool_desc = item.__doc__ 
                    if not tool_desc:
                        logger.warning(f"Function '{name}' in module '{module_name}' has no docstring. Skipping.")
                        continue

                    # Load and register the function as a tool
                    func = getattr(module, name)
                    mcp.add_tool(func, name=tool_name, description=tool_desc)
                    mcp_logger.info(f"Registered CLI tool: {tool_name}")

        except ImportError as e:
            mcp_logger.error(f"Error importing module {module_name}: {e}")
        except Exception as e:
            mcp_logger.error(f"Error loading tool from {file}: {e}")
