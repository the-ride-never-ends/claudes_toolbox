
"""
Test suite for extract_function_stubs function.

Docstring:
=================
Extract function stubs from a Python file or directory.

Parses Python files to identify all callable definitions and extracts
their signatures, type hints, and docstrings to create function stubs.

If a directory is provided, all Python files in the directory will be
processed. If a file is provided, only that file will be processed.

Args:
    path (str): Path to the Python file or directory to analyze.
    markdown_path (Optional[str]): If provided, the function will write
        the extracted stubs to a markdown file at this path. If not
        specified, no markdown file will be created.
    recursive (bool): If True and path is a directory, search subdirectories
        recursively for Python files. Ignored if path is a file.

Returns:
    List[Dict[str, Any]]: A list of dictionaries, each containing:
        - 'name' (str): The function/class name
        - 'signature' (str): Complete function signature with type hints
        - 'docstring' (Optional[str]): The function's docstring if present
        - 'is_async' (bool): Whether the function is an async function
        - 'is_method' (bool): Whether the function is a class method
        - 'decorators' (list[str]): List of decorator names as strings
        - 'class_name' (Optional[str]): Name of containing class if is_method is True
        - 'file_path' (str): Path to the file containing this function/class

Raises:
    PermissionError: If files cannot be read due to permission issues.
    SyntaxError: If Python files contain syntax errors.
    ValueError: If the path is empty or invalid.
    OSError: If there are other file system related errors.

Example:
    >>> # Extract from a single file
    >>> stubs = extract_function_stubs('my_module.py')
    >>> for stub in stubs:
    ...     print(f"Function: {stub['name']} in {stub['file_path']}")
    ...     print(f"Signature: {stub['signature']}")
    ...     if stub['docstring']:
    ...         print(f"Docstring: {stub['docstring'][:50]}...")
    >>> 
    >>> # Extract from a directory
    >>> stubs = extract_function_stubs('./src/', recursive=True)
    >>> async_funcs = [s for s in stubs if s['is_async']]
    >>> 
    >>> # Extract from directory with markdown output
    >>> stubs = extract_function_stubs('./src/', 'output.md', recursive=False)
"""
import unittest
import tempfile
import os
import json
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
                
                self.assertEqual(len(result), 2)  # One for class, one for method
                # Find the method stub by name
                method_stub = next(s for s in result if s['name'] == 'instance_method')
                self.assertEqual(method_stub['name'], 'instance_method')
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'MyClass')
                self.assertIn('self, x: int', method_stub['signature'])
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
                
                self.assertEqual(len(result), 2)  # One for class, one for method
                # Find the static method stub by name
                method_stub = next(s for s in result if s['name'] == 'static_method')
                self.assertEqual(method_stub['name'], 'static_method')
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'MyClass')
                self.assertIn('x: int', method_stub['signature'])
                self.assertNotIn('self', method_stub['signature'])
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
                
                self.assertEqual(len(result), 2) # One for class, one for method
                # Find the class method stub by name
                method_stub = next(s for s in result if s['name'] == 'class_method')
                self.assertEqual(method_stub['name'], 'class_method')
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'MyClass')
                self.assertIn('cls, x: int', method_stub['signature'])
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
                if len(result) == 2:
                    # Find the property stub by name
                    property_stub = next(s for s in result if s['name'] == 'my_property')
                    self.assertEqual(property_stub['name'], 'my_property')
                    self.assertTrue(property_stub['is_method'])
                    self.assertEqual(property_stub['class_name'], 'MyClass')
                else:
                    self.assertEqual(len(result), 1)  # Just the class
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
                
                self.assertEqual(len(result), 4) # Two classes + two methods
                
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
                
                self.assertEqual(len(result), 4) # Two classes + two methods
                
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
                
                self.assertEqual(len(result), 2)  # One for class, one for method
                # Find the async method stub by name
                method_stub = next(s for s in result if s['name'] == 'async_method')
                self.assertTrue(method_stub['is_async'])
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'MyClass')
            finally:
                os.unlink(f.name)


