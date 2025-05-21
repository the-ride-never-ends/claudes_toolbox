from typing import Optional


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


def check_if_function_is_in_function_database(
    description: Optional[str] = None,
    function_name: Optional[str] = None,
    cid: Optional[str] = None,
) -> Optional[list[dict]]:
    """
    Check if a python function is stored in a SQL database.

    This function searches a SQL database of functions to find a specific function.
    If one or more functions are found, it returns a list of dictionaries containing the function's details.
    Each dictionary contains the following:
        - cid: The unique content ID of the function.
        - name: The name of the function.
        - parameters: A dictionary of the function's parameters, including:
            - name: The name of the parameter.
            - type: The type of the parameter.
            - default: The default value of the parameter (if any).
        - return_type: The return type of the function.
        - docstring: The function's docstring.

    NOTE: All options are mutually exclusive. If more than one is provided, the function raises a Value Error.

    Args:
        function_name (str): The name of the function.
        description (str): A natural language description of what the function does.
        cid (str): The unique content ID of the function.

    Returns:
        list[dict]: A list of dictionaries of potential functions that match the query.
        The list is ranked according to relevance to the input parameter.
        If no function is found, an empty list is returned.

    Raises:
        ValueError: If more than one of the function_name, description, or cid is provided.
        Exception: If there is an error retrieving the function from the database.

    Example:
        >>> check_if_function_is_in_function_database(
        ...     function_name="read_a_file_from_posix_os",
        ... )
        [
            {
                "cid": "12345",
                "name": "read_a_file_from_posix_os",
                "parameters": {
                    "name": "file_path"
                    "type": "str",
                },
                "return_type": "str",
                "docstring": '''
                    Read a file from a POSIX operating system.

                    Args:
                        file_path (str): The path to the file to be read.

                    Raises:
                        FileNotFoundError: If the file does not exist.
                        OSError: If there is an error reading the file.

                    Returns:
                        str: The content of the file.
                    '''
            }
        ]
        >>> check_if_function_is_in_function_database(
        ...     description="A function that reads a file.",
        ... )
        [
            {
                "cid": "12345",
                "name": "read_a_file_from_posix_os",
                "parameters": {
                    "name": "file_path"
                    "type": "str",
                },
                "return_type": "str",
                "docstring": '''
                    Read a file from a POSIX operating system.

                    Args:
                        file_path (str): The path to the file to be read.

                    Raises:
                        FileNotFoundError: If the file does not exist.
                        OSError: If there is an error reading the file.

                    Returns:
                        str: The content of the file.
                    '''
            }, 
            {
                "cid": "67890",
                "name": "read_a_file_from_windows_os",
                "parameters": {
                    "name": "file_path"
                    "type": "str",
                    "default": "C:\\path\\to\\file.txt"
                },
                "return_type": "str",
                "docstring": '''
                    Read a file from a Windows operating system.

                    Args:
                        file_path (str): The path to the file to be read.

                    Raises:
                        FileNotFoundError: If the file does not exist.
                        OSError: If there is an error reading the file.

                    Returns:
                        str: The content of the file.
                    '''
            }
        ]
        >>> check_if_function_is_in_function_database(
        ...     cid="12345",
        ... )
        [
            {
                "cid": "12345",
                "name": "read_a_file_from_posix_os",
                "parameters": {
                    "name": "file_path"
                    "type": "str",
                },
                "return_type": "str",
                "docstring": '''
                    Read a file from a POSIX operating system.

                    Args:
                        file_path (str): The path to the file to be read.

                    Raises:
                        FileNotFoundError: If the file does not exist.
                        OSError: If there is an error reading the file.

                    Returns:
                        str: The content of the file.
                    '''
            }
        ]
    """
    if function_name and description:
        raise ValueError("Only one of function_name, description, or cid can be provided.")
    if function_name and cid:
        raise ValueError("Only one of function_name, description, or cid can be provided.")
    if description and cid:
        raise ValueError("Only one of function_name, description, or cid can be provided.")
    if not function_name and not description and not cid:
        raise ValueError("At least one of function_name, description, or cid must be provided.")

    if function_name:
        function_list = function_database.search_by_name(function_name)
    if description:
        function_list = function_database.search_by_description(description)
    if cid:
        function_list = function_database.search_by_cid(cid)

    return function_list if function_list else []

    raise ValueError("Should not reach here. If it does, please check the logic.")
