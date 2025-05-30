from pathlib import Path
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler
log_file = os.path.join(os.path.dirname(__file__), 'use_cli_program_as_tool.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)


def _get_program_name_from(help_output: str) -> str:
    import re
    # Extract program name from usage line.
    patterns = [
        r'usage:\s+(\S+)',  # Standard: "usage: program_name"
        r'Usage:\s+(\S+)',  # Capitalized: "Usage: program_name"
        r'^(\S+)\s+\[',     # Program name at start with options
    ]
    program_name = None
    for pattern in patterns:
        match = re.search(pattern, help_output, re.MULTILINE)
        if match:
            program_name = match.group(1)
            break
    if program_name is None:
        raise ValueError("Could not extract program name from help output.")
    return program_name

def _run_python_command(
    file: Path, 
    python_cmd: str = 'python',
    cli_arguments: list[str] = [],
    timeout: int = 10 # seconds
    ) -> tuple[str, str]:
    import subprocess

    cmd_list: list[str] = [python_cmd, str(file.resolve())]
    if cli_arguments:
        cmd_list.extend(cli_arguments)

    try:
        results = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        logger.debug(f"Command results: {results}")
        # Help menu route
        if cli_arguments and cli_arguments[-1] == '--help':
            help_menu = results.stdout.strip()
            return _get_program_name_from(help_menu), help_menu
        # Actual program output route
        else:
            output = results.stdout.strip()
            if results.stderr.strip():
                output += f"\nStderr: {results.stderr.strip()}"
            if output is None:
                output = """
Command completed successfully with return code 0, but gave no stdout or stderr output.
This may indicate that the program does not produce console output or that it was run with no arguments.
If you expected console output, please check the program's functionality or its arguments.
            """
            return file.stem, output

    except subprocess.CalledProcessError as e:
        error_string = e.stdout.strip() or "No output"
        if e.stderr:
            error_string += f"\nError output: {str(e.stderr).strip()}"
        raise Exception(f"CalledProcessError running {file.name}: {error_string}") from e
    except Exception as e:
        raise Exception(f"A {type(e).__name__} occurred while running {file.name}: {e}") from e

def _has_argparse_parser(content: str) -> bool:
    import ast
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    if (hasattr(node.value.func, 'attr') and 
                        node.value.func.attr == 'ArgumentParser'):
                        return True
    except:
        return False
    return False

def _validate_program_name(program_name: str) -> None:
    """
    Validate the program name to ensure the LLM didn't put in anything unexpected.
    """
    # Prevent the LLM from putting in a file path instead of a program name.
    if Path(program_name).is_file():
        raise ValueError("The program_name argument should be the name of the program, not a file path.")

    # Prevent the LLM from putting in anything but valid python names.
    if '/' in program_name or '\\' in program_name or ' ' in program_name: # Catches "/this_program_name" or "this program name" or "this\program_name"
        raise ValueError("The program_name argument should not contain slashes, backslashes, or spaces.")

    if program_name.startswith('_') or program_name.endswith('_'): # Catches "_this_program_name" or "this_program_name_"
        raise ValueError("The program_name argument should not start or end with an underscore.")


def _normalize_program_name(program_name: str) -> str:
    """
    Normalize the program name to ensure consistent matching.
    """
    return program_name.lower().replace(' ', '_').replace('-', '_').removesuffix('.py')


def use_cli_program_as_tool(
        program_name: str,
        cli_arguments: list[str] = [],
        ) -> dict[str, str]:
    """
    Run a argparse-based CLI tool files in the tools/cli directory.
    WARNING: This function does not validate the CLI program's authenticity, functionality, or security.
    It is the user's and LLM's responsibility to ensure that the program is safe to run.

    Args:
        program_name (str): The name of the program.
        cli_arguments (list[str], optional): Command-line arguments to pass to the tool, if it takes any.
            If not provided, defaults to an empty list, which is equivalent to running the tool without any arguments.
            e.g. 'python tools/cli/my_tool.py'.

    Returns:
        dict[str, str]: A dictionary containing the following:
            - 'name': The program_name argument.
            - 'results': The output of the tool when run with the provided arguments.
        If an error occurs, the dictionary will contain:
            - 'name': The program_name argument.
            - 'path': The path to the tool file.
            - 'help_menu': The tool's help menu, if available.
            - 'error': The name of the error that occured.
            - 'error_msg': A string describing the error that occurred.
    Raises:
        FileNotFoundError: If the program is not found in the tools directory.
        ValueError: If the program_name argument is invalid.
        Exception: If there is an error running the program or parsing its output.
    """
    # TODO This is a test to see if todo_finder is working.
    _validate_program_name(program_name)

    # Keep this path hardcoded so that we aren't running argparse tools we haven't vetted.
    tools_dir = Path(__file__).parent.parent
    cli_tools_dir = tools_dir / 'cli'

    # Get the virtual environment python executable directly
    venv_python = Path.cwd() / '.venv/bin/python'
    python_cmd = str(venv_python.resolve()) if venv_python.is_file() else 'python'

    help_menu = None
    for file in cli_tools_dir.rglob('*.py'):
        if not file.name.startswith('_'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue

            if not _has_argparse_parser(content):
                continue

            # Get name and help menu first.
                # NOTE We do this to avoid argparsers being in files like "main.py" or "cli.py"
                # And to see if we can run the program at all.
            try:
                name, help_menu = _run_python_command(file, python_cmd=python_cmd, cli_arguments=["--help"])
            except Exception as e:
                continue  # Skip files that can't show help

            # NOTE Prevents things like 'Todo Finder' from not matching 'todo_finder'
            normalized_name = _normalize_program_name(name)
            normalized_program_name = _normalize_program_name(program_name)
            if normalized_name != normalized_program_name:
                continue

            # Found the right program, now run it with actual arguments
            try:
                _, results = _run_python_command(file, python_cmd=python_cmd, cli_arguments=cli_arguments)
                return {
                    "name": program_name, 
                    "results": results
                }
            except Exception as e:
                return {
                    'name': program_name,
                    'path': str(file.resolve()),
                    'error': type(e).__name__,
                    'error_msg': str(e),
                    'help_menu': help_menu
                }

    # If we get here, program wasn't found
    raise FileNotFoundError(f"Program not found in cli tools directory '{cli_tools_dir.resolve()}'")
