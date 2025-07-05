# """
# Use a function in this folder as an MCP tool.

# Hacky way to get around MCP's 129 tool limit.
# """
# from typing import Any, Callable
# import importlib

# def _call_function_and_return_results(
#     function_name: str,
#     function: Callable,
#     args_dict: dict[str, Any] = None,
#     kwargs_dict: dict[str, Any] = None,
#     ) -> dict[str, Any]:
#     """Call a function with the provided arguments and return the result."""
#     if kwargs_dict and args_dict:
#         result = function(*args_dict.values(), **kwargs_dict)
#     else:
#         if args_dict:
#             # If only args_dict is provided, call the function with positional arguments
#             result = function(*args_dict.values())
#         elif kwargs_dict:
#             # If only kwargs_dict is provided, call the function with keyword arguments
#             result = function(**kwargs_dict)
#         else:
#             result = function()
#     return {
#         'name': function_name,
#         'result': result
#     }

# def _verify_tool_call(
#         function_name: str, 
#         functions_docstring: str
#         ) -> None:
#     """
#     Verify that the function exists in the tools directory and that its docstring matches the provided docstring.
#         This is to make sure the LLM didn't hallucinate the function or its docstring.
#         # TODO There's probably a more elegant way to do this. Figure one out.
#     """
#     from tools.functions.list_tools_in_functions_dir import list_tools_in_functions_dir
#     tools = list_tools_in_functions_dir(get_docstring=True)
#     # Make sure the LLM didn't hallucinate the function.
#     tool = [
#         tool for tool in tools if tool['name'] == function_name
#     ]
#     if tool is None or not tool:
#         raise FileNotFoundError(f"Function '{function_name}' not found in tools directory.")
#     # Make sure the LLM didn't hallucinate the docstring.
#     if tool[0]['docstring'] != functions_docstring:
#         raise ValueError(f"Function '{function_name}' does not match the provided docstring. Please check it and try again.")

# def use_function_as_tool(
#         function_name: str, 
#         functions_docstring: str,
#         args_dict: dict[str, Any] = None, 
#         kwargs_dict: dict[str, Any] = None,
#         ) -> dict[str, Any]:
#     """
#     Use a function in the tools.functions directory as a tool.

#     Args:
#         function_name (str): The name of the function to use as a tool.
#         functions_docstring (str): The docstring of the function to use as a tool.
#         args_dict (dict[str, Any]): A dictionary of positional arguments to pass to the function.
#             The order of the keys must match the order of the function's arguments.
#         kwargs_dict (dict[str, Any]): A dictionary of keyword arguments to pass to the function.

#     Returns:
#         dict: A dictionary with the following:
#             - The name of the function.
#             - The result of the function call, if any.
#     Raises:
#         FileNotFoundError: If the function is not found in the tools directory.
#         ImportError: If the module for the function cannot be imported.
#         AttributeError: If the function isn't in the module or isn't callable.
#         ValueError: If there is an error calling the function.
#     """
#     _verify_tool_call(function_name, functions_docstring)

#     try:
#         module = importlib.import_module(f'tools.functions.{function_name}')
#         function = getattr(module, function_name)
#     except (ModuleNotFoundError, ImportError) as e:
#         raise ImportError(f"Could not import module for function '{function_name}': {e}")
#     except AttributeError:
#         raise AttributeError(f"Function '{function_name}' not found in module 'tools.functions.{function_name}'.")

#     assert callable(function), f"Function '{function_name}' is not callable."
#     try:
#         return _call_function_and_return_results(
#             function_name=function_name,
#             function=function,
#             args_dict=args_dict,
#             kwargs_dict=kwargs_dict
#         )
#     except Exception as e:
#         raise ValueError(f"Error calling function '{function_name}': {e}") from e


"""
Tool for dynamically executing functions from the tools.functions directory.
"""

import os
import importlib
import inspect
from typing import Any, Optional


