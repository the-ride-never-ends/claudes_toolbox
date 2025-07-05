import importlib
from pathlib import Path
from logger import mcp_logger


def register_files_in_functions_dir() -> list[str]:
    """
    Register all Python files in the functions directory as modules.
    This allows for dynamic loading of function modules.
    """
    # Iterate over all files in the current directory
    modules = []
    for file in Path(__file__).parent.iterdir():
        if file.is_file() and file.suffix == ".py" and file.name != "__init__.py":
            module_name = file.stem
            module_path = f"tools.functions.{module_name}"
            # Register the module in the global namespace
            try:
                globals()[module_name] = importlib.import_module(module_path)
            except Exception as e:
                mcp_logger.exception(f"Failed to import module {module_name}: {e}")
                continue
            else:
                modules.append(module_name)
    # Sort the modules alphabetically
    return sorted(modules)

modules_names = register_files_in_functions_dir()

__all__ = [
    module for module in modules_names
]
