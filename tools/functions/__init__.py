import importlib
from pathlib import Path


def register_files_in_functions_dir():
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
            globals()[module_name] = importlib.import_module(module_path)
            modules.append(module_name)
    return modules

modules_names = register_files_in_functions_dir()

__all__ = [
    module for module in modules_names
]