class TestDirectoryFunctionality(unittest.TestCase):
    """Test directory handling functionality."""
    
    def test_directory_with_single_python_file(self):
        """
        GIVEN a directory with one Python file containing functions
        WHEN extract_function_stubs is called on the directory
        THEN expect functions from that file to be extracted
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file in the directory
            python_file = os.path.join(tmpdir, 'test_module.py')
            with open(python_file, 'w') as f:
                f.write('''def func1():
    """First function."""
    pass

def func2():
    """Second function."""
    pass
''')
            
            result = extract_function_stubs(tmpdir)
            
            self.assertEqual(len(result), 2)
            names = {stub['name'] for stub in result}
            self.assertEqual(names, {'func1', 'func2'})
            
            # Check that file_path is set correctly
            for stub in result:
                self.assertEqual(stub['file_path'], python_file)
    
    def test_directory_with_multiple_python_files(self):
        """
        GIVEN a directory with multiple Python files
        WHEN extract_function_stubs is called on the directory  
        THEN expect functions from all files to be extracted
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first Python file
            file1 = os.path.join(tmpdir, 'module1.py')
            with open(file1, 'w') as f:
                f.write('''def func_from_file1():
    pass
''')
            
            # Create second Python file
            file2 = os.path.join(tmpdir, 'module2.py')
            with open(file2, 'w') as f:
                f.write('''def func_from_file2():
    pass
''')
            
            result = extract_function_stubs(tmpdir)
            
            self.assertEqual(len(result), 2)
            names = {stub['name'] for stub in result}
            self.assertEqual(names, {'func_from_file1', 'func_from_file2'})
            
            # Check that file_path is set correctly for each function
            file_paths = {stub['file_path'] for stub in result}
            self.assertEqual(file_paths, {file1, file2})
    
    def test_directory_with_subdirectories_recursive_true(self):
        """
        GIVEN a directory with subdirectories containing Python files
        WHEN extract_function_stubs is called with recursive=True
        THEN expect functions from all files including subdirectories
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file in root directory
            root_file = os.path.join(tmpdir, 'root.py')
            with open(root_file, 'w') as f:
                f.write('''def root_func():
    pass
''')
            
            # Create subdirectory with file
            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)
            sub_file = os.path.join(subdir, 'sub.py')
            with open(sub_file, 'w') as f:
                f.write('''def sub_func():
    pass
''')
            
            result = extract_function_stubs(tmpdir, recursive=True)
            
            self.assertEqual(len(result), 2)
            names = {stub['name'] for stub in result}
            self.assertEqual(names, {'root_func', 'sub_func'})
    
    def test_directory_with_subdirectories_recursive_false(self):
        """
        GIVEN a directory with subdirectories containing Python files
        WHEN extract_function_stubs is called with recursive=False
        THEN expect functions only from root directory files
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file in root directory
            root_file = os.path.join(tmpdir, 'root.py')
            with open(root_file, 'w') as f:
                f.write('''def root_func():
    pass
''')
            
            # Create subdirectory with file
            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)
            sub_file = os.path.join(subdir, 'sub.py')
            with open(sub_file, 'w') as f:
                f.write('''def sub_func():
    pass
''')
            
            result = extract_function_stubs(tmpdir, recursive=False)
            
            self.assertEqual(len(result), 1)
            names = {stub['name'] for stub in result}
            self.assertEqual(names, {'root_func'})
    
    def test_directory_with_no_python_files(self):
        """
        GIVEN a directory with no Python files
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some non-Python files
            with open(os.path.join(tmpdir, 'readme.txt'), 'w') as f:
                f.write('This is not Python')
            
            result = extract_function_stubs(tmpdir)
            
            self.assertEqual(result, [])
    
    def test_directory_with_mixed_file_types(self):
        """
        GIVEN a directory with Python files and other file types
        WHEN extract_function_stubs is called
        THEN expect only Python files to be processed
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file
            python_file = os.path.join(tmpdir, 'module.py')
            with open(python_file, 'w') as f:
                f.write('''def python_func():
    pass
''')
            
            # Create non-Python files
            with open(os.path.join(tmpdir, 'readme.txt'), 'w') as f:
                f.write('Not Python')
            with open(os.path.join(tmpdir, 'data.json'), 'w') as f:
                f.write('{"not": "python"}')
            
            result = extract_function_stubs(tmpdir)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['name'], 'python_func')
    
    def test_directory_with_syntax_error_files(self):
        """
        GIVEN a directory with one valid Python file and one with syntax errors
        WHEN extract_function_stubs is called
        THEN expect functions from valid file to be extracted, invalid file to be skipped
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create valid Python file
            valid_file = os.path.join(tmpdir, 'valid.py')
            with open(valid_file, 'w') as f:
                f.write('''def valid_func():
    pass
''')
            
            # Create invalid Python file
            invalid_file = os.path.join(tmpdir, 'invalid.py')
            with open(invalid_file, 'w') as f:
                f.write('''def broken_syntax(
    # Missing closing parenthesis
''')
            
            result = extract_function_stubs(tmpdir)
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['name'], 'valid_func')


class TestDirectoryMarkdownOutput(unittest.TestCase):
    """Test markdown output for directory processing."""
    
    def test_directory_markdown_output_multiple_files(self):
        """
        GIVEN a directory with multiple Python files
        WHEN extract_function_stubs is called with markdown_path
        THEN expect markdown file to be created with functions from all files
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple Python files
            file1 = os.path.join(tmpdir, 'module1.py')
            with open(file1, 'w') as f:
                f.write('''def func1():
    """Function from file 1."""
    pass
''')
            
            file2 = os.path.join(tmpdir, 'module2.py')
            with open(file2, 'w') as f:
                f.write('''def func2():
    """Function from file 2."""
    pass
''')
            
            # Create markdown output file
            md_file = os.path.join(tmpdir, 'output.md')
            
            result = extract_function_stubs(tmpdir, markdown_path=md_file)
            
            # Check that markdown file was created
            self.assertTrue(os.path.exists(md_file))
            
            # Check markdown content
            with open(md_file, 'r') as f:
                content = f.read()
                self.assertIn('func1', content)
                self.assertIn('func2', content)
                self.assertIn('Function from file 1', content)
                self.assertIn('Function from file 2', content)
                self.assertIn('Files processed:', content)


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
    
    def test_empty_string_as_file_path(self):
        """
        GIVEN file_path = ""
        WHEN extract_function_stubs is called
        THEN expect ValueError to be raised
        """
        with self.assertRaises(ValueError):
            extract_function_stubs('')
    
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
                required_keys = {'name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name', 'file_path'}
                self.assertTrue(all(set(stub.keys()) == required_keys for stub in result))
            finally:
                os.unlink(f.name)

    def test_all_expected_keys_are_present(self):
        """
        GIVEN any valid function stub result
        WHEN examining the dictionary
        THEN expect keys: ['name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name', 'file_path']
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
            f.write('''def another_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name)[0]
                expected_keys = ['name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name', 'file_path']
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
            - decorators: list
            - class_name: str | None
            - file_path: str
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
                self.assertIsInstance(result['decorators'], list)
                self.assertTrue(isinstance(result['class_name'], (str, type(None))))
                self.assertIsInstance(result['file_path'], str)
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
                self.assertEqual(len(result), 6)  # 2 classes + 4 methods
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
            f.write('''from abc import ABC

@class_decorator
class MyClass(ABC):
    """This is a class."""
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

                    # Check if classes are included
                    self.assertIn("## MyClass", markdown_content)
                    self.assertIn("class MyClass(ABC):", markdown_content)

                    # Check if decorators are included
                    self.assertIn("@property", markdown_content)
                    self.assertIn("@random_decorator", markdown_content)
                    self.assertIn("@some_decorator", markdown_content)
                    self.assertIn("@some_other_decorator", markdown_content)
                    self.assertIn("@class_decorator", markdown_content)

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
                    self.assertIn("This is a class.", markdown_content)
                    
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


class TestClassDocstrings(unittest.TestCase):
    """Test extraction of class docstrings."""
    
    def test_class_with_single_line_docstring(self):
        """
        GIVEN a temporary file with:
            class SimpleClass:
                \"\"\"A simple class with a single line docstring.\"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "SimpleClass"
            - docstring = "A simple class with a single line docstring."
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class SimpleClass:
    """A simple class with a single line docstring."""
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'SimpleClass')
                self.assertEqual(stub['docstring'], 'A simple class with a single line docstring.')
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_with_multiline_docstring(self):
        """
        GIVEN a temporary file with:
            class ComplexClass:
                \"\"\"
                A complex class with multiline docstring.
                
                This class demonstrates multiple lines
                of documentation with proper formatting.
                
                Attributes:
                    attr1 (int): First attribute
                    attr2 (str): Second attribute
                \"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "ComplexClass"
            - docstring contains all lines including "A complex class" and "Attributes:"
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class ComplexClass:
    """
    A complex class with multiline docstring.
    
    This class demonstrates multiple lines
    of documentation with proper formatting.
    
    Attributes:
        attr1 (int): First attribute
        attr2 (str): Second attribute
    """
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'ComplexClass')
                self.assertIn('A complex class', stub['docstring'])
                self.assertIn('Attributes:', stub['docstring'])
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_without_docstring(self):
        """
        GIVEN a temporary file with:
            class NoDocClass:
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "NoDocClass"
            - docstring = None
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class NoDocClass:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'NoDocClass')
                self.assertIsNone(stub['docstring'])
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_with_methods_and_class_docstring(self):
        """
        GIVEN a temporary file with:
            class DocumentedClass:
                \"\"\"Class-level documentation.\"\"\"
                
                def method1(self):
                    \"\"\"Method-level documentation.\"\"\"
                    pass
        WHEN extract_function_stubs is called
        THEN expect 2 results:
            1. Class stub with:
                - name = "DocumentedClass"
                - docstring = "Class-level documentation."
                - is_method = False
                - class_name = None
            2. Method stub with:
                - name = "method1"
                - docstring = "Method-level documentation."
                - is_method = True
                - class_name = "DocumentedClass"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class DocumentedClass:
    """Class-level documentation."""
    
    def method1(self):
        """Method-level documentation."""
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 2)
                
                # Find class and method stubs
                class_stub = next(s for s in result if s['name'] == 'DocumentedClass')
                method_stub = next(s for s in result if s['name'] == 'method1')
                
                # Check class stub
                self.assertEqual(class_stub['docstring'], 'Class-level documentation.')
                self.assertFalse(class_stub['is_method'])
                self.assertIsNone(class_stub['class_name'])
                
                # Check method stub
                self.assertEqual(method_stub['docstring'], 'Method-level documentation.')
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'DocumentedClass')
            finally:
                os.unlink(f.name)


class TestClassDecorators(unittest.TestCase):
    """Test extraction of classes with decorators."""
    
    def test_class_with_single_decorator(self):
        """
        GIVEN a temporary file with:
            @dataclass
            class DataClass:
                name: str
                age: int
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "DataClass"
            - signature or decorators info includes "@dataclass"
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''@dataclass
class DataClass:
    name: str
    age: int
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                print(f"result: {result}")
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'DataClass')
                # Check if decorator info is present (might be in signature or separate field)
                self.assertTrue(
                    'dataclass' in stub.get('signature', '') or 
                    'dataclass' in str(stub.get('decorators', []))
                )
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_with_multiple_decorators(self):
        """
        GIVEN a temporary file with:
            @decorator1
            @decorator2(arg="value")
            @decorator3
            class MultiDecoratedClass:
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "MultiDecoratedClass"
            - decorators info includes all three decorators in order
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''@decorator1
@decorator2(arg="value")
@decorator3
class MultiDecoratedClass:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'MultiDecoratedClass')
                # Check all decorators are present
                stub_str = str(stub)
                self.assertIn('decorator1', stub_str)
                self.assertIn('decorator2', stub_str)
                self.assertIn('decorator3', stub_str)
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)

    def test_class_with_decorator_and_docstring(self):
        """
        GIVEN a temporary file with:
            @singleton
            class SingletonClass:
                \"\"\"A singleton implementation.\"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "SingletonClass"
            - decorator info includes "@singleton"
            - docstring = "A singleton implementation."
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''@singleton
class SingletonClass:
    """A singleton implementation."""
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'SingletonClass')
                self.assertIn('singleton', str(stub))
                self.assertEqual(stub['docstring'], 'A singleton implementation.')
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)

    def test_function_decorators_vs_class_decorators(self):
        """
        GIVEN a temporary file with:
            @function_decorator
            def decorated_func():
                pass
            
            @class_decorator
            class DecoratedClass:
                pass
        WHEN extract_function_stubs is called
        THEN expect 2 results with appropriate decorator info for each
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
@function_decorator
def decorated_func():
    pass

@class_decorator
class DecoratedClass:
    pass
''')
            f.flush()
            
            try:
                from pprint import pprint
                result = extract_function_stubs(f.name)
                for idx, res in enumerate(result, start=1):
                    pprint(f"{idx} result: {res}")
                self.assertEqual(len(result), 2)
                
                func_stub = next(s for s in result if s['name'] == 'decorated_func')
                class_stub = next(s for s in result if s['name'] == 'DecoratedClass')
                
                self.assertIn('function_decorator', str(func_stub))
                self.assertIn('class_decorator', str(class_stub))
            finally:
                os.unlink(f.name)

def add(x: int, y: int) -> int:
    """Add two numbers.
    
    x: int
    y: int

    Returns:
        int: The sum of x and y.
    """
    pass


class TestClassInheritance(unittest.TestCase):
    """Test extraction of class inheritance information."""

    def test_class_with_single_inheritance(self):
        """
        GIVEN a temporary file with:
            class ChildClass(ParentClass):
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "ChildClass"
            - signature or inheritance info includes "ParentClass"
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class ChildClass(ParentClass):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'ChildClass')
                self.assertIn('ParentClass', stub.get('signature', ''))
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_with_multiple_inheritance(self):
        """
        GIVEN a temporary file with:
            class MultiChild(Parent1, Parent2, Parent3):
                pass
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "MultiChild"
            - inheritance info includes all three parent classes in order
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class MultiChild(Parent1, Parent2, Parent3):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                self.assertEqual(stub['name'], 'MultiChild')
                sig = stub.get('signature', '')
                self.assertIn('Parent1', sig)
                self.assertIn('Parent2', sig)
                self.assertIn('Parent3', sig)
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)
    
    def test_class_inheriting_from_builtin_types(self):
        """
        GIVEN a temporary file with:
            class CustomList(list):
                pass
            
            class CustomDict(dict):
                pass
            
            class CustomException(Exception):
                pass
        WHEN extract_function_stubs is called
        THEN expect 3 results with appropriate inheritance from builtins
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class CustomList(list):
    pass

