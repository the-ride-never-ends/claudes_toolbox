import sys
from typing import Any


def mcp_print(input: Any) -> None:
    """
    Prints the input to the console.
    This is needed because print() won't log to an MCP debug file.

    Args:
        input: The input to print.
    """
    print(input, file=sys.stderr)
