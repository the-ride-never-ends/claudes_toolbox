import argparse
import importlib
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any, Annotated, Dict, List, Type, Union
import types


# Re-import necessary components due to code state reset
from typing import Any, Dict, Union


from argparse import (
    ArgumentParser,
    ArgumentError,
    ArgumentTypeError,
    FileType,
    HelpFormatter,
    ArgumentDefaultsHelpFormatter,
    RawDescriptionHelpFormatter,
    RawTextHelpFormatter,
    MetavarTypeHelpFormatter,
    Namespace,
    Action,
    ONE_OR_MORE,
    OPTIONAL,
    PARSER,
    REMAINDER,
    SUPPRESS,
    ZERO_OR_MORE
)
ALLOW_ABREV_ALSO_DISABLES_GROUPING_OF_SHORT_FLAGS: bool = False
EXIT_ON_ERROR_PARAM_EXISTS: bool = True
ARGUMENT_PARSER_READS_FROM_FILE_SYSTEM_ENCODING_ERROR_HANDLER: bool = False
CONST_ALWAYS_NONE_BY_DEFAULT: bool = False
DEPRECATED_EXISTS: bool = False
ADD_ARGUMENT_GROUP_IS_DEPRECATED: bool = False
# NOTE: This is in now ways good style, but like hell if I'm going to remember this bit of argparse history.
CALLING_ADD_ARGUMENT_GROUP_OR_ADD_MUTUALLY_EXCLUSIVE_GROUP_ON_MUTUALLY_EXCLUSIVE_GROUP_IS_DEPRECATED: bool = False

# Get the current Python version
# Since argparse has different imports, options, and behaviors in different Python versions
match sys.version_info[0:1]:
    case (3, 8):
        pass
    case (3, 9):
        pass
    case (3, 10):
        pass
    case (3, 11):
        pass
    case (3, 12):
        pass
    case (3, 13):
        pass
    case _:
        pass

# Set specific behaviors based on Python version
# This is essentially a compatibility layer that tracks the changes in argparse over time.
if sys.version_info < (3, 8):
    raise RuntimeError(f"Unsupported Python version: {sys.version_info[0:2]}. This script requires Python 3.8 or higher.")

if sys.version_info == (3, 8):
    ALLOW_ABREV_ALSO_DISABLES_GROUPING_OF_SHORT_FLAGS = True
    EXIT_ON_ERROR_PARAM_EXISTS = False

if sys.version_info >= (3, 8):
    from argparse import BooleanOptionalAction

if sys.version_info >= (3, 11):
    CONST_ALWAYS_NONE_BY_DEFAULT = True
    ADD_ARGUMENT_GROUP_IS_DEPRECATED = True
    CALLING_ADD_ARGUMENT_GROUP_OR_ADD_MUTUALLY_EXCLUSIVE_GROUP_ON_MUTUALLY_EXCLUSIVE_GROUP_IS_DEPRECATED = True

if sys.version_info >= (3, 12):
    ARGUMENT_PARSER_READS_FROM_FILE_SYSTEM_ENCODING_ERROR_HANDLER = True
else:
    print("Warning: This script has only been tested on Python 3.12.")

if sys.version_info >= (3, 13):
    DEPRECATED_EXISTS = True
    print("Warning: This script has only been tested on Python 3.12.")


DEFAULT_DB_PATH = "templates.db"

def extract_argument_traits(parser: ArgumentParser) -> Dict[str, Union[str, Dict[str, Any]]]:
    """Extracts all argument traits from a single parser."""
    result = {}
    for action in parser._actions:
        if action.dest == 'help':
            continue

        arg_info = {
            "option_strings": action.option_strings,
            "dest": action.dest,
            "default": action.default,
            "required": action.required,
            "nargs": action.nargs,
            "const": getattr(action, "const", None),
            "type": getattr(action, "type", None),
            "choices": getattr(action, "choices", None),
            "help": action.help,
            "metavar": action.metavar,
            "action": action.__class__.__name__,
        }

        arg_info = {k: v for k, v in arg_info.items() if v is not None}

        # Special handling for subparsers
        if action.__class__.__name__ == "_SubParsersAction":
            sub_result = {}
            for name, subparser in action.choices.items():
                sub_result[name] = extract_argument_traits(subparser)
            result[action.dest] = {
                "help": action.help,
                "subcommands": sub_result,
                "action": action.__class__.__name__
            }
        else:
            result[action.dest] = arg_info
    return result

