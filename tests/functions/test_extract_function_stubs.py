
"""
Test suite for extract_function_stubs function.

Docstring:
=================
Extract function stubs from a Python file.

Parses a Python file to identify all callable definitions and extracts
their signatures, type hints, and docstrings to create function stubs.

Args:
    file_path (str): Path to the Python file to analyze.

Returns:
    List[Dict[str, Any]]: A list of dictionaries, each containing:
        - 'name' (str): The function/class name
        - 'signature' (str): Complete function signature with type hints
        - 'docstring' (Optional[str]): The function's docstring if present
        - 'is_async' (bool): Whether the function is an async function
        - 'is_method' (bool): Whether the function is a class method
        - 'class_name' (Optional[str]): Name of containing class if is_method is True

Raises:
    FileNotFoundError: If the specified file does not exist.
    PermissionError: If the file cannot be read due to permission issues.
    SyntaxError: If the Python file contains syntax errors.
    ValueError: If the file_path is empty or invalid.
    OSError: If there are other file system related errors.

Example:
    >>> stubs = extract_function_stubs('my_module.py')
    >>> for stub in stubs:
    ...     print(f"Function: {stub['name']}")
    ...     print(f"Signature: {stub['signature']}")
    ...     if stub['docstring']:
    ...         print(f"Docstring: {stub['docstring'][:50]}...")
    >>> # Example usage in a script:
    >>> stubs = extract_function_stubs('./src/utils.py')
    >>> async_funcs = [s for s in stubs if s['is_async']]
"""
import unittest
import tempfile
import os
from typing import Any, List, Dict
from tools.functions.extract_function_stubs import extract_function_stubs


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of extract_function_stubs."""
    
    def test_simple_function_with_type_hints_and_docstring(self):
        """
        GIVEN a temporary file with:
            def add_numbers(a: int, b: int) -> int:
                \"\"\"Add two numbers together.\"\"\"
                return a + b
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "add_numbers"
            - signature contains "a: int, b: int) -> int"
            - docstring = "Add two numbers together."
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'add_numbers')
                self.assertIn('a: int, b: int) -> int', stub['signature'])
                self.assertEqual(stub['docstring'], 'Add two numbers together.')
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)

    def test_file_with_multiple_functions(self):
        """
        GIVEN a temporary file with:
            def func1(): pass
            def func2(): pass
            def func3(): pass
        WHEN extract_function_stubs is called
        THEN expect 3 results with names ["func1", "func2", "func3"]
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def func1(): pass
def func2(): pass
def func3(): pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 3)
                names = [stub['name'] for stub in result]
                self.assertEqual(names, ['func1', 'func2', 'func3'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_no_type_hints(self):
        """
        GIVEN a temporary file with:
            def no_hints(a, b):
                return a + b
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "no_hints"
            - signature contains "(a, b)" without type annotations
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def no_hints(a, b):
    return a + b
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'no_hints')
                self.assertIn('(a, b)', stub['signature'])
                self.assertNotIn(':', stub['signature'])  # No type annotations
            finally:
                os.unlink(f.name)
    
    def test_functions_with_no_docstrings(self):
        """
        GIVEN a temporary file with:
            def no_docstring():
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - docstring = None or empty string
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def no_docstring():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn(stub['docstring'], [None, ''])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_both_type_hints_and_docstrings(self):
        """
        GIVEN a temporary file with:
            def complete_func(x: str) -> str:
                \"\"\"Returns the input string.\"\"\"
                return x
        WHEN extract_function_stubs is called
        THEN expect 1 result with all fields properly populated
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def complete_func(x: str) -> str:
    """Returns the input string."""
    return x
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'complete_func')
                self.assertIn('x: str) -> str', stub['signature'])
                self.assertEqual(stub['docstring'], 'Returns the input string.')
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)


