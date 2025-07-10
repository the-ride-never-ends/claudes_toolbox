#!/usr/bin/env python3
"""
MCP Protocol Debug Analysis
Focus on message framing and protocol-level issues rather than JSON content.
"""

import json
import logging
from typing import Any, Dict

def analyze_mcp_message_framing():
    """Analyze potential MCP message framing issues."""
    print("=== MCP Message Framing Analysis ===")
    
    # The error "position 4 (line 1 column 5)" suggests issues with message headers
    # MCP uses JSON-RPC 2.0 over stdio/sockets
    
    problematic_patterns = [
        {
            "name": "Missing Content-Length header",
            "description": "MCP requires proper Content-Length headers for message framing",
            "example_bad": '{"jsonrpc": "2.0", "result": {...}}',
            "example_good": 'Content-Length: 45\r\n\r\n{"jsonrpc": "2.0", "result": {...}}'
        },
        {
            "name": "Malformed JSON-RPC response",
            "description": "Missing required JSON-RPC fields",
            "example_bad": '{"result": "data"}',
            "example_good": '{"jsonrpc": "2.0", "id": 1, "result": "data"}'
        },
        {
            "name": "Mixed response types",
            "description": "Sometimes returning JSON, sometimes plain strings",
            "example_bad": "Error: Invalid database ID",
            "example_good": '{"jsonrpc": "2.0", "id": 1, "error": {"code": -1, "message": "Invalid database ID"}}'
        },
        {
            "name": "Unicode/encoding issues",
            "description": "Improper UTF-8 encoding in message stream",
            "example_bad": "Content with unusual chars: \x00\x01",
            "example_good": "Properly encoded UTF-8 content"
        }
    ]
    
    for pattern in problematic_patterns:
        print(f"\n🔍 {pattern['name']}")
        print(f"   Issue: {pattern['description']}")
        print(f"   Bad:  {pattern['example_bad'][:50]}...")
        print(f"   Good: {pattern['example_good'][:50]}...")

def check_fastmcp_response_format():
    """Check if FastMCP is properly formatting responses."""
    print("\n=== FastMCP Response Format Check ===")
    
    # Your tools return strings, but MCP expects JSON-RPC wrapped responses
    sample_tool_returns = [
        "Simple string return",
        '{"status": "success", "data": "json"}',
        "Error: Database not found",
        json.dumps({"large": "data" * 1000})
    ]
    
    print("Analyzing tool return formats:")
    for i, return_val in enumerate(sample_tool_returns, 1):
        print(f"\nReturn {i}: {return_val[:50]}...")
        
        # Check if it's valid JSON
        try:
            if return_val.startswith('{') or return_val.startswith('['):
                parsed = json.loads(return_val)
                print(f"  ✅ Valid JSON: {type(parsed)}")
            else:
                print(f"  ⚠️  Plain string (may need JSON-RPC wrapping)")
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            
        # Check length
        if len(return_val) > 10000:
            print(f"  ⚠️  Large response ({len(return_val):,} bytes)")

