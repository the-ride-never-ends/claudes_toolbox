from pathlib import Path


from logger import logger


def get_tool_file_paths(tool_dir: Path) -> list[Path]:
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
