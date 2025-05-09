"""
claudes_toolbox:
Serves utility programs from Claude's Toolbox using the Model Context Protocol (MCP).
Allows agentic LLMs to use the programs regardless of their API interface (e.g. Claude Code, Claude Desktop, etc.).
"""
from .configs import configs
from .logger import logger

__all__ = [
    "configs",
    "logger",
]