class TestFunctionSignatureVariations(unittest.TestCase):
    """Test various function signature patterns."""
    
    def test_functions_with_no_parameters(self):
        """
        GIVEN a temporary file with:
            def no_params() -> None:
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to be "() -> None"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def no_params() -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('() -> None', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_positional_parameters_only(self):
        """
        GIVEN a temporary file with:
            def pos_only(a, b, c):
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to contain "(a, b, c)"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def pos_only(a, b, c):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('(a, b, c)', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_keyword_parameters_with_defaults(self):
        """
        GIVEN a temporary file with:
            def with_defaults(a: int, b: str = "default", c: bool = True):
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to contain 'b: str = "default"' and 'c: bool = True'
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def with_defaults(a: int, b: str = "default", c: bool = True):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('b: str = "default"', stub['signature'])
                self.assertIn('c: bool = True', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_args_and_kwargs(self):
        """
        GIVEN a temporary file with:
            def variadic(a: int, *args: str, **kwargs: Any) -> None:
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to contain "*args: str" and "**kwargs: Any"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''from typing import Any

def variadic(a: int, *args: str, **kwargs: Any) -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('*args: str', stub['signature'])
                self.assertIn('**kwargs: Any', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_complex_type_hints(self):
        """
        GIVEN a temporary file with:
            from typing import Union, Optional, List, Dict
            def complex_types(x: Union[int, str], y: Optional[List[Dict[str, int]]]) -> None:
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to preserve complex type annotations exactly
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''from typing import Union, Optional, List, Dict

def complex_types(x: Union[int, str], y: Optional[List[Dict[str, int]]]) -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('Union[int, str]', stub['signature'])
                self.assertIn('Optional[List[Dict[str, int]]]', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_functions_with_return_type_annotations(self):
        """
        GIVEN a temporary file with:
            def returns_int() -> int:
                return 42
        WHEN extract_function_stubs is called
        THEN expect signature to end with "-> int"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def returns_int() -> int:
    return 42
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('-> int', stub['signature'])
            finally:
                os.unlink(f.name)


class TestClassAndMethodTests(unittest.TestCase):
    """Test detection of class methods vs standalone functions."""
    
    def test_standalone_functions_not_in_classes(self):
        """
        GIVEN a temporary file with:
            def standalone():
                pass
        WHEN extract_function_stubs is called
        THEN expect:
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def standalone():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_methods_regular_instance_methods(self):
        """
        GIVEN a temporary file with:
            class MyClass:
                def instance_method(self, x: int) -> str:
                    pass
        WHEN extract_function_stubs is called
        THEN expect:
            - name = "instance_method"
            - is_method = True
            - class_name = "MyClass"
            - signature contains "self, x: int"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MyClass:
    def instance_method(self, x: int) -> str:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'instance_method')
                self.assertTrue(stub['is_method'])
                self.assertEqual(stub['class_name'], 'MyClass')
                self.assertIn('self, x: int', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_static_methods(self):
        """
        GIVEN a temporary file with:
            class MyClass:
                @staticmethod
                def static_method(x: int) -> int:
                    pass
        WHEN extract_function_stubs is called
        THEN expect method to be detected with appropriate metadata
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MyClass:
    @staticmethod
    def static_method(x: int) -> int:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'static_method')
                self.assertTrue(stub['is_method'])
                self.assertEqual(stub['class_name'], 'MyClass')
                self.assertIn('x: int', stub['signature'])
                self.assertNotIn('self', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_class_methods_with_classmethod_decorator(self):
        """
        GIVEN a temporary file with:
            class MyClass:
                @classmethod
                def class_method(cls, x: int) -> int:
                    pass
        WHEN extract_function_stubs is called
        THEN expect method to be detected with signature containing "cls"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MyClass:
    @classmethod
    def class_method(cls, x: int) -> int:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'class_method')
                self.assertTrue(stub['is_method'])
                self.assertEqual(stub['class_name'], 'MyClass')
                self.assertIn('cls, x: int', stub['signature'])
            finally:
                os.unlink(f.name)
    
    def test_property_decorators(self):
        """
        GIVEN a temporary file with:
            class MyClass:
                @property
                def my_property(self) -> str:
                    return "value"
        WHEN extract_function_stubs is called
        THEN expect property to be detected (or decide if it should be excluded)
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MyClass:
    @property
    def my_property(self) -> str:
        return "value"
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                # Properties might be included or excluded - test for either behavior
                if len(result) == 1:
                    stub = result[0]
                    self.assertEqual(stub['name'], 'my_property')
                    self.assertTrue(stub['is_method'])
                    self.assertEqual(stub['class_name'], 'MyClass')
                else:
                    self.assertEqual(len(result), 0)
            finally:
                os.unlink(f.name)
    
    def test_nested_classes_and_their_methods(self):
        """
        GIVEN a temporary file with:
            class Outer:
                class Inner:
                    def inner_method(self):
                        pass
                def outer_method(self):
                    pass
        WHEN extract_function_stubs is called
        THEN expect both methods detected with correct class_name values
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class Outer:
    class Inner:
        def inner_method(self):
            pass
    def outer_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 2)
                
                # Find methods by name
                inner_stub = next(s for s in result if s['name'] == 'inner_method')
                outer_stub = next(s for s in result if s['name'] == 'outer_method')
                
                self.assertEqual(inner_stub['class_name'], 'Inner')
                self.assertEqual(outer_stub['class_name'], 'Outer')
            finally:
                os.unlink(f.name)
    
    def test_inheritance_scenarios(self):
        """
        GIVEN a temporary file with:
            class Parent:
                def parent_method(self):
                    pass
            class Child(Parent):
                def child_method(self):
                    pass
        WHEN extract_function_stubs is called
        THEN expect both methods detected with correct class associations
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class Parent:
    def parent_method(self):
        pass

class Child(Parent):
    def child_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 2)
                
                # Find methods by name
                parent_stub = next(s for s in result if s['name'] == 'parent_method')
                child_stub = next(s for s in result if s['name'] == 'child_method')
                
                self.assertEqual(parent_stub['class_name'], 'Parent')
                self.assertEqual(child_stub['class_name'], 'Child')
            finally:
                os.unlink(f.name)


class TestAsyncFunctionTests(unittest.TestCase):
    """Test detection of async vs synchronous functions."""
    
    def test_regular_synchronous_functions(self):
        """
        GIVEN a temporary file with:
            def sync_func():
                pass
        WHEN extract_function_stubs is called
        THEN expect is_async = False
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def sync_func():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertFalse(stub['is_async'])
            finally:
                os.unlink(f.name)
    
    def test_async_functions(self):
        """
        GIVEN a temporary file with:
            async def async_func():
                pass
        WHEN extract_function_stubs is called
        THEN expect is_async = True
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''async def async_func():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertTrue(stub['is_async'])
            finally:
                os.unlink(f.name)
    
    def test_async_methods_in_classes(self):
        """
        GIVEN a temporary file with:
            class MyClass:
                async def async_method(self):
                    pass
        WHEN extract_function_stubs is called
        THEN expect:
            - is_async = True
            - is_method = True
            - class_name = "MyClass"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MyClass:
    async def async_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertTrue(stub['is_async'])
                self.assertTrue(stub['is_method'])
                self.assertEqual(stub['class_name'], 'MyClass')
            finally:
                os.unlink(f.name)


