from __future__ import annotations
from pathlib import Path
from typing import Any, Callable


from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult


from configs import Configs
from server_utils._run_tool import run_tool


class CliTools:
    """
    A class to organize CLI tools.
    """ 
    _THIS_FILE = Path(__file__)
    _THIS_DIR = _THIS_FILE.parent
    _CLAUDES_TOOLBOX_DIR = _THIS_DIR.parent.parent
    _PATHS_DICT = {
        "_THIS_FILE": _THIS_FILE,
        "this_dir": _THIS_DIR,
        "project_dir": _THIS_DIR.parent,
        "venv_dir": _THIS_DIR / ".venv",
        "server_dir": _THIS_DIR,
        "tools_dir": _THIS_DIR / "tools",
    }
    _SUPPORTED_CLI_TOOLS = {
        "Test Generator": "test_generator",
        "Documentation Generator": "documentation_generator",
        "Lint a Python Codebase": "lint_a_python_codebase",
        "Run Tests and Save Their Results": "run_tests_and_save_their_results",
        "Codebase Search": "codebase_search",
    }
    _REQUIRED_FILES = ["__version__.py", "__main__.py", "__init__.py"]

    def __init__(self, 
                 configs: Configs = None, 
                 resources: dict[str, Callable] = None
                 ) -> None:
        self.configs = configs
        self._resources = resources
        self._cli_tool_paths: list[Path] = None

        self._run_tool: Callable = resources["run_tool"]
        self._return_results: Callable = resources["return_results"]
        self._total_tools: Callable = resources["total_tools"]
        self._logger: Callable = resources["logger"]

        self._cli_tool_paths = self._get_finished_cli_tool_paths()
        self._verify_cli_paths()

    def _get_finished_cli_tool_paths(self) -> list[Path]:
        supported_tools = []
        for dir in self.configs.search_dir.iterdir():
            # Skip if not a directory or if the path contains "venv" or "tests"
            if not dir.is_dir() or "venv" in dir.name or dir.name == "tests":
                continue

            # Find all directories with the required files
            if all((dir / file).exists() for file in self._REQUIRED_FILES):
                try:
                    version_file = dir / "__version__.py"
                    with open(version_file, "r") as f:
                        version_content = f.read()
                        # Extract the version number from the file.
                        version = version_content.split("=")[1].strip().strip("'\"")

                    if version.startswith("1"):
                        supported_tools.append(
                            {"dir": dir, 
                            "path": dir.resolve()}
                        )
                except (IOError, IndexError):
                    continue
        return supported_tools

    def register_cli_tools(self, mcp: FastMCP) -> None:
        """Register the tools with the server."""
        for idx, method in enumerate(dir(self), start=1):
            func = getattr(self, method)
            if isinstance(func, Callable) and not method.startswith("_"):
                try:
                    mcp.add_tool(
                        func, 
                        name=method, 
                        description=func.__doc__
                    )
                    # Increment the tool count
                    self._total_tools()
                except Exception as e:
                    self._logger.exception(f"Error registering tool '{method}': {e}")
                    continue

    def _verify_cli_paths(self) -> None:
        """ 
        Verify that the CLI paths are correct.
        """
        _verified_tools = []
        for tool in self._cli_tool_paths:
            if not tool['path'].exists():
                self._logger.warning(f"Path '{tool}' does not exist")
                continue
            else:
                _verified_tools.append(tool)
        if _verified_tools is None:
            raise FileNotFoundError(f"Could not find any tools.")
        self._cli_tool_paths = _verified_tools

    def _add_parameters(self, cmd: list[str], **kwargs) -> list[str]:
        """
        Add parameters to the command.
        NOTE Because positional arguments are assigned a value when passed to the calling function,
        we can treat them as keyword arguments as long as we call them first.
        """
        for key, value in kwargs.items():
            # Replace underscores with dashes for command line arguments
            key = key.replace("_", "-")
            if value is not None:
                cmd.append(f"--{key}")
                match value:
                    case list():
                        for item in value:
                            cmd.extend(item)
                    case bool():
                        if value is False: 
                            cmd.pop() # Since we are using a CLI, we remove the flag to set it to False
                    case int() | float():
                        cmd.append(str(value))
                    case _:
                        cmd.append(value)
        return cmd

    def _build_cli_command(self, tool_name: str, *args, **kwargs) -> list[str]:
        """
        Build the command for the CLI tool.
        """
        cmd = [tool_name]
        cmd = self._add_parameters(cmd, **kwargs)
        # Add positional arguments
        for arg in args:
            cmd.append(arg)
        # Add keyword arguments
        cmd = self._add_parameters(cmd, **kwargs)
        return cmd


    def _get_tool_path(self, tool_name: str) -> Path:
        for tool in self._cli_tool_paths:
            if tool["dir"].name == tool_name:
                return tool["path"]

    def test_generator(self,
                    name: str, 
                    description: str, 
                    test_parameter_json: str, 
                    output_dir: str = "tests", 
                    harness: str = "unittest"
                    ) -> CallToolResult:
        """Generate test files based on JSON input.
        
        Args:
            name: Test name.
            description: A short description of the test.
            test_parameter_json: The file path to the test parameters JSON file.
            output_dir: Path to output directory for tests. Defaults to "tests".
            harness: Which python testing harness to use. Defaults to "unittest".
        
        Returns:
            str: Command output from the test generator.
            
        Note:
            Additional options available in CLI but not exposed here:
            - has-fixtures: Whether a test needs fixtures
            - parametrized: Whether to generate parametrized tests
            - debug: Enable debug mode with enhanced output
            - test-params: JSON string of parameters for conditional test generation
            - docstring-style: Docstring style to parse
        """
        
        tool_path = self._get_tool_path('test_generator')
        assert tool_path, f"Tool 'test_generator' not found."
        cmd = [
            "python", "-m", f"{tool_path}",
            "--name", f"{name}",
            "--description", f"{description}",
            "--test_parameter_json", f"{test_parameter_json}", 
            "--output_dir", f"{output_dir}",
            "--harness", f"{harness}"
        ]
        return self._run_tool(cmd, "Test Generator")

    def documentation_generator(self,
                                input: str, 
                                output: str = "docs", 
                                docstring_style: str = "google", 
                                ignore: list[str] = None, 
                                inheritance: bool = True,
                                ) -> CallToolResult:
        """Generate documentation from Python source code.
        
        Args:
            input: Path to Python file or directory to generate documentation from.
            output: Path to output directory for documentation. Defaults to "docs".
            docstring_style: Docstring style to parse (google, numpy, or rest). Defaults to "google".
            ignore: Paths to ignore when generating documentation. Defaults to None.
            inheritance: Enable enhanced inheritance documentation with class hierarchies. Defaults to True.
        
        Returns:
            str: Command output from the documentation generator.
        
        Note:
            This tool is in Alpha status, not all features are fully debugged.
            Additional options available in CLI but not exposed here:
            - format: Output format for documentation (currently only markdown)
            - verbose: Enable verbose output
            - ignore-file: Path to file containing paths to ignore
            - save-ignore: Save ignore paths to ignore file
            - self-doc: Enable self-documentation mode
        """
        cmd = [
            "python", "-m", f"{self._get_tool_path('documentation_generator')}",
            "--input", f"{input}",
            "--output", f"{output}",
            "--docstring-style", f"{docstring_style}"
        ]

        # Add optional parameters if they're provided
        if ignore:
            cmd.append("--ignore")
            for path in ignore:
                cmd.append(path)

        if inheritance:
            cmd.append("--inheritance")

        return self._run_tool(cmd, "Documentation Generator")


    def lint_a_python_codebase(self,
                            path: str = ".", 
                            patterns: list[str] = None, 
                            exclude: list[str] = None, 
                            no_blank: bool = False,
                            no_trailing: bool = False,
                            no_newlines: bool = False,
                            dry_run: bool = False, 
                            verbose: bool = False) -> CallToolResult:
        """Fix common linting issues in Python codebases.
        
        Args:
            path: Target directory to process. Defaults to current directory.
            patterns: File patterns to match. Defaults to None, which uses '**/*.py'.
            exclude: Directories to exclude. Defaults to None, which uses ['.venv', '.git', '__pycache__'].
            no_blank: Don't fix blank lines with whitespace. Defaults to False.
            no_trailing: Don't fix trailing whitespace. Defaults to False.
            no_newlines: Don't ensure files end with a newline. Defaults to False.
            dry_run: Don't make any changes, just show what would be done. Defaults to False.
            verbose: Print detailed information for each file. Defaults to False.
        
        Returns:
            str: Command output from the linting tool.
        """
        cmd = ["python", "-m", "main.py", path]

        # Add optional parameters
        if patterns:
            cmd.append("--patterns")
            for pattern in patterns:
                cmd.extend(pattern)

        if exclude:
            cmd.append("--exclude")
            for dir in exclude:
                cmd.extend(dir)

        if no_blank:
            cmd.append("--no-blank")
        if no_trailing:
            cmd.append("--no-trailing")
        if no_newlines:
            cmd.append("--no-newlines")
        if dry_run:
            cmd.append("--dry-run")
        if verbose:
            cmd.append("--verbose")

        return run_tool(cmd, "Lint Python Codebase")

    def run_tests_and_save_their_results(self,
                                        path: str = ".", 
                                        check_all: bool = False, 
                                        mypy: bool = False, 
                                        flake8: bool = False, 
                                        lint_only: bool = False, 
                                        respect_gitignore: bool = False) -> CallToolResult:
        """Run unit tests, type checking, and linting for a specified Python project.
        
        Args:
            path: Path to the project directory. Defaults to current directory.
            check_all: Run tests, type checking, linting, and corner cutting checks. Defaults to False.
            mypy: Run mypy type checking. Defaults to False.
            flake8: Run flake8 linting. Defaults to False.
            lint_only: Run only type checking and linting (no tests). Defaults to False.
            respect_gitignore: Ignore files/folders listed in .gitignore during linting. Defaults to False.
        
        Returns:
            str: Command output containing test and linting results.
        
        Note:
            This tool is in Alpha status, not all features are fully debugged.
            Additional options available in CLI but not exposed here:
            - quiet: Run tests with reduced verbosity
            - corner-cutting: Run corner cutting checks (identifies implementation shortcuts)
        """
        cmd = ["./run_tests.sh", "--path", path]

        # Add optional flags
        if check_all:
            cmd.append("--check-all")

        if mypy:
            cmd.append("--mypy")

        if flake8:
            cmd.append("--flake8")

        if lint_only:
            cmd.append("--lint-only")

        if respect_gitignore:
            cmd.append("--respect-gitignore")

        stdout = run_tool(cmd, "Run Tests and Save Results")
        return stdout

    def codebase_search(self,
                    pattern: str, 
                    path: str = ".", 
                    case_insensitive: bool = False, 
                    whole_word: bool = False, 
                    regex: bool = False, 
                    extensions: str = None, 
                    exclude: str = None,
                    max_depth: int = None,
                    context: int = 0, 
                    format: str = "text",
                    output: str = None,
                    compact: bool = False,
                    group_by_file: bool = False,
                    summary: bool = False) -> CallToolResult:
        """Search codebase for patterns with structured output.\n

        Args:\n
            pattern: The pattern to search for.
            path: The path to search in. Defaults to current directory.
            case_insensitive: Perform case-insensitive search. Defaults to False.
            whole_word: Match whole words only. Defaults to False.
            regex: Interpret pattern as a regular expression. Defaults to False.
            extensions: Comma-separated list of file extensions to search (e.g., 'py,txt'). Defaults to None.
            exclude: Comma-separated list of glob patterns to exclude (e.g., '*.git*,*node_modules*'). Defaults to None.
            max_depth: Maximum directory depth to search. Defaults to None.
            context: Number of lines of context to include before and after matches. Defaults to 0.
            format: Output format (text or json). Defaults to "text".
            output: Write output to file instead of stdout. Defaults to None.
            compact: Use compact output format (one line per match). Defaults to False.
            group_by_file: Group results by file. Defaults to False.
            summary: Include summary information in output. Defaults to False.
        
        Returns:
            str: Command output containing search results.
        """
        cmd = ["python", "-m", "codebase_search", pattern, path]

        # Add optional parameters
        if case_insensitive:
            cmd.append("--case-insensitive")
        
        if whole_word:
            cmd.append("--whole-word")
        
        if regex:
            cmd.append("--regex")
        
        if extensions:
            cmd.extend(["--extensions", extensions])
        
        if exclude:
            cmd.extend(["--exclude", exclude])
        
        if max_depth is not None:
            cmd.extend(["--max-depth", str(max_depth)])
        
        if context > 0:
            cmd.extend(["--context", str(context)])
        
        if format != "text":
            cmd.extend(["--format", format])
        
        if output:
            cmd.extend(["--output", output])
        
        if compact:
            cmd.append("--compact")
        
        if group_by_file:
            cmd.append("--group-by-file")
        
        if summary:
            cmd.append("--summary")
        
        stdout = run_tool(cmd, "Codebase Search")
        return stdout