import asyncio
import os
import shlex
import subprocess as sub
import traceback
from typing import Any, Callable


from configs import configs, Configs
from logger import mcp_logger
from utils.run_tool._return_text_content import return_text_content
from utils.run_tool._return_tool_call_results import return_tool_call_results, ResultObject


class _RunTool:

    def __init__(self, configs: Configs = None, resources: dict[str, Callable] = None) -> None:
        self.configs = configs
        self.resources = resources
        self.timeout: int = self.configs.tool_timeout or 60

        self._return_tool_call_results: Callable = self.resources['return_tool_call_results']
        self._return_text_content: Callable = self.resources['return_text_content']
        self._logger: Callable = self.resources['logger']


    def _run_func_tool(self, func: Callable, *args, **kwargs) -> ResultObject:
        """Run a function tool with the given function and arguments.
        
        This can be used to run both synchronous and asynchronous functions.
        
        Args:
            func: The function to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            The result of the function execution wrapped in a ResultObject.
        """
        try:
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
            return self.result(f"\n'{func.__qualname__}' output: {result}")
        except Exception as e:
            return self.result(e)


    def result(self, result: Any) -> ResultObject:
        """
        Format the result of a tool call.

        Args:
            result: The result of the tool call, can be an arbitrary type or an exception.

        Returns:
            A ResultObject object containing the result.
        """
        if self.configs.log_level == 10:
            self._logger(f"Tool call result: {result}")
        error = True if isinstance(result, Exception) else False
        msg = repr(result) if error else "Success"
        content = self._return_text_content(result, msg)
        return self._return_tool_call_results(content, error)


    def _run_cli_tool(self, cmd_list: list[str], func_name: str) -> ResultObject:
        """
        Run a command line tool with the given command and function name.

        Args:
            cmd_list: The command to run.
            func_name: The name of the command line tool that called this.

        Returns:
            A ResultObject object containing the result of the command.
        """
        self._logger(f"Running '{func_name}' with command: {' '.join(cmd_list)}")

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
            self._logger(traceback.print_exc())
            return self.result(e)


    def __call__(self, *args, **kwargs) -> ResultObject:
        """
        Route to the appropriate tool caller based on the given arguments and keyword arguments.
        """
        # Check if this is a CLI tool call (expected to have cmd and func_name)
        if len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], str) and not kwargs:
            if self.configs.log_level == 10:
                self._logger(f"Running CLI tool {args[1]} with command: {' '.join(args[0])}")

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
                    self._logger(f"Running function tool '{func}' with args: {args} and kwargs: {kwargs}")
                return self._run_func_tool(func, *func_args, **kwargs)


# Create singleton instance of _RunTool.
resources = {
    'return_tool_call_results': return_tool_call_results,
    'return_text_content': return_text_content,
    'logger': mcp_logger
}
_run_tool = _RunTool(configs=configs, resources=resources)


def run_tool(*args, **kwargs) -> ResultObject:
    """
    Run a tool with the given arguments and keyword arguments.

    This function can run both function tools and command line tools.

    Args:
        *args: Positional arguments to pass to the tool
        **kwargs: Keyword arguments to pass to the tool
    Returns:
        A CallToolResult object containing the result of the tool call.
    """
    # Run the tool and get the result
    return _run_tool(*args, **kwargs)