class TestEdgeCasesAndErrorConditions(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_python_file(self):
        """
        GIVEN an empty file with no content
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(result, [])
            finally:
                os.unlink(f.name)
    
    def test_file_containing_only_comments(self):
        """
        GIVEN a file with:
            # This is a comment
            # Another comment
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''# This is a comment
# Another comment
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(result, [])
            finally:
                os.unlink(f.name)
    
    def test_file_containing_only_import_statements(self):
        """
        GIVEN a file with:
            import os
            from typing import Any
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''import os
from typing import Any
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(result, [])
            finally:
                os.unlink(f.name)
    
    def test_file_containing_syntax_errors(self):
        """
        GIVEN a file with:
            def broken_syntax(
                # Missing closing parenthesis and colon
        WHEN extract_function_stubs is called
        THEN expect SyntaxError to be raised
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def broken_syntax(
    # Missing closing parenthesis and colon
''')
            f.flush()
            
            try:
                with self.assertRaises(SyntaxError):
                    extract_function_stubs(f.name)
            finally:
                os.unlink(f.name)
    
    def test_non_existent_file_path(self):
        """
        GIVEN a file path "/nonexistent/path/file.py"
        WHEN extract_function_stubs is called
        THEN expect FileNotFoundError to be raised
        """
        with self.assertRaises(FileNotFoundError):
            extract_function_stubs('/nonexistent/path/file.py')
    
    def test_empty_string_as_file_path(self):
        """
        GIVEN file_path = ""
        WHEN extract_function_stubs is called
        THEN expect ValueError to be raised
        """
        with self.assertRaises(ValueError):
            extract_function_stubs('')
    
    def test_directory_path_instead_of_file_path(self):
        """
        GIVEN a directory path "/some/directory"
        WHEN extract_function_stubs is called
        THEN expect appropriate error (IsADirectoryError or similar)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises((IsADirectoryError, OSError, ValueError)):
                extract_function_stubs(tmpdir)
    
    def test_non_python_file_wrong_extension(self):
        """
        GIVEN a file "test.txt" with Python code inside
        WHEN extract_function_stubs is called
        THEN expect either:
            - Function works (treats as Python regardless of extension), OR
            - Appropriate error is raised
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('''def valid_python():
    pass
''')
            f.flush()
            
            try:
                # Either it works or raises an error - both are valid behaviors
                try:
                    result = extract_function_stubs(f.name)
                    # If it works, verify the result
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]['name'], 'valid_python')
                except (ValueError, OSError):
                    # If it raises an error, that's also acceptable
                    pass
            finally:
                os.unlink(f.name)
    
    def test_file_with_no_read_permissions(self):
        """
        GIVEN a file with permissions set to write-only
        WHEN extract_function_stubs is called
        THEN expect PermissionError to be raised
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''def test_func():
    pass
''')
            f.flush()
            
            try:
                # Set file to write-only (no read permissions)
                os.chmod(f.name, 0o200)
                
                with self.assertRaises(PermissionError):
                    extract_function_stubs(f.name)
            finally:
                # Restore permissions to delete the file
                os.chmod(f.name, 0o600)
                os.unlink(f.name)


class TestDocstringVariations(unittest.TestCase):
    """Test handling of different docstring formats."""

    def test_single_line_docstrings(self):
        """
        GIVEN a file with:
            def func():
                \"\"\"Single line docstring.\"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect docstring = "Single line docstring."
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func():
    """Single line docstring."""
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(result[0]['docstring'], 'Single line docstring.')
            finally:
                os.unlink(f.name)

    def test_multi_line_docstrings(self):
        """
        GIVEN a file with:
            def func():
                \"\"\"
                Multi-line docstring
                with multiple lines.
                \"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect docstring to preserve formatting and newlines
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func():
    """
    Multi-line docstring
    with multiple lines.
    """
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                expected = "Multi-line docstring\nwith multiple lines."
                self.assertEqual(result[0]['docstring'].strip(), expected)
            finally:
                os.unlink(f.name)

    def test_google_style_docstrings(self):
        """
        GIVEN a file with Google-style docstring including Args, Returns, Raises sections
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured with formatting preserved
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func(a: int) -> int:
    """
    Short description.

    Args:
        a (int): Input number.

    Returns:
        int: Output number incremented by 1.

    Raises:
        ValueError: If input is negative.
    """
    return a + 1
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertIn('Args:', result[0]['docstring'])
                self.assertIn('Returns:', result[0]['docstring'])
                self.assertIn('Raises:', result[0]['docstring'])
            finally:
                os.unlink(f.name)

    def test_numpy_style_docstrings(self):
        """
        GIVEN a file with NumPy-style docstring using Parameters, Returns sections
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func(a: int) -> int:
    """
    Short description.

    Parameters
    ----------
    a : int
        Input number.

    Returns
    -------
    int
        Output number incremented by 1.
    """
    return a + 1
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertIn('Parameters', result[0]['docstring'])
                self.assertIn('Returns', result[0]['docstring'])
            finally:
                os.unlink(f.name)

    def test_sphinx_style_docstrings(self):
        """
        GIVEN a file with Sphinx-style docstring using :param: and :returns: syntax
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func(a: int) -> int:
    """
    Short description.

    :param a: Input number.
    :type a: int
    :returns: Output number incremented by 1.
    :rtype: int
    """
    return a + 1
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertIn(':param a:', result[0]['docstring'])
                self.assertIn(':returns:', result[0]['docstring'])
            finally:
                os.unlink(f.name)

    def test_no_docstring_at_all(self):
        """
        GIVEN a file with:
            def func():
                x = 1
                return x
        WHEN extract_function_stubs is called
        THEN expect docstring = None
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def func():
    x = 1
    return x
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertIsNone(result[0]['docstring'])
            finally:
                os.unlink(f.name)


class TestComplexPythonConstructs(unittest.TestCase):
    """Test handling of complex Python language constructs."""

    def test_decorators_on_functions(self):
        """
        GIVEN a file with:
            @decorator
            @another_decorator(param=value)
            def decorated_func():
                pass
        WHEN extract_function_stubs is called
        THEN expect function to be detected (decorators may or may not be included in signature)
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
@decorator
@another_decorator(param='value')
def decorated_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['name'], 'decorated_func')
            finally:
                os.unlink(f.name)

    def test_lambda_functions(self):
        """
        GIVEN a file with:
            my_lambda = lambda x: x + 1
        WHEN extract_function_stubs is called
        THEN expect either:
            - Lambda is ignored (likely), OR
            - Lambda is detected as a callable
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''my_lambda = lambda x: x + 1
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                # Typically lambdas are not detected as callable definitions by parsing tools.
                self.assertEqual(len(result), 0)
            finally:
                os.unlink(f.name)

    def test_nested_function_definitions(self):
        """
        GIVEN a file with:
            def outer():
                def inner():
                    pass
                return inner
        WHEN extract_function_stubs is called
        THEN expect both functions to be detected
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def outer():
    def inner():
        pass
    return inner
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                names = {stub['name'] for stub in result}
                self.assertSetEqual(names, {'outer', 'inner'})
            finally:
                os.unlink(f.name)

    def test_functions_defined_inside_try_except_blocks(self):
        """
        GIVEN a file with:
            try:
                def func_in_try():
                    pass
            except:
                def func_in_except():
                    pass
        WHEN extract_function_stubs is called
        THEN expect both functions to be detected
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''try:
    def func_in_try():
        pass
except:
    def func_in_except():
        pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                names = {stub['name'] for stub in result}
                self.assertSetEqual(names, {'func_in_try', 'func_in_except'})
            finally:
                os.unlink(f.name)

    def test_functions_using_type_variables(self):
        """
        GIVEN a file with:
            from typing import TypeVar
            T = TypeVar('T')
            def generic_func(x: T) -> T:
                return x
        WHEN extract_function_stubs is called
        THEN expect TypeVar usage to be preserved in signature
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''from typing import TypeVar
T = TypeVar('T')

def generic_func(x: T) -> T:
    return x
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertIn('x: T', stub['signature'])
                self.assertIn('-> T', stub['signature'])
            finally:
                os.unlink(f.name)


class TestOutputValidation(unittest.TestCase):
    """Test validation of output format and content."""

    def test_correct_structure_of_returned_dictionaries(self):
        """
        GIVEN any valid Python file with functions
        WHEN extract_function_stubs is called
        THEN expect each result to be a dictionary with exactly the required keys
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def test_func(a: int) -> int:
    """Test function."""
    return a
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                required_keys = {'name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name'}
                self.assertTrue(all(set(stub.keys()) == required_keys for stub in result))
            finally:
                os.unlink(f.name)

    def test_all_expected_keys_are_present(self):
        """
        GIVEN any valid function stub result
        WHEN examining the dictionary
        THEN expect keys: ['name', 'signature', 'docstring', 'is_async', 'is_method', 'class_name']
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def another_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)[0]
                expected_keys = ['name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name']
                self.assertListEqual(sorted(result.keys()), sorted(expected_keys))
            finally:
                os.unlink(f.name)

    def test_data_types_of_each_field(self):
        """
        GIVEN any function stub result
        WHEN examining field types
        THEN expect:
            - name: str
            - signature: str
            - docstring: str | None
            - is_async: bool
            - is_method: bool
            - class_name: str | None
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''async def async_func():
    """An async function."""
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)[0]
                self.assertIsInstance(result['name'], str)
                self.assertIsInstance(result['signature'], str)
                self.assertTrue(isinstance(result['docstring'], (str, type(None))))
                self.assertIsInstance(result['is_async'], bool)
                self.assertIsInstance(result['is_method'], bool)
                self.assertTrue(isinstance(result['class_name'], (str, type(None))))
            finally:
                os.unlink(f.name)

    def test_is_method_flag_correctly_set(self):
        """
        GIVEN files with both standalone functions and class methods
        WHEN extract_function_stubs is called
        THEN expect is_method = True only for class methods, False for standalone functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
def standalone():
    pass

class MyClass:
    def method(self):
        pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                standalone = next(s for s in result if s['name'] == 'standalone')
                method = next(s for s in result if s['name'] == 'method')
                self.assertFalse(standalone['is_method'])
                self.assertTrue(method['is_method'])
            finally:
                os.unlink(f.name)

    def test_class_name_correctly_populated(self):
        """
        GIVEN class methods
        WHEN extract_function_stubs is called
        THEN expect class_name to match the containing class name exactly
        AND expect class_name = None for standalone functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
class MyClass:
    def method(self):
        pass

def standalone():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                method = next(s for s in result if s['name'] == 'method')
                standalone = next(s for s in result if s['name'] == 'standalone')
                self.assertEqual(method['class_name'], 'MyClass')
                self.assertIsNone(standalone['class_name'])
            finally:
                os.unlink(f.name)

    def test_is_async_flag_correctly_set(self):
        """
        GIVEN mix of async and sync functions
        WHEN extract_function_stubs is called
        THEN expect is_async = True only for async functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
async def async_func():
    pass

def sync_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                async_stub = next(s for s in result if s['name'] == 'async_func')
                sync_stub = next(s for s in result if s['name'] == 'sync_func')
                self.assertTrue(async_stub['is_async'])
                self.assertFalse(sync_stub['is_async'])
            finally:
                os.unlink(f.name)

    def test_if_decorators_are_detected(self):
        """
        GIVEN a file with decorated functions
        WHEN extract_function_stubs is called
        THEN expect decorators to be captured in the 'decorators' field
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''@my_decorator
def decorated_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                decorated_func_stub = next(s for s in result if s['name'] == 'decorated_func')
                self.assertTrue(decorated_func_stub['decorators'])
                self.assertFalse(decorated_func_stub['is_async'])
            finally:
                os.unlink(f.name)


class TestRealWorldScenarios(unittest.TestCase):
    """Test with real-world Python files and complex scenarios."""

    def test_actual_python_standard_library_modules(self):
        """
        GIVEN a standard library file like "/usr/lib/python3.x/json/__init__.py"
        WHEN extract_function_stubs is called
        THEN expect reasonable number of functions detected without errors
        AND expect all public functions to be found
        """
        import json
        json_path = json.__file__

        result = extract_function_stubs(json_path)

        # json module has at least load, loads, dump, dumps
        public_functions = {'load', 'loads', 'dump', 'dumps'}
        extracted_names = {stub['name'] for stub in result}

        self.assertTrue(public_functions.issubset(extracted_names))

    def test_complex_third_party_library_files(self):
        """
        GIVEN a complex library file (if available in test environment)
        WHEN extract_function_stubs is called
        THEN expect function to handle complex real-world code without crashing
        """
        # Use a standard library module as proxy for complexity
        import unittest
        unittest_path = unittest.__file__

        try:
            result = extract_function_stubs(unittest_path)
            self.assertTrue(len(result) > 0)
        except Exception as e:
            self.fail(f"extract_function_stubs crashed with exception {e}")

    def test_files_with_multiple_classes_with_many_methods(self):
        """
        GIVEN a file with:
            class ClassA:
                def method1(self): pass
                def method2(self): pass
            class ClassB:
                def method3(self): pass
                def method4(self): pass
        WHEN extract_function_stubs is called
        THEN expect all 4 methods detected with correct class associations
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
class ClassA:
    def method1(self): pass
    def method2(self): pass

class ClassB:
    def method3(self): pass
    def method4(self): pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 4)
                class_a_methods = {stub['name'] for stub in result if stub['class_name'] == 'ClassA'}
                class_b_methods = {stub['name'] for stub in result if stub['class_name'] == 'ClassB'}

                self.assertSetEqual(class_a_methods, {'method1', 'method2'})
                self.assertSetEqual(class_b_methods, {'method3', 'method4'})
            finally:
                os.unlink(f.name)

    def test_presence_in_markdown(self):
        """
        GIVEN a file with various function types and a markdown output path
        WHEN extract_function_stubs is called with markdown_path parameter
        THEN expect all functions to be present in the markdown output with correct formatting
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''
class MyClass:
    def method(self):
        """This is a method."""
        pass

    @property
    def some_property(self):
        """This is a property."""
        pass
    
    @random_decorator
    def method_with_decorator(self):
        """This is a method with a decorator."""
        pass

def standalone():
    """This is a standalone function."""
    pass

async def async_standalone():
    """This is an async standalone function."""
    pass

@some_decorator
def decorated_standalone():
    """This is a decorated standalone function."""
    pass

@some_other_decorator
async def async_decorated_standalone():
    """This is an async decorated standalone function."""
    pass
    ''')
            f.flush()
            
            with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as md_file:
                try:
                    result = extract_function_stubs(f.name, md_file.name)
                    
                    # Verify stubs were extracted
                    self.assertGreater(len(result), 0)
                    
                    # Read the markdown file
                    with open(md_file.name, 'r', encoding='utf-8') as md_handle:
                        markdown_content = md_handle.read()
                    
                    # Check that all functions are present in markdown
                    expected_functions = ['method', 'some_property', 'method_with_decorator', 
                                        'standalone', 'async_standalone', 'decorated_standalone', 
                                        'async_decorated_standalone']
                    
                    for func_name in expected_functions:
                        self.assertIn(f"## {func_name}", markdown_content)

                    # Check if decorators are included
                    self.assertIn("@property", markdown_content)
                    self.assertIn("@random_decorator", markdown_content)
                    self.assertIn("@some_decorator", markdown_content)
                    self.assertIn("@some_other_decorator", markdown_content)
                    
                    # Check for async functions properly marked
                    self.assertIn("async def async_standalone", markdown_content)
                    self.assertIn("async def async_decorated_standalone", markdown_content)
                    
                    # Check for regular functions
                    self.assertIn("def method(", markdown_content)
                    self.assertIn("def standalone(", markdown_content)
                    
                    # Check docstrings are included
                    self.assertIn("This is a method.", markdown_content)
                    self.assertIn("This is a standalone function.", markdown_content)
                    self.assertIn("This is an async standalone function.", markdown_content)
                    
                    # Check metadata is present
                    self.assertIn("**Async:** True", markdown_content)
                    self.assertIn("**Async:** False", markdown_content)
                    self.assertIn("**Method:** True", markdown_content)
                    self.assertIn("**Method:** False", markdown_content)
                    self.assertIn("**Class:** MyClass", markdown_content)
                    self.assertIn("**Class:** N/A", markdown_content)
                    
                finally:
                    os.unlink(f.name)
                    os.unlink(md_file.name)



if __name__ == '__main__':
    unittest.main()