def format_google_docstring(parser_structure: Dict[str, Any]) -> str:

    def format_arg(name: str, info: Dict[str, Any], indent: int = 4) -> str:
        indent_space = ' ' * indent
        desc = info.get("help", "No description")
        typ = info.get("type", str)
        required = info.get("required", False)
        default = info.get("default", None)
        line = f"{indent_space}{name} ({typ.__name__ if callable(typ) else typ})"
        if not required:
            line += f", optional"
        if default not in [None, False]:
            line += f", default={default}"
        line += f": {desc}"
        return line

    def recurse_args(args: Dict[str, Any], indent: int = 4) -> str:
        doc_lines = []
        for key, val in args.items():
            if key == "help" or key == "action":
                continue
            if key == "subcommands":
                for subcmd, subargs in val.items():
                    doc_lines.append(f"\n{' ' * indent}Subcommand `{subcmd}`:")
                    doc_lines.extend(recurse_args(subargs, indent + 4))
            else:
                doc_lines.append(format_arg(key, val, indent))
        return doc_lines

    docstring = f'"""Command-line interface for: {parser_structure["parser"]["description"]}\n\n'
    docstring += "Args:\n"
    docstring += "\n".join(recurse_args(parser_structure["parser"]["arguments"]))
    docstring += '\n"""'
    return docstring


def _validate_target_dir(target_dir) -> None:
    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory does not exist: {target_dir}")
    if not target_dir.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {target_dir}")
    if not any(target_dir.iterdir()):
        raise FileNotFoundError(f"Target directory is empty: {target_dir}")

def extract_argparse_info(content: str, file_path: str) -> dict:
    """Extract information about an argparse program from file content."""
    
    # Basic info
    info = {
        "file_path": str(file_path),
        "program_name": Path(file_path).stem,
        "description": "",
        "arguments": []
    }
    
    # Try to find description
    desc_match = re.search(r'ArgumentParser\(.*?description=[\'"]([^\'"]*)[\'"]', content, re.DOTALL)
    if desc_match:
        info["description"] = desc_match.group(1)
    
    # Find arguments (basic implementation)
    arg_matches = re.findall(r'add_argument\([\'"](-[-\w]+)[\'"].*?help=[\'"]([^\'"]*)[\'"]', content, re.DOTALL)
    for arg, help_text in arg_matches:
        info["arguments"].append({
            "name": arg,
            "help": help_text
        })
        
    return info