def identify_mcp_specific_issues():
    """Identify issues specific to MCP protocol implementation."""
    print("\n=== MCP-Specific Issues ===")
    
    issues = [
        {
            "issue": "Tool function returns not wrapped in JSON-RPC",
            "location": "FastMCP framework handling",
            "solution": "Ensure FastMCP properly wraps tool responses in JSON-RPC format",
            "debug_step": "Check if @mcp.tool() decorator handles response wrapping"
        },
        {
            "issue": "Streaming response chunks malformed",
            "location": "Message transport layer", 
            "solution": "Verify message framing with proper Content-Length headers",
            "debug_step": "Log raw bytes being sent over the connection"
        },
        {
            "issue": "Concurrent request handling corruption",
            "location": "Server request processing",
            "solution": "Ensure thread-safe response handling",
            "debug_step": "Test with single sequential requests"
        },
        {
            "issue": "Exception during response serialization",
            "location": "Tool execution or response formatting",
            "solution": "Wrap all tool functions in try/catch with proper error responses",
            "debug_step": "Add logging to catch exceptions before they reach MCP layer"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['issue']}")
        print(f"   Location: {issue['location']}")
        print(f"   Solution: {issue['solution']}")
        print(f"   Debug: {issue['debug_step']}")

def create_debug_wrapper():
    """Create a debug wrapper for MCP tool functions."""
    print("\n=== Debug Wrapper Code ===")
    
    wrapper_code = '''
import json
import logging
import traceback
from functools import wraps

logger = logging.getLogger(__name__)

def mcp_debug_wrapper(func):
    """Wrapper to debug MCP tool function responses."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            
            # Call the original function
            result = func(*args, **kwargs)
            
            # Log the raw result
            logger.debug(f"{func.__name__} returned: {type(result)} - {str(result)[:200]}...")
            
            # Validate the result can be JSON serialized
            if isinstance(result, str):
                try:
                    # Try to parse as JSON to validate
                    if result.strip().startswith(('{', '[')):
                        json.loads(result)
                        logger.debug(f"{func.__name__} returned valid JSON string")
                    else:
                        logger.debug(f"{func.__name__} returned plain string")
                except json.JSONDecodeError as e:
                    logger.error(f"{func.__name__} returned invalid JSON: {e}")
                    # Return a properly formatted error response
                    return json.dumps({
                        "status": "error", 
                        "message": f"Invalid JSON response from {func.__name__}",
                        "original_error": str(e)
                    })
            
            # Check response size
            result_size = len(str(result))
            if result_size > 100000:  # 100KB
                logger.warning(f"{func.__name__} returned large response: {result_size:,} bytes")
            
            return result
            
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return a properly formatted error response
            return json.dumps({
                "status": "error",
                "message": f"Exception in {func.__name__}: {str(e)}",
                "error_type": type(e).__name__
            })
    
    return wrapper

# Usage: Apply to all your MCP tool functions
# @mcp.tool()
# @mcp_debug_wrapper
# def your_tool_function(...):
#     ...
'''
    
    print(wrapper_code)

def suggest_immediate_debugging_steps():
    """Suggest immediate steps to debug the MCP issue."""
    print("\n" + "="*60)
    print("🚨 IMMEDIATE DEBUGGING STEPS")
    print("="*60)
    
    steps = [
        {
            "step": 1,
            "action": "Enable detailed MCP logging",
            "command": "Add logging.basicConfig(level=logging.DEBUG) to your server",
            "purpose": "See exact messages being sent/received"
        },
        {
            "step": 2, 
            "action": "Test with minimal tool",
            "command": "Create a simple tool that returns just 'hello world'",
            "purpose": "Isolate if issue is in specific tools or all tools"
        },
        {
            "step": 3,
            "action": "Check FastMCP version compatibility", 
            "command": "pip show fastmcp; check GitHub for known issues",
            "purpose": "Ensure you're using a stable version"
        },
        {
            "step": 4,
            "action": "Add response validation",
            "command": "Use the debug wrapper provided above",
            "purpose": "Catch and fix malformed responses before they reach MCP"
        },
        {
            "step": 5,
            "action": "Test with sequential requests only",
            "command": "Avoid rapid/concurrent tool calls initially",
            "purpose": "Rule out concurrency issues"
        }
    ]
    
    for step_info in steps:
        print(f"\n{step_info['step']}. {step_info['action']}")
        print(f"   Command: {step_info['command']}")
        print(f"   Purpose: {step_info['purpose']}")
    
    print(f"\n{'='*60}")
    print("💡 KEY INSIGHT FROM YOUR DEBUG OUTPUT:")
    print("Since JSON serialization works fine, the issue is likely in:")
    print("  - MCP message framing (Content-Length headers)")
    print("  - FastMCP response wrapping") 
    print("  - Exception handling during tool execution")
    print("  - Concurrent request handling")

if __name__ == "__main__":
    print("🔍 MCP Protocol-Level Debug Analysis")
    print("="*60)
    
    analyze_mcp_message_framing()
    check_fastmcp_response_format()
    identify_mcp_specific_issues()
    create_debug_wrapper()
    suggest_immediate_debugging_steps()