def use_function_as_tool(
    function_name: str,
    functions_docstring: str,
    args_dict: Optional[dict[str, Any]] = None,
    kwargs_dict: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Execute functions from the tools.functions directory as MCP tools.

    Args:
        function_name (str): The exact name of the function to execute from the
            tools.functions directory. Must match an existing Python file and function
            name exactly (case-sensitive).
        functions_docstring (str): The complete docstring of the target function.
            Used for verification to ensure accurate function information and prevent
            hallucination of non-existent functions. Must match the actual function's
            docstring exactly.
        args_dict (dict[str, Any], optional): Dictionary containing positional arguments
            to pass to the target function. Keys represent parameter names and must be
            ordered to match the function's parameter sequence. Values can be of any
            type compatible with the target function. If None, no positional arguments
            are passed. Defaults to None.
        kwargs_dict (dict[str, Any], optional): Dictionary containing keyword arguments
            to pass to the target function. Keys must exactly match the function's
            parameter names. Values can be of any type compatible with the target
            function. If None, no keyword arguments are passed. Defaults to None.

    Returns:
        dict[str, Any]: A structured dictionary containing execution results with the following keys:
            - 'name' (str): The name of the function that was executed
            - 'result' (Any): The actual return value from the function execution,
              preserving the original type and structure returned by the target function

    Raises:
        FileNotFoundError: If the specified function_name does not exist in the
            tools.functions directory.
        ImportError: If the module containing the function cannot be imported due to
            Python import errors, missing dependencies, or syntax errors in the target file.
        AttributeError: If the function name exists as a file but the function itself
            is not found within the module, or if the found object is not callable.
        ValueError: If there is an error during function execution, including:
            - Incorrect argument types or values
            - Function-specific validation failures
            - Docstring verification failures

    Examples:
        >>> # Execute a simple function with positional arguments
        >>> result = use_function_as_tool(
        ...     "calculate_sum", 
        ...     "Calculate the sum of two numbers...",
        ...     args_dict={"a": 5, "b": 10}
        ... )
        >>> print(result)
        {'name': 'calculate_sum', 'result': 15}
        
        >>> # Execute a function with keyword arguments
        >>> result = use_function_as_tool(
        ...     "process_text",
        ...     "Process text with specified options...",
        ...     kwargs_dict={"text": "hello", "uppercase": True}
        ... )
        >>> print(result)
        {'name': 'process_text', 'result': 'HELLO'}
        
        >>> # Execute a function with both positional and keyword arguments
        >>> result = use_function_as_tool(
        ...     "format_data",
        ...     "Format data with given parameters...",
        ...     args_dict={"data": [1, 2, 3]},
        ...     kwargs_dict={"format": "json", "indent": 2}
        ... )
        >>> print(result)
        {'name': 'format_data', 'result': '[\\n  1,\\n  2,\\n  3\\n]'}
        
        >>> # Execute a parameterless function
        >>> result = use_function_as_tool(
        ...     "get_system_info",
        ...     "Retrieve system information..."
        ... )
        >>> print(result)
        {'name': 'get_system_info', 'result': {'os': 'linux', 'python': '3.9.0'}}

    Note:
        Function verification prevents execution of hallucinated functions by confirming
        both existence and docstring accuracy. The target function file should be located
        at tools/functions/{function_name}.py and contain a function with the same name.
        
        All exceptions from the target function are caught and re-raised as ValueError
        with additional context for easier debugging.
    """
    # Step 1: Check if the module file exists
    module_path = f"tools.functions.{function_name}"
    
    # Check if the file exists in the tools/functions directory
    # We need to handle different ways the tests might set up the path
    file_found = False
    
    # Try to import the module to check if it exists
    try:
        # First, try to import the module
        module = importlib.import_module(module_path)
        file_found = True
    except ImportError as e:
        # If import fails, check if it's because the file doesn't exist
        # or because of other import errors (syntax errors, etc.)
        
        # Try to find the file directly
        # Look in various possible locations based on how tests might set up paths
        for base_path in ['.', '..', '../..', os.getcwd()]:
            potential_file = os.path.join(base_path, 'tools', 'functions', f'{function_name}.py')
            if os.path.exists(potential_file):
                file_found = True
                break
        
        if not file_found:
            # Check if the module exists in sys.modules or can be found
            try:
                # Try using __import__ which might work differently
                __import__(module_path)
                file_found = True
            except ImportError:
                pass
        
        if not file_found:
            raise FileNotFoundError(
                f"Function '{function_name}' not found in tools.functions directory"
            )
        else:
            # File exists but import failed for other reasons
            raise ImportError(
                f"Failed to import module 'tools.functions.{function_name}': {str(e)}"
            )
    
    # Step 2: Get the function from the module
    if not hasattr(module, function_name):
        raise AttributeError(
            f"Module 'tools.functions.{function_name}' does not contain a function named '{function_name}'"
        )
    
    func = getattr(module, function_name)
    
    # Check if it's callable
    if not callable(func):
        raise AttributeError(
            f"'{function_name}' in module 'tools.functions.{function_name}' is not callable"
        )
    
    # Step 3: Validate the docstring
    actual_docstring = inspect.getdoc(func)
    if actual_docstring is None:
        actual_docstring = ""
    
    if actual_docstring != functions_docstring:
        raise ValueError(
            f"Docstring mismatch for function '{function_name}'. "
            f"Expected: {repr(functions_docstring)}, "
            f"Got: {repr(actual_docstring)}"
        )
    
    # Step 4: Prepare arguments
    args = []
    kwargs = {}
    
    if args_dict is not None:
        # Convert args_dict to a list of positional arguments
        # The keys should be in order of the function parameters
        args = list(args_dict.values())
    
    if kwargs_dict is not None:
        kwargs = kwargs_dict
    
    # Step 5: Execute the function
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        # Wrap any execution errors in ValueError
        raise ValueError(
            f"Error during function execution of '{function_name}': {type(e).__name__}: {str(e)}"
        )
    
    # Step 6: Return the result
    return {
        'name': function_name,
        'result': result
    }