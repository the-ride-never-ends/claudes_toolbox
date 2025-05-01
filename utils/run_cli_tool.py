import os
import subprocess


from utils.mcp_print import mcp_print


def run_cli_tool(cmd: list[str], func_name: str) -> str:
    """
    Run a command line tool with the given command and function name.

    Args:
        cmd: The command to run.
        func_name: The name of the function that called this.
    """
    mcp_print(f"Running {func_name} with command: {' '.join(cmd)}")

    # Activate the virtual environment and run the command
    match os.name:
        case "nt":
            # Windows
            cmd = ["cmd", "/c", ".venv\\Scripts\\activate.bat && " + " ".join(cmd)]
        case "posix":
            # Linux/macOS
            cmd = ["bash", "-c", "source .venv/bin/activate && " + " ".join(cmd)]
        case _:
            raise ValueError(f"Unsupported operating system: {os.name}")

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check if the command was successful and return the output
    if result.returncode == 0:
        mcp_print(f"{func_name} executed successfully.\n{func_name} output: {result.stdout}")
        return result.stdout
    else:
        raise ValueError(f"{func_name} failed: {result.stderr}")