class CustomDict(dict):
    pass

class CustomException(Exception):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 3)
                
                names_and_parents = {
                    stub['name']: stub.get('signature', '') 
                    for stub in result
                }
                
                self.assertIn('list', names_and_parents['CustomList'])
                self.assertIn('dict', names_and_parents['CustomDict'])
                self.assertIn('Exception', names_and_parents['CustomException'])
            finally:
                os.unlink(f.name)

    def test_class_with_generic_inheritance(self):
        """
        GIVEN a temporary file with:
            from typing import Generic, TypeVar
            
            T = TypeVar('T')
            
            class GenericClass(Generic[T]):
                pass
            
            class SpecificClass(GenericClass[str]):
                pass
        WHEN extract_function_stubs is called
        THEN expect results with:
            - GenericClass inheriting from Generic[T]
            - SpecificClass inheriting from GenericClass[str]
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''from typing import Generic, TypeVar

T = TypeVar('T')

class GenericClass(Generic[T]):
    pass

class SpecificClass(GenericClass[str]):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                # Filter out TypeVar assignment if it appears
                class_results = [s for s in result if s['name'] in ['GenericClass', 'SpecificClass']]
                self.assertEqual(len(class_results), 2)
                
                generic_stub = next(s for s in class_results if s['name'] == 'GenericClass')
                specific_stub = next(s for s in class_results if s['name'] == 'SpecificClass')
                
                self.assertIn('Generic[T]', generic_stub.get('signature', ''))
                self.assertIn('GenericClass[str]', specific_stub.get('signature', ''))
            finally:
                os.unlink(f.name)

    def test_class_with_inheritance_decorator_and_docstring(self):
        """
        GIVEN a temporary file with:
            @dataclass
            class CompleteClass(BaseClass, Interface1, Interface2):
                \"\"\"
                A complete class with everything.
                
                This demonstrates inheritance, decorators, and docstring.
                \"\"\"
                field1: str
                field2: int
        WHEN extract_function_stubs is called
        THEN expect 1 result with:
            - name = "CompleteClass"
            - decorator info includes "@dataclass"
            - inheritance info includes all three parent classes
            - docstring contains the full multiline documentation
            - is_async = False
            - is_method = False
            - class_name = None
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''@dataclass
class CompleteClass(BaseClass, Interface1, Interface2):
    """
    A complete class with everything.
    
    This demonstrates inheritance, decorators, and docstring.
    """
    field1: str
    field2: int
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 1)
                stub = result[0]
                
                self.assertEqual(stub['name'], 'CompleteClass')
                self.assertIn('dataclass', str(stub))
                
                sig = stub.get('signature', '')
                self.assertIn('BaseClass', sig)
                self.assertIn('Interface1', sig)
                self.assertIn('Interface2', sig)
                
                self.assertIn('A complete class with everything', stub['docstring'])
                self.assertIn('This demonstrates inheritance', stub['docstring'])
                
                self.assertFalse(stub['is_async'])
                self.assertFalse(stub['is_method'])
                self.assertIsNone(stub['class_name'])
            finally:
                os.unlink(f.name)

    def test_nested_class_inheritance(self):
        """
        GIVEN a temporary file with:
            class OuterClass:
                class InnerBase:
                    pass
                
                class InnerChild(InnerBase):
                    pass
        WHEN extract_function_stubs is called
        THEN expect results showing:
            - OuterClass (no inheritance)
            - InnerBase (no inheritance, but nested in OuterClass)
            - InnerChild (inheriting from InnerBase, nested in OuterClass)
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''class OuterClass:
    class InnerBase:
        pass
    
    class InnerChild(InnerBase):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 3)
                
                outer_stub = next(s for s in result if s['name'] == 'OuterClass')
                inner_base_stub = next(s for s in result if s['name'] == 'InnerBase')
                inner_child_stub = next(s for s in result if s['name'] == 'InnerChild')
                
                # Check OuterClass has no inheritance
                self.assertNotIn('(', outer_stub.get('signature', 'class OuterClass'))
                
                # Check InnerChild inherits from InnerBase
                self.assertIn('InnerBase', inner_child_stub.get('signature', ''))
                
                # Both inner classes should have OuterClass as their class_name
                self.assertEqual(inner_base_stub['class_name'], 'OuterClass')
                self.assertEqual(inner_child_stub['class_name'], 'OuterClass')
            finally:
                os.unlink(f.name)


class TestClassExtractionComplexScenarios(unittest.TestCase):
    """Test complex combinations of class features."""

    def test_abstract_class_with_decorators_and_inheritance(self):
        """
        GIVEN a temporary file with:
            from abc import ABC, abstractmethod
            
            @dataclass
            class AbstractBase(ABC):
                \"\"\"Abstract base class.\"\"\"
                
                @abstractmethod
                def required_method(self) -> None:
                    \"\"\"Must be implemented by subclasses.\"\"\"
                    pass
        WHEN extract_function_stubs is called
        THEN expect results for:
            - AbstractBase class with decorator, inheritance from ABC, and docstring
            - required_method with @abstractmethod decorator and docstring
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''from abc import ABC, abstractmethod