def import_from_file(module_name: str, file_path: Path) -> types.ModuleType:
    import importlib.util
    import importlib.machinery
    import sys
    loader = importlib.machinery.SourceFileLoader(module_name, file_path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    loader.exec_module(module)
    return module

def extract_argument_traits(parser: argparse.ArgumentParser) -> Dict[str, Union[str, Dict[str, Any]]]:
    """Extracts all argument traits from a single parser."""
    result = {}
    for action in parser._actions:
        if action.dest == 'help':
            continue

        arg_info = {
            "option_strings": action.option_strings,
            "dest": action.dest,
            "default": action.default,
            "required": action.required,
            "nargs": action.nargs,
            "const": getattr(action, "const", None),
            "type": getattr(action, "type", None),
            "choices": getattr(action, "choices", None),
            "help": action.help,
            "metavar": action.metavar,
            "action": action.__class__.__name__,
        }

        arg_info = {k: v for k, v in arg_info.items() if v is not None}

        # Special handling for subparsers
        if action.__class__.__name__ == "_SubParsersAction":
            sub_result = {}
            for name, subparser in action.choices.items():
                sub_result[name] = extract_argument_traits(subparser)
            result[action.dest] = {
                "help": action.help,
                "subcommands": sub_result,
                "action": action.__class__.__name__
            }
        else:
            result[action.dest] = arg_info
    return result


import pydantic
from pydantic import AfterValidator as AV, BaseModel, BeforeValidator as BV, Field
from typing import TypeAlias


class ParseAction:

    def __init__(self, action: argparse.Action):
        self.action = action



def parse_action(action: argparse.Action) -> Dict[str, Any]:
    try: # Python 3.9+
        boolean: TypeAlias = argparse.BooleanOptionalAction
    except AttributeError:
        boolean = None

    match action:
        case "store_const":
            return {"action": "store_const", "const": action.const, "dest": action.dest}
        case "store_true":
            return {"action": "store_true", "dest": action.dest}
        case "store_false":
            return {"action": "store_false", "dest": action.dest}
        case "append":
            return {"action": "append", "dest": action.dest}
        case "append_const":
            return {"action": "append_const", "const": action.const, "dest": action.dest}
        case "extend":
            return {"action": "extend", "dest": action.dest}
        case "count":
            return {"action": "count", "dest": action.dest}
        case "help":
            return {"action": "help", "dest": action.dest, "help": action.help}
        case "version":
            return {"action": "version", "dest": action.dest, "version": action.version}
        case issubclass(action, argparse.Action): # Custom action
            # TODO implement custom action parsing
            # From : https://docs.python.org/3/library/argparse.html
            #
            # class FooAction(argparse.Action):
            #     def __init__(self, option_strings, dest, nargs=None, **kwargs):
            #         if nargs is not None:
            #             raise ValueError("nargs not allowed")
            #         super().__init__(option_strings, dest, **kwargs)
            #     def __call__(self, parser, namespace, values, option_string=None):
            #         print('%r %r %r' % (namespace, values, option_string))
            #         setattr(namespace, self.dest, values)
            #
            # parser = argparse.ArgumentParser()
            # parser.add_argument('--foo', action=FooAction)
            # parser.add_argument('bar', action=FooAction)
            # args = parser.parse_args('1 --foo 2'.split())
            raise NotImplementedError(f"Custom action parsing not implemented for {action.__class__.__name__}")
        case _:
            if boolean and isinstance(action, boolean):
                return {
                    "action": action.__class__.__name__,
                    "dest": action.dest,
                }
            else:
                return {"action": "count", "dest": action.dest}



class ArgInfo(BaseModel):
        """
        Information about a single argument in an argparse program.
        """
        name: str = Field(..., description="The name of the argument.")
        option_strings: list[str] = Field(default_factory=list)
        dest: str = Field(default="")
        default: Any = Field(default=None, description="The default value of the argument.")
        required: bool = Field(default=False, description="Whether the argument is required.")
        nargs: int | str | None = Field(default=None, description="The the argument takes more than one value.")
        const: Annotated[Any, BV(getattr(const, "const"))] = None
        type: Union[Type, None] = None
        choices: Union[list[Any], None] = None
        help: str = Field(default="")
        metavar: Union[str, None] = None
        action: str = ""

        def __init__(cls, action: argparse.Action):
            return super().__init__(
                name=action.dest,
                option_strings=action.option_strings,
                dest=action.dest,
                default=action.default,
                required=action.required,
                nargs=action.nargs,
                const=getattr(action, "const", None),
                type=getattr(action, "type", None),
                choices=getattr(action, "choices", None),
                help=action.help or "",
            )
        
        @property
        def as_arg(self) -> str:
            """
            Get the argument as a string representation.
            """
            arg_str = f"{self.name}: "
            type_hint = f"{self.type.__name__}" if self.type else "Any"
            if self.nargs:
                name, type_hint = arg_str.split(":")
            if self.default is not None:
                arg_str += f"{type_hint} = {self.default}"
    
        @property
        def as_docstring_line(self) -> str:
            pass

        def format_as_func_string(self) -> str:
            """
            Format the argument information as a function signature string.
            """
            name = self.name
            parameters = []
            docstring = format_google_docstring(self.model_dump())
            arg_str = f"{self.name}: {self.type.__name__}" if self.type else self.name
            if self.nargs:
                arg_str += f" ({self.nargs})"
            if self.default is not None:
                arg_str += f" = {self.default}"
            return arg_str

        arg_info = {
            "option_strings": action.option_strings,
            "dest": action.dest,
            "default": action.default,
            "required": action.required,
            "nargs": action.nargs,
            "const": getattr(action, "const", None),
            "type": getattr(action, "type", None),
            "choices": getattr(action, "choices", None),
            "help": action.help,
            "metavar": action.metavar,
            "action": action.__class__.__name__,
        }

class ArgparseToFunction(BaseModel):
    """
    """
    func_name: str = Field(..., description="Name of the function to be generated from the argparse program.")
    description: str = Field(..., description="Description of the argparse program.")
    arguments: Dict[str, ArgInfo] = Field(default_factory=dict, description="Arguments of the argparse program.")
    usage: str = Field(default="", description="Usage string for the argparse program.")

    def __init__(self, parser: argparse.ArgumentParser):
        """
        Initialize the ArgparseToFunction model from an argparse.ArgumentParser instance.
        
        Args:
            parser (argparse.ArgumentParser): The argparse parser to extract information from.
        """
        super().__init__(
            parser_name=parser.prog,
            description=parser.description,
            arguments=extract_argument_traits(parser),
            usage=parser.format_usage
        )

    def _generate_function_signature(self) -> str:
        """
        Generate the function signature based on the arguments.
        
        Returns:
            str: The function signature as a string.
        """
        args = [arg.format_as_func_string() for arg in self.arguments.values()]
        return f"def {self.func_name}({', '.join(args)}) -> str:"

    def _format_args_in_docstring(self) -> str:
        pass



    def _generate_docstring(self) -> str:
        """
        Generate the docstring for the function.

        Returns:
            str: The docstring for the function.
        """
        return f'''"""
{self.description}
NOTE: This function is auto-generated from an argparse.ArgumentParser instance.
Results may produced unexpected results.
Args:
    {self._format_args()}
Returns:
    A string detailing the success of failure of the subprocess.
Example:
"""'''

    def _generate_definition(self) -> str:
        return f"""
def {self.func_name}({', '.join(arg.format_as_func_string() for arg in self.arguments.values())}):
"""
    def _generate_body(self) -> str:
        """
        Generate the body of the function.
        
        Returns:
            str: The body of the function as a string.
        """
        return f"""

"""



# full_parser_structure = {
#     "parser": {
#         "description": parser.description,
#         "arguments": extract_argument_traits(parser)
#     }
# }


def list_argparse_programs(
    target_dir: str,
    ignore_dir: list[str] = None,
) -> list[dict[str, str]]:
    """
    List all python-based argparse programs files in the target directory and its subdirectories.

    Args:
        target_dir (str): Path to the target directory.
        ignore_dir (list[str], optional): List of directories to ignore.
        file_extension (str, optional): File extension to search for. Defaults to ".py".

    Returns:
        list[dict[str, str]]: List of dictionaries containing the program's name, description, ar.
    """
    import argparse
    from pathlib import Path
    path_to_target_dir: Path = _validate_target_dir(Path(target_dir))
    import importlib
    import importlib.util
    import importlib.machinery
    import sys
    import os


    from typing import Callable, Any
    from .list_dir_posix_os import list_dir_posix_os
    from .read_multiple_files_from_posix_os import read_multiple_files_from_posix_os
    from .read_a_file_from_posix_os import read_a_file_from_posix_os
    import re

    # Validate the target directory (exists, is a directory, is not empty)

    # There are multiple places, both among files and within them, where a parser might be defined:
    # So we have to check for them all:

    if sys.version_info != (3, 12):
        print("This function has only been tested on Python 3.12. Continue at your own risk.")

    # List all files and directories in the target directory
    #files: list[str] = list_dir_posix_os(target_dir, as_directory_tree=False)
    files_to_check = []

    files_to_check_for = [
        "main.py",        # Most common entry point
        "cli.py",         # Very common for command-line interfaces
        "__main__.py",    # Common in packages meant to be run directly
        "app.py",         # Common for applications
        "run.py",         # Common runner script
        "server.py",      # Common for server applications
        "commands.py",    # Command collections
        "command.py",     # Individual command implementations
        "script.py",      # General scripts
        "tools.py",       # Tool collections
        "runner.py",      # Alternative runners
        "console.py",     # Console interfaces
        "scripts.py",     # Script collections
        "parser.py",      # Argument parsing
        "tool.py",        # Individual tools
        "entrypoint.py",  # Entry points
        "shell.py",       # Shell interfaces
        "argparser.py",   # Specific argument parser
        "interface.py",   # General interfaces
        "executable.py"   # Rarely named this way
    ]
    for root, dirs, files in Path(target_dir).walk():
        for file in files:
            if file in files_to_check_for:
                files_to_check.append(file)

    if files_to_check is None or len(files_to_check) == 0:
        raise FileNotFoundError(f"No obvious candidates for argparse (e.g. main.py, cli.py, etc.) found in the target directory: {target_dir}")

    # Import the argparse parser object using importlib
    for file in files_to_check:
        file: str
        target_file = Path(target_dir) / file

        # Open the file and check if it contains an argparse parser
        file_content = read_a_file_from_posix_os(str(target_file))

        # Look for common argparse patterns
        if "argparse.ArgumentParser" in file_content:

            # Get the argparse parser object
            module = import_from_file(target_file.stem, target_file)
            parser_name = "parser"
            if hasattr(parser_name, module):
                parser: argparse.ArgumentParser = getattr(module, parser_name)
                # Get full parser structure recursively
                result = {
                    "parser": {
                        "description": parser.description,
                        "arguments": extract_argument_traits(parser)
                    }
                }

                # Extract information about the argparse program
                parser_info = extract_argparse_info(file_content, target_file)
                if parser_info:
                    return [parser_info]

        # If we reach here, we need to do a more thorough search of all Python files
        all_python_files = []
        for root, dirs, files in os.walk(target_dir):
            pass
        if ignore_dir and any(ignored in root for ignored in ignore_dir):
            continue
        all_python_files.extend(
            str(Path(root) / file) for file in files if file.endswith(".py")
        )
        
        results = []
        for file_path in all_python_files:
            pass
        file_content = read_a_file_from_posix_os(file_path)
        if "argparse.ArgumentParser" in file_content:
            parser_info = extract_argparse_info(file_content, file_path)
            if parser_info:
                results.append(parser_info)
        
        return results




