from pathlib import Path
import subprocess as sub

from logger import mcp_logger

def install_tool_dependencies_to_shared_venv(requirements_file_paths: list[Path]) -> None:
    """
    Install tool dependencies to a shared virtual environment using venv.

    Args:
        requirements_file_paths (str): Paths to the requirements.txt files.
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