@dataclass
class AbstractBase(ABC):
    """Abstract base class."""
    
    @abstractmethod
    def required_method(self) -> None:
        """Must be implemented by subclasses."""
        pass
''')
            f.flush()

            try:
                result = extract_function_stubs(f.name)
                # Should have at least AbstractBase and required_method
                self.assertGreaterEqual(len(result), 2)

                # Find the relevant stubs
                class_stub = next(s for s in result if s['name'] == 'AbstractBase')
                method_stub = next(s for s in result if s['name'] == 'required_method')

                # Check class stub
                self.assertIn('dataclass', str(class_stub))
                self.assertIn('ABC', class_stub.get('signature', ''))
                self.assertEqual(class_stub['docstring'], 'Abstract base class.')

                # Check method stub
                self.assertIn('abstractmethod', str(method_stub))
                self.assertEqual(method_stub['docstring'], 'Must be implemented by subclasses.')
                self.assertTrue(method_stub['is_method'])
                self.assertEqual(method_stub['class_name'], 'AbstractBase')
            finally:
                os.unlink(f.name)

    def test_metaclass_usage(self):
        """
        GIVEN a temporary file with:
            class MetaClass(type):
                \"\"\"A metaclass.\"\"\"
                pass
            
            class ClassWithMeta(metaclass=MetaClass):
                \"\"\"A class using a metaclass.\"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect results showing:
            - MetaClass inheriting from type
            - ClassWithMeta with metaclass information
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
class MetaClass(type):
    """A metaclass."""
    pass

class ClassWithMeta(metaclass=MetaClass):
    """A class using a metaclass."""
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name)
                self.assertEqual(len(result), 2)
                
                meta_stub = next(s for s in result if s['name'] == 'MetaClass')
                class_stub = next(s for s in result if s['name'] == 'ClassWithMeta')
                
                # Check MetaClass inherits from type
                self.assertIn('type', meta_stub.get('signature', ''))
                self.assertEqual(meta_stub['docstring'], 'A metaclass.')
                
                # Check ClassWithMeta has metaclass info
                self.assertEqual(class_stub['docstring'], 'A class using a metaclass.')
                # Metaclass info might be in signature or a separate field
                self.assertIn('MetaClass', str(class_stub))
            finally:
                os.unlink(f.name)

    def test_serialization_to_json(self):
        """
        GIVEN a temporary file with various functions and classes
        WHEN extract_function_stubs is called with markdown_path
        THEN expect a JSON file to be created alongside the markdown file
        AND expect the JSON to contain all extracted stubs in serializable format
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
@dataclass
class Person:
    """A person class."""
    name: str
    age: int

    def greet(self) -> str:
        """Greet someone."""
        return f"Hello, I'm {self.name}"

async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    pass

def calculate(x: int, y: int = 5) -> int:
    """Calculate sum."""
    return x + y
''')
            f.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md_file:
                try:
                    result = extract_function_stubs(f.name, md_file.name)
                    
                    # Verify stubs were extracted
                    self.assertIsInstance(result, list)
                    self.assertGreater(len(result), 0)
                    
                    # Check JSON file was created
                    json_path = md_file.name.replace('.md', '.json')
                    self.assertTrue(os.path.exists(json_path))
                    
                    # Load and verify JSON content
                    with open(json_path, 'r', encoding='utf-8') as json_file:
                        json_data = json.load(json_file)
                    
                    self.assertIsInstance(json_data, list)
                    self.assertEqual(len(json_data), len(result))
                    
                    # Verify all expected items are in JSON
                    names = [item['name'] for item in json_data]
                    expected_names = ['Person', 'greet', 'fetch_data', 'calculate']
                    
                    for expected_name in expected_names:
                        self.assertIn(expected_name, names)
                    
                    # Verify structure of JSON entries
                    for item in json_data:
                        self.assertIn('name', item)
                        self.assertIn('signature', item)
                        self.assertIn('is_async', item)
                        self.assertIn('is_method', item)
                        self.assertIn('decorators', item)
                        self.assertIn('class_name', item)
                        # docstring can be None
                        self.assertIn('docstring', item)
                    
                    # Clean up JSON file
                    os.unlink(json_path)
                    
                finally:
                    os.unlink(f.name)
                    os.unlink(md_file.name)


if __name__ == '__main__':
    unittest.main()
