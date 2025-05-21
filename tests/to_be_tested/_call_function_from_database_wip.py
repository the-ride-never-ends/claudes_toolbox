from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Any, Optional
import sys
import importlib
from contextlib import contextmanager



import os
import inspect

sys.path.insert(0, str(Path(__file__).parent.resolve()))


@contextmanager
def _create_temp_file_in_this_dir(temp_filename):
    """
    Creates a temporary file in the same directory as the calling file.
    
    Args:
        temp_filename (str): Name for the temporary file (without .py extension)
    
    Returns:
        str: Full path to the created temporary file
    
    Example:
        # If called from /path/to/functions/_get_function_from_database.py
        # with temp_filename="_this_function"
        # Returns: "/path/to/functions/_this_function.py"
        # And creates the file
    """
    try:
        # Get the frame of the calling function
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        caller_dir = os.path.dirname(os.path.abspath(caller_file))

        # Construct the path for the new temporary file
        temp_file_path = os.path.join(caller_dir, f"{temp_filename}.py")

        # Create the temporary file
        with open(temp_file_path, 'w') as f:
            pass  # Create empty file

        yield temp_file_path
    except Exception as e:
        raise RuntimeError(f"Failed to create temporary file: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)




class _MockDatabase:

    def __init__(self):
        self.functions = {}

    def get_function(self, function_name: str) -> Optional[dict]:
        return self.functions.get(function_name)

    def _search(self, function_name: str, function_data: dict):
        return self.functions[function_name]

    def search_by_name(self, function_name: str) -> Optional[dict]:
        return self.functions.get(function_name)
    
    def search_by_description(self, description: str) -> Optional[dict]:
        pass

    def search_by_cid(self, cid: str) -> Optional[dict]:
        pass

# Mock database for demonstration purposes
function_database = _MockDatabase()

# import the mcp server from the main module


def _call_function_from_database_wip(
    function_name: Optional[str] = None,
    cid: Optional[str] = None,
    args: Optional[dict] = {},
    kwargs: Optional[dict] = {},
) -> dict[str, Any]:
    """
    Retrieve and execute a python function stored in a SQL database.

    Args:
        function_name (str): The name of the function to query.
        cid (str): The Content ID of the function.
        args (dict): The positional arguments to pass to the function.
        kwargs (dict): The keyword arguments to pass to the function.

    Raises:
        ValueError: If both function_name and cid are provided.
        AttributeError: If the function 
        Exception: If there is an error retrieving the function from the database.

    Returns:
        A string that details the function's outcome, or an Exception that details the function's failure.
    """
    if function_name and cid:
        raise ValueError("Both function_name and cid cannot be provided at the same time.")
    if not function_name and not cid:
        raise ValueError("Either function_name or cid must be provided.")
    
    # Retrieve the function from the database
    if function_name:
        function_data: str = function_database.get_function(function_name)
        if function_data is None:
            raise ValueError(f"Function '{function_name}' not found in the database.")
    elif cid:
        function_data: str = function_database.get_function(cid)
        if function_data is None:
            raise ValueError(f"Function '{function_name}' not found in the database.")
    else:
        raise ValueError("Should not reach here. If it does, please check the logic.")
    
    # Write the function to a temporary file
    temp_file_path = Path(__file__).parent / f"{function_name}.py"
    temp_file_path.resolve()

    with _create_temp_file_in_this_dir(temp_file_path) as temp_file:

        # Write the function data to the temporary file
        with open(temp_file_path, "w") as temp_file:
            temp_file.write(function_data)

        # Check to make sure the file is written correctly
        if not temp_file_path.exists():
            raise Exception(f"Temporary file '{temp_file_path}' was not created.")

        # Import the function and add it to the global namespace
        # TODO
        imported_module = importlib.import_module(function_name)

        # Register the function in the global namespace


        # Register the function
        exec_globals = {}
        with open(temp_file_path) as temp_file:
            exec(temp_file.read(), exec_globals)
        
        # Call the function
        func = exec_globals[function_name]
        result = func(*args, **kwargs)

    return {
        "function_name": function_name,
        #"description": description,
        "cid": cid,
    }