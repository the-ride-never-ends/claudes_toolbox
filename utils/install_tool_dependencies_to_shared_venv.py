from pathlib import Path
import subprocess


def install_tool_dependencies_to_shared_venv(requirements_file_paths: list[Path]) -> None:
    """
    Install tool dependencies to a shared virtual environment using venv.

    Args:
        requirements_file_paths (str): Paths to the requirements.txt files.
    """
    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        raise RuntimeError("uv is not installed. Please install it first.")

    # Install each tool's dependencies
    for path in requirements_file_paths:
        if path is None:
            continue

        try:
            results = subprocess.run(["uv", "add", "-r", path.resolve()])
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to install dependencies from {path}.") from e

        if results.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies from {path}.")

    print(f"All tools have been installed to the shared virtual environment at .venv.")
