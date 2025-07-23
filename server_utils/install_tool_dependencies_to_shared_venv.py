from pathlib import Path
import subprocess as sub


from logger import mcp_logger


def install_tool_dependencies_to_shared_venv(requirements_file_paths: list[Path]) -> None:
    """
    Install dependencies from multiple requirements.txt files to a shared virtual environment using uv.

    This function processes a list of requirements.txt file paths and installs their dependencies
    into the current virtual environment using the 'uv' package manager. It validates that uv
    is installed and available before proceeding.

    Args:
        requirements_file_paths (list[Path]): List of Path objects pointing to requirements.txt 
                                            files containing package dependencies to install.

    Returns:
        None

    Raises:
        RuntimeError: If uv is not installed or if installation of any requirements file fails.

    Note:
        - Skips non-existent file paths with a warning
        - Logs progress and results for each requirements file processed
        - Uses 'uv add -r' command to install packages
    """
    # Check if uv is installed
    try:
        sub.run(["uv", "--version"], check=True, capture_output=True)
    except (sub.SubprocessError, FileNotFoundError):
        raise RuntimeError("uv is not installed. Please install it first.") from e

    if requirements_file_paths is None:
        mcp_logger.info("No requirements.txt files found.")
    else:
        len_requirements_file_paths = len(requirements_file_paths)
        mcp_logger.info(f"Found {len_requirements_file_paths} requirements.txt files.")

    installed_tools = 0
    # Install each tool's dependencies
    for path in requirements_file_paths:
        abs_path = path.resolve()
        if not abs_path.exists():
            mcp_logger.warning(f"Path {abs_path.resolve()} does not exist. Skipping...")
            continue
        else:
            mcp_logger.info(f"Installing dependencies from {abs_path.resolve()}...")

            try:
                results = sub.run(["uv", "add", "-r", f"{abs_path}"],capture_output=True)
            except sub.SubprocessError as e:
                raise RuntimeError(f"Failed to install dependencies from {path}.") from e

            if results.returncode != 0:
                raise RuntimeError(f"""
    Failed to install dependencies from {path}.\nresults:{results.stdout}\nerror:{results.stderr}
            """)
            else:
                mcp_logger.info(f"Successfully installed dependencies from {path}.")
                installed_tools += 1

    mcp_logger.info(f"Installed {installed_tools} requirements for {len_requirements_file_paths} tools at .venv.")
