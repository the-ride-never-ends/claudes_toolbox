# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a template for a webapp that uses main.py.
"""
from __future__ import annotations


import argparse
import asyncio
import os
import sys

import mcp.server


# from fastapi import FastAPI
# import uvicorn
# import yaml


from configs import configs
from logger import logger
from utils.install_tool_dependencies_to_shared_venv import install_tool_dependencies_to_shared_venv

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

import subprocess
from subprocess import CalledProcessError
from typing import Any

# Initialize FastMCP server
mcp = FastMCP("claudes_toolbox")


from .utils.mcp_print import mcp_print
from .utils.run_cli_tool import run_cli_tool


@mcp.tool()
def write_file_in_linux(file_path: str, content: str) -> None:
    """
    Write content to a file in Linux. 
    This is a test to see if Claude can use a server tool served from WSL.

    Args:
        file_path: Path of the file to write.
        content: Content to write to the file.
    """
    logger.info("TESTING WRITE FILE IN LINUX")
    mcp_print(f"Writing to content to {file_path}")
    if "\\" in file_path:
        # Convert Windows-style path to Linux-style path
        file_path = file_path.replace("\\", "/")
        mcp_print(f"Changed windows file path to Linux. Path is now '{file_path}'")

    # Get the home directory so that Claude doesn't write to the root directory
    if os.name != "nt":
        if "~" not in file_path:
            home_dir = os.path.expanduser("~")
            file_path = os.path.join(home_dir, file_path)
            mcp_print(f"Original path was outside home directory. Path is now '{file_path}'")

    try:
        with open(file_path, "w", newline="\n") as file:
            file.write(content)
        mcp_print(f"File written to {file_path}")
    except Exception as e:
        mcp_print(f"Error writing to file: {e}")


@mcp.tool()
def test_generator(name: str, 
                   description: str, 
                   test_parameter_json: str, 
                   output_dir: str = "tests", 
                   harness: str = "unittest"
                ):
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
    # Execute test generator command with appropriate arguments
    cmd = [
        "python", "-m", "test_generator",
        "--name", f"{name}",
        "--description", f"{description}",
        "--test_parameter_json", f"{test_parameter_json}", 
        "--output_dir", f"{output_dir}",
        "--harness", f"{harness}"
    ]

    stdout = run_cli_tool(cmd, "Test Generator")
    return stdout


@mcp.tool()
def documentation_generator(input_path: str, 
                            output_path: str = "docs", 
                            docstring_style: str = "google", 
                            ignore: list[str] = None, 
                            inheritance: bool = True,
                            ):
    """Generate documentation from Python source code.
    
    Args:
        input_path: Path to Python file or directory to generate documentation from.
        output_path: Path to output directory for documentation. Defaults to "docs".
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
        "python", "documentation_generator.py",
        "--input", f"{input_path}",
        "--output", f"{output_path}",
        "--docstring-style", f"{docstring_style}"
    ]

    # Add optional parameters if they're provided
    if ignore:
        cmd.append("--ignore")
        for path in ignore:
            cmd.append(path)

    if inheritance:
        cmd.append("--inheritance")

    stdout = run_cli_tool(cmd, "Documentation Generator")
    return stdout


@mcp.tool()
def lint_a_python_codebase(path: str = ".", 
                          patterns: list[str] = None, 
                          exclude: list[str] = None, 
                          no_blank: bool = False,
                          no_trailing: bool = False,
                          no_newlines: bool = False,
                          dry_run: bool = False, 
                          verbose: bool = False):
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
    cmd = ["python", "main.py", path]

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

    stdout = run_cli_tool(cmd, "Lint Python Codebase")
    return stdout


@mcp.tool()
def run_tests_and_save_their_results(path: str = ".", 
                                     check_all: bool = False, 
                                     mypy: bool = False, 
                                     flake8: bool = False, 
                                     lint_only: bool = False, 
                                     respect_gitignore: bool = False) -> str:
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

    stdout = run_cli_tool(cmd, "Run Tests and Save Results")
    return stdout


@mcp.tool()
def codebase_search(pattern: str, 
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
                   summary: bool = False) -> str:
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
    
    stdout = run_cli_tool(cmd, "Codebase Search")
    return stdout



if __name__ == "__main__":
    install_tool_dependencies_to_shared_venv(configs.REQUIREMENTS_FILE_PATHS)
    keyboard_interrupt = False
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        keyboard_interrupt = True
        mcp_print("Server stopped by user.")
    finally:
        if not keyboard_interrupt:
            mcp_print("Server stopped.")
        sys.exit(0)
