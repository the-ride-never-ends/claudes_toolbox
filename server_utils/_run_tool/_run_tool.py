import asyncio
import importlib
import logging
import os
import shlex
import subprocess as sub
import sys
import traceback
from typing import Any, Callable


from configs import configs, Configs
from logger import mcp_logger
from server_utils._run_tool._return_text_content import return_text_content
from server_utils._run_tool._return_tool_call_results import return_tool_call_results, CallToolResultType


# Add the tools directory to the system path so we can reload tools dynamically.
sys.path.insert(0, (configs.ROOT_DIR / 'tools' / 'functions').resolve())


class _RunTool:

    def __init__(self, configs: Configs = None, resources: dict[str, Callable] = None) -> None:
        self.configs = configs
        self.resources = resources
        self.timeout: int = self.configs.tool_timeout

        self._return_tool_call_results: Callable = self.resources['return_tool_call_results']
        self._return_text_content: Callable = self.resources['return_text_content']
        self._logger: logging.Logger = self.resources['logger']

    def _reload_tool(self, func: Callable) -> None:
        """
        Reload a tool module before running it.
        This allows for dynamic updates to the tool without restarting the application.
        """
        # Reload the module to ensure we have the latest version
        module_name = func.__module__
        if module_name in sys.modules:
            self._logger.debug(f"Reloading module '{module_name}' for tool '{func.__name__}'")
            importlib.reload(sys.modules[module_name])

    def _run_func_tool(self, func: Callable, *args, **kwargs) -> CallToolResultType:
        """Run a function tool with the given function/coroutine and arguments.
        
        This method provides a unified interface for executing both synchronous and asynchronous 
        functions as tools. It handles proper async execution context management, result formatting,
        and error handling.

        Args:
            func: The function or coroutine to execute as a tool.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            CallToolResultType (BaseModel): The result of the function execution wrapped in the 
                expected result type. Contains either the function output
                or exception information if execution failed.
                Large outputs (>=20,000 chars) are truncated to 19,000 characters with ellipsis
        """
        try:
            # Reload the tool module to ensure we have the latest version
            self._reload_tool(func)
            if asyncio.iscoroutinefunction(func):
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If the event loop is already running, use asyncio.run_coroutine_threadsafe
                    future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop)
                    result = future.result()
                else:
                    # If the event loop is not running, use asyncio.run
                    result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)

            result_string = f"\n'{func.__qualname__}' output: {repr(result)}"
            mcp_logger.debug(f"Function tool '{func.__name__}' executed successfully with result: {result_string}")

            # Truncate the output string to 19,000 if it exceeds 20,000 characters
            if len(result_string) >= 20000:
                result_string = f"\nTruncated '{func.__qualname__}' output (first 19,000 characters): {result[:19000]}..."

            return self.result(result_string)

        except Exception as e:
            mcp_logger.exception(f"Exception occurred while running function tool '{func.__name__}': {e}\n{traceback.format_exc()}")
            return self.result(e)


    def result(self, result: Any) -> CallToolResultType:
        """
        Format and process the result of a tool call into a standardized CallToolResultType.

        This method handles various types of tool execution results and converts them into
        a consistent return format. It performs error detection, logging, and message
        formatting based on the result type.

        Args:
            result (Any): The result of the tool call execution. Can be:
                - A CalledProcessError for failure results from external CLI tools.
                - An Exception for general errors from function-based tools.
                - A string for successful results
                - Any other types are treated as errors.

        Returns:
            CallToolResultType: A standardized result object containing:
                - Formatted content with the result data and status message
                - Error flag indicating success (False) or failure (True)
                - Appropriate logging based on configured log level
        """
        if self.configs.log_level == 10:
            mcp_logger.debug(f"Tool call result: {result}")

        error = True # Assume error by default.
        msg = ""
        match result:
            case sub.CalledProcessError():
                msg = f"CalledProcessError: {result.returncode}\nCommand: {result.cmd}\nOutput: {result.output}\nError: {result.stderr}"
            case Exception():
                msg = f"Error: {type(result).__name__}: {str(result)}"
            case str():
                error = False
                msg = "Success"
            case _:
                # Handle any other result type
                # Defaults to error, since we shouldn't get unexpected types.
                msg = f"Unexpected Result: {type(result).__name__}"

        content = self._return_text_content(result, msg)
        return self._return_tool_call_results(content, error)


    def _run_cli_tool(self, cmd_list: list[str], func_name: str) -> CallToolResultType:
        """
        Run a command line tool with the given command and function name.

        Args:
            cmd_list: The command to run.
            func_name: The name of the command line tool that called this.

        Returns:
            A CallToolResultType object containing the result of the command.
        """
        mcp_logger.debug(f"Running '{func_name}' with command: {' '.join(cmd_list)}")

        # Activate the virtual environment and run the command
        match os.name:
            case "nt":
                # Windows
                cmd = ["cmd", "/c", ".venv\\Scripts\\activate.bat && " + shlex.join(cmd_list)]
            case "posix":
                # Linux/macOS
                cmd = ["bash", "-c", "source .venv/bin/activate && " + shlex.join(cmd_list)]
            case _:
                return self.result(OSError(f"Unsupported operating system: {os.name}"))
        try:
            result = sub.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            # Check if the command was successful and return the output
            if result.returncode == 0:
                return self.result(f"\n'{func_name}' output: {result.stdout}")
            else:
                return self.result(
                    sub.CalledProcessError(
                        returncode=result.returncode,
                        cmd=cmd,
                        output=result.stdout,
                        stderr=result.stderr,
                    ))
        except Exception as e:
            mcp_logger.exception(traceback.print_exc())
            return self.result(e)


    def __call__(self, *args, **kwargs) -> CallToolResultType:
        """
        Route to the appropriate tool caller based on the given arguments and keyword arguments.
        """
        # Check if this is a CLI tool call (expected to have cmd and func_name)
        if len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], str) and not kwargs:
            return self._run_cli_tool(args[0], args[1])
        # Otherwise, treat as a function call
        else:
            if not args:
                return self.result(ValueError("No arguments provided"))
            func = args[0]

            if not isinstance(func, Callable):
                if isinstance(func, (str, Exception)):
                    return self.result(func)
                else:   
                    return self.result(ValueError(f"First argument '{func}' is not callable, string, or exception."))
            else:
                func_args = args[1:] if len(args) > 1 else ()
                if self.configs.log_level == 10:
                    mcp_logger.debug(f"Running function tool '{func}' with args: {args} and kwargs: {kwargs}")
                return self._run_func_tool(func, *func_args, **kwargs)


# Create singleton instance of _RunTool.
resources = {
    'return_tool_call_results': return_tool_call_results,
    'return_text_content': return_text_content,
    'logger': mcp_logger
}
_run_tool = _RunTool(configs=configs, resources=resources)


def run_tool(*args, **kwargs) -> CallToolResultType:
    """
    Run a tool with the given arguments and keyword arguments.

    This function can run both function tools and command line tools.

    Args:
        *args: Positional arguments to pass to the tool
        **kwargs: Keyword arguments to pass to the tool

    Returns:
        A CallToolResult object containing the result of the tool call.
    """
    return _run_tool(*args, **kwargs)

def return_results(input: Any) -> CallToolResultType:
    """
    Return the result of a tool call.

    Args:
        input: The result of the tool call, can be an arbitrary type or an exception.

    Returns:
        A CallToolResultType object containing the result.
    """
    return _run_tool.result(input)
