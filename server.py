#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An MCP server for serving CLI programs and utility functions to LLMs.
"""
from __future__ import annotations
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise ImportError("mcp is not installed. Please install it with `pip install mcp`.")

from configs import configs
from logger import mcp_logger
from server_utils.install_tool_dependencies_to_shared_venv import install_tool_dependencies_to_shared_venv
from server_utils.server_.get_functions_tools_from_files import get_function_tools_from_files


class TotalTools:
    MAX_TOOL_COUNT = 129

    def __init__(self):
        self.count = 0

    def __call__(self):
        if self.count >= self.MAX_TOOL_COUNT:
            raise ValueError(f"Maximum MCP tool count of {self.MAX_TOOL_COUNT} reached.")
        self.count += 1
        return self.count


total_tools = TotalTools()


def main():
    mcp_logger.info("Starting Claude's Toolbox MCP server...")

    # Initialize FastMCP server
    mcp = FastMCP("claudes_toolbox")

    mcp_logger.info("API instantiated. Installing shared venv requirements...")

    # Load dependencies
    install_tool_dependencies_to_shared_venv(configs.REQUIREMENTS_FILE_PATHS)

    mcp_logger.info("Shared venv requirements installed.")
    mcp_logger.info("Registering MCP tools from tools/functions directory...")

    # Register function tools from files with the server
    mcp = get_function_tools_from_files(mcp)

    mcp_logger.info("Function tools registered.")

    # Register standalone CLI tools with the server
    # cli_tools = CliTools(configs, resources={
    #     "run_tool": run_tool,
    #     "return_results": return_results,
    #     "total_tools": TotalTools(),
    #     "logger": mcp_logger,
    # })
    # cli_tools.register_cli_tools(mcp)

    #mcp = register_database_tools(mcp)

    mcp_logger.info("Claude's Toolbox MCP server started")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    keyboard_interrupt = False
    try:
        main()
    except KeyboardInterrupt:
        keyboard_interrupt = True
        mcp_logger.info("Server stopped by user.")
    except Exception as e:
        mcp_logger.exception(f"An error occurred while running the server: {e}")
    finally:
        import time
        if not keyboard_interrupt:
            mcp_logger.info("Server stopped.")
        # Wait a moment for any daemons/threads to join.
        time.sleep(1)
        sys.exit(0)
