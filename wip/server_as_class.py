# class ClaudesToolboxServer:
#     """
#     Organizing class for the MCP server and its CLI tools.
#     """

#     def __init__(self, 
#                 configs: Configs = None, 
#                 resources: dict[str, Callable] = None
#                 ) -> None:
#         self.configs = configs
#         self.resources = resources

#         self.tools: list[dict[str, Any]] = self.configs["tools"]

#         self.__run_tool: Callable = self.resources["run_tool"]
#         self.__install_tool_dependencies_to_shared_venv: Callable = self.resources["install_tool_dependencies_to_shared_venv"]
#         self.__turn_argparse_help_into_docstring: Callable = self.resources["turn_argparse_help_into_docstring"]

#         self.server = self.resources["server"]

#         self.setup()

#     def setup(self) -> None:
#         """Setup the server and tools, and install dependencies."""
#         assert hasattr(self.server, "add_tool"), "Server does not have 'add_tool' method"
#         assert hasattr(self.server, "run"), "Server does not have 'run' method"
#         if not self.tools:
#             raise ValueError("No tools found. Please check the tool paths.")
#         self._validate_tool_paths()
#         self._install_tool_dependencies_to_shared_venv()

#     def _validate_tool_paths(self) -> None:
#         """
#         Validate the tool paths.
#         """
#         for tool in self.tools:
#             if not Path(tool["path"]).exists():
#                 raise FileNotFoundError(f"Tool '{tool['name']}' not found at {tool['path']}.")

#     def _install_tool_dependencies_to_shared_venv(self) -> None:
#         """
#         Install tool dependencies to the server's shared virtual environment.
#         """
#         requirements_file_paths = []
#         for tool in self.tool_paths:
#             requirements_file_path = Path(tool["path"]).parent / "requirements.txt"
#             if requirements_file_path.exists():
#                 requirements_file_paths.append(requirements_file_path)
#         self.__install_tool_dependencies_to_shared_venv(requirements_file_paths)

#     def _sanitize_tool_inputs(self, *args, **kwargs) -> None:
#         """
#         Sanitize CLI tool inputs to prevent various injection attacks.
        
#         Args:
#             args: Positional arguments.
#             kwargs: Keyword arguments.

#         Raises:
#             ValueError: If any of the inputs are invalid.
#         """ 
#         pass

#     def _turn_argparse_help_into_docstring(self, help_message: str) -> str:
#         """
#         Converts command-line argument documentation to Google-style docstring.

#         Args:
#             help_message (str): The help message from argparse.
#         """
#         self.__turn_argparse_help_into_docstring(help_message)


#     def _run_tool(self, cmd: list[str], tool_name: str) -> str:
#         self.__run_tool(cmd, tool_name)


#     def load_tools(self) -> dict[str, Any]:
#         """
#         Get the attributes of a tool.
#         """
#         _tools = []
#         for tool in self.tools:
#             tool_name = tool["name"]
#             tool_path: Path = Path(tool["path"])

#             # Get its description by running the tool with --help
#             # This will also check if the tool can be found and run
#             cmd = ["python ", tool_path, "--help"]
#             help_message = self._run_tool(cmd, tool_name)
#             if not help_message:
#                 self._mcp_print(f"'{tool_name}' did not return a help message. Skipping.")
#                 continue
#             # Convert the help message to a docstring
#             #description = self._turn_argparse_help_into_docstring(help_message)
#         raise FileNotFoundError(f"Could not find any tools.")


#     def register_tools(self) -> None:
#         """
#         Register tools with the server.
#         """
#         for tool in self.tools:
#             func = tool.pop("func")
#             self.server.add_tool(func, **tool)

#     def run(self) -> None:
#         """
#         Run the server.
#         """
#         self.server.run(transport="stdio")