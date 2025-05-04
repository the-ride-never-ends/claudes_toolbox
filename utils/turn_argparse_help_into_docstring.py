import re
from typing import Any, Type


def _string_type_hints_to_python_type(type_str: str) -> Type:
    match type_str:
        case "int":
            return int
        case "float":
            return float
        case "str":
            return str
        case "bool":
            return bool
        case "list":
            return list
        case "dict":
            return dict
        case "tuple":
            return tuple
        case "set":
            return set
        case "None":
            return None
        case "any":
            return Any
        case _:  # Default to string
            return str


def turn_argparse_help_into_docstring(cmd_args_text: str) -> str:
    """Converts command-line argument documentation to Google-style docstring.

    Takes a string containing command-line argument help text (like from argparse)
    and converts it to a properly formatted Google-style docstring.
    
    Args:
        cmd_args_text (str): The command-line argument help text to convert.
            Expected to contain program usage, description, and argument details.

    Returns:
        str: A Google-style docstring with function description and args section.

    Example:
        Input text like:
        ```
        usage: my_script.py [-h] --input INPUT
        This is a description of my script.
        options:
          -h, --help       show help
          --input INPUT    Input file path (type: str)
        ```
        
        Would convert to:
        ```
        '''This is a description of my script.
        
        Args:
            input (str): Input file path.
        '''
        ```
    """
    # Extract program name and description
    lines = cmd_args_text.strip().split('\n')
    
    # Get the script name from the usage line
    script_name = re.search(r'usage: (\S+)', lines[0])
    script_name = script_name.group(1) if script_name else "script"
    
    # Find the description (text between usage line and options)
    description = ""
    idx = 1
    while idx < len(lines) and not lines[idx].startswith('options:'):
        if lines[idx].strip():
            description += lines[idx].strip() + " "
        idx += 1
    description = description.strip()

    # Skip the "options:" line
    idx += 1

    # Process arguments
    func_parts: list[dict] = []
    args_section = []

    while idx < len(lines):
        line = lines[idx].strip()
        idx += 1
        
        if not line:
            continue
            
        # Check if this is a new argument
        arg_match = re.search(r'(-[a-zA-Z-]+,)?\s*(--[a-zA-Z-]+)\s*([\w]+)?', line)
        
        arg_dict = {"name": None, "type": None}

        if arg_match:
            # Get argument name without -- prefix
            arg_name = arg_dict["name"] = arg_match.group(2).lstrip('-')
            
            # Extract argument description and type
            remainder = line[arg_match.end():].strip()
            
            # Look for type information
            type_match = re.search(r'\(type: ([^)]+)\)', remainder)
            arg_type = arg_dict["type"] = type_match.group(1) if type_match else "str"

            # Get the description
            description_text = remainder.split('(type:')[0].strip()
            if description_text.endswith(')'):
                description_text = re.sub(r'\s*\([^)]*\)\s*$', '', description_text)
            
            # Look for default value
            default_match = re.search(r'\(default: ([^)]+)\)', remainder)
            default_value = default_match.group(1) if default_match else None
            
            # Only include actual arguments (skip help, etc.)
            if arg_name not in ['h', 'help']:
                arg_desc = description_text
                if default_value and default_value not in ['None', '[]']:
                    arg_desc += f" Default: {default_value}."
                
                args_section.append(f"{arg_name} ({arg_type}): {arg_desc}")
    
    # Assemble the docstring
    docstring = f'"""{description}\n\n'
    
    if args_section:
        docstring += "Args:\n"
        for arg in args_section:
            docstring += f"    {arg}\n"
    
    docstring += '"""'
    
    return docstring
