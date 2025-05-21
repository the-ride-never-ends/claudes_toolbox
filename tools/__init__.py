"""
Tools for the MCP server.
NOTE: All imports in tools are lazy loaded to avoid import errors with third-party libraries.
This means that if a tool's imports fail, it won't stop the server from starting.
This is important with tools that rely on large libraries like PyTorch, TensorFlow, etc.

The lazy loading pattern allows the server to start even if some tool dependencies
are not installed, making the system more robust to partial installations and
configuration issues. Each tool should be implemented in a way that its dependencies
are only imported when the tool is actually used.
"""