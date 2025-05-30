
from pathlib import Path

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

def _get_name_and_help_menu(
    file: Path, 
    timeout: int = 10 # seconds
    ) -> tuple[str, str]:
    import subprocess
    try:
        # Get the virtual environment python executable directly
        venv_python = Path.cwd() / '.venv/bin/python'
        python_cmd = str(venv_python.resolve()) if venv_python.is_file() else 'python'
        result = subprocess.run(
            [python_cmd, str(file.resolve()), '--help'],
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        help_menu = result.stdout.strip()
        return _get_program_name_from(help_menu), help_menu
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error running {file.name} with --help: {e.stderr.strip()}")
    except Exception as e:
        raise Exception(f"A {type(e).__name__} occurred while getting help menu for {file.name}: {e}") from e

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

def list_tools_in_cli_dir(get_help_menu: bool = True) -> list[dict[str, str]]:
    """
    Lists all working argparse-based CLI tool files in the tools/cli directory.

    Args:
        get_help_menu (bool): If True, gets the tool's docstring. Defaults to True.

    Returns:
        list[dict[str, str]]: List of dictionaries containing Python filenames (without .py extension).
            If `get_help_menu` is True, each dictionary will also contain the tool's help menu.
        If no working tools are found, returns an empty list.
    """
    # Keep this path hardcoded so that we aren't running argparse tools we haven't vetted.
    tools_dir = Path(__file__).parent.parent
    cli_tools_dir = tools_dir / 'cli'
    python_files = []

    for file in cli_tools_dir.rglob('*.py'):
        if not file.name.startswith('_'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if _has_argparse_parser(content):
                    name, help_menu = _get_name_and_help_menu(file)
                    file_dict = {
                        'name': name
                    }
                    if get_help_menu is True:
                        file_dict['help_menu'] = help_menu
                    python_files.append(file_dict)
            except Exception as e:
                # If an error occurs while reading the file and getting its traits, skip it.
                    # After all, if we can't even open the file and run the help menu, 
                    # it probably won't work as a valid tool with MCP anyways.
                #continue
                python_files.append({ # Debugging purposes only
                    'name': file.stem,  # Get the name without the .py extension
                    'path': str(file.resolve()),  # Get the name without the .py extension
                    'error': str(e)  # Store the error message
                })
                continue
        else:
            # python_files.append({ # Debugging purposes only
            #     'name': file.stem,  # Get the name without the .py extension
            #     'path': str(file.resolve()),  # Get the name without the .py extension
            #     'debug': 'This is a debugging message to indicate that this file is not a valid Python file or does not start with an underscore.' 
            # })
            # Skip non-Python files or files that start with an underscore
            continue

    if not python_files:
        return [] # Sort by name for consistent ordering
    return sorted(python_files, key=lambda x: x['name'])
