#!/usr/bin/env python3
"""
Debug script to identify JSON parsing issues in MCP database tools.
"""

import json
import logging
from typing import Any, Dict

def test_json_serialization(data: Any, context: str = ""):
    """Test if data can be properly serialized to JSON."""
    try:
        json_str = json.dumps(data, indent=2)
        # Try to parse it back
        parsed = json.loads(json_str)
        print(f"✅ {context}: JSON serialization successful")
        return True, json_str
    except Exception as e:
        print(f"❌ {context}: JSON serialization failed - {e}")
        return False, str(e)

def test_sql_escaping_scenarios():
    """Test various content scenarios that might break SQL."""
    
    test_cases = [
        ("Simple text", "Hello world"),
        ("Single quotes", "It's a test"),
        ("Multiple quotes", "It's 'really' a test"),
        ("Newlines", "Line 1\nLine 2\nLine 3"),
        ("Mixed quotes and newlines", "It's a test\nwith 'quotes'\nand newlines"),
        ("Backslashes", "Path\\to\\file"),
        ("JSON content", '{"key": "value", "nested": {"inner": "data"}}'),
        ("SQL injection attempt", "'; DROP TABLE test; --"),
        ("Unicode", "Hello 世界 🌍"),
        ("Large content", "x" * 10000),
    ]
    
    print("=== SQL Escaping Test Cases ===")
    for name, content in test_cases:
        print(f"\nTesting: {name}")
        
        # Test basic escaping (current method)
        basic_escaped = content.replace("'", "''")
        print(f"Basic escaped length: {len(basic_escaped)}")
        
        # Test if it would break JSON
        test_response = {
            "content": content,
            "escaped_content": basic_escaped,
            "length": len(content)
        }
        
        success, result = test_json_serialization(test_response, f"Response for {name}")
        
        if not success:
            print(f"  🔍 Issue details: {result}")

def test_large_response_scenarios():
    """Test scenarios with large responses that might break MCP."""
    
    print("\n=== Large Response Test Cases ===")
    
    # Simulate large markdown file responses
    large_content = "# Large Markdown File\n" + ("This is a test line.\n" * 1000)
    
    responses_to_test = [
        {
            "name": "Large markdown content",
            "data": {
                "file_path": "large_file.md",
                "content": large_content,
                "file_size": len(large_content)
            }
        },
        {
            "name": "Many small files",
            "data": {
                "files": [{"file": f"file_{i}.md", "content": f"Content {i}"} for i in range(1000)]
            }
        },
        {
            "name": "Deep nested structure",
            "data": {"level1": {"level2": {"level3": {"level4": {"data": "deep"}}}}}
        }
    ]
    
    for test_case in responses_to_test:
        print(f"\nTesting: {test_case['name']}")
        success, result = test_json_serialization(test_case['data'], test_case['name'])
        
        if success:
            json_size = len(result)
            print(f"  📏 JSON size: {json_size:,} bytes")
            if json_size > 100000:  # 100KB
                print(f"  ⚠️  Large response detected ({json_size:,} bytes)")

def test_error_response_consistency():
    """Test that error responses are consistently formatted."""
    
    print("\n=== Error Response Consistency ===")
    
    # Test different error response patterns found in the code
    error_patterns = [
        ("Direct string", "Error: Invalid database ID"),
        ("JSON error", {"error": "Invalid database ID", "status": "error"}),
        ("Mixed response", {"status": "partial_success", "errors": ["Error 1", "Error 2"]}),
    ]
    
    for name, response in error_patterns:
        print(f"\nTesting error pattern: {name}")
        
        if isinstance(response, str):
            # String responses might not be valid JSON
            print(f"  📝 String response: {response}")
            # Test if wrapping in JSON would work
            wrapped = {"message": response}
            test_json_serialization(wrapped, f"Wrapped {name}")
        else:
            test_json_serialization(response, name)

def identify_potential_fixes():
    """Suggest potential fixes for the identified issues."""
    
    print("\n" + "="*50)
    print("🔧 POTENTIAL FIXES")
    print("="*50)
    
    fixes = [
        {
            "issue": "SQL Injection & Escaping",
            "solution": "Use parameterized queries instead of string formatting",
            "example": "Use db.execute('SELECT * FROM table WHERE id = ?', [user_id])"
        },
        {
            "issue": "Large JSON Responses", 
            "solution": "Implement response size limits and pagination",
            "example": "Limit content to first N characters, provide separate endpoint for full content"
        },
        {
            "issue": "Inconsistent Error Responses",
            "solution": "Standardize all responses to return JSON",
            "example": "Always return {'status': 'error', 'message': 'description'}"
        },
        {
            "issue": "Content Encoding",
            "solution": "Properly encode content for JSON transmission",
            "example": "Use base64 encoding for binary content, escape special characters"
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"\n{i}. {fix['issue']}")
        print(f"   Solution: {fix['solution']}")
        print(f"   Example: {fix['example']}")

if __name__ == "__main__":
    print("🔍 MCP JSON Debug Analysis")
    print("="*50)
    
    test_sql_escaping_scenarios()
    test_large_response_scenarios() 
    test_error_response_consistency()
    identify_potential_fixes()
    
    print(f"\n{'='*50}")
    print("✅ Debug analysis complete!")
    print("\nNext steps:")
    print("1. Run this script to identify specific failure patterns")
    print("2. Check your MCP server logs for the exact JSON that's failing")
    print("3. Implement the suggested fixes")
    print("4. Test with small, simple operations first")