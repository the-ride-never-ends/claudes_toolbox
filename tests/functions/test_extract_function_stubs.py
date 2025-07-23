
"""
Test suite for extract_function_stubs function.

Docstring:
=================
Extract function stubs from Python files and write them to markdown files.
    
Parses Python files to identify all callable definitions (functions, async functions, 
and classes) and extracts their signatures, type hints, and docstrings. The extracted
information is then written to markdown files for documentation purposes.

If a directory is provided, all Python files in the directory will be processed.
If a file is provided, only that file will be processed.

Args:
    path (str): Path to the Python file or directory to analyze.
    output_dir (str): The output destination for markdown files. Behavior depends on the input:
        - If `path` is a file and `output_dir` ends with '.md': writes to that specific file
        - If `path` is a file and `output_dir` is a directory: writes '{filename}_stubs.md' in that directory
        - If `path` is a directory and `output_dir` ends with '.md': writes all stubs to that single file
        - If `path` is a directory and `output_dir` is a directory: writes individual '{filename}_stubs.md' files
    recursive (bool): If True and path is a directory, search subdirectories
        recursively for Python files. Ignored if path is a file. Defaults to True.

Returns:
    str: A status message indicating the number of files processed successfully,
            or "No files were written." if no files were processed.

    Each output file contains:
        - 'name' (str): The function/class name
        - 'signature' (str): Complete function signature with type hints
        - 'docstring' (Optional[str]): The function's docstring if present
        - 'is_async' (bool): Whether the function is an async function
        - 'is_method' (bool): Whether the function is a class method
        - 'decorators' (list[str]): List of decorator names as strings
        - 'class_name' (Optional[str]): Name of containing class if is_method is True
        - 'file_path' (str): Path to the file containing this function/class

Raises:
    FileNotFoundError: If the specified file or directory does not exist.
    PermissionError: If files cannot be read due to permission issues.
    ValueError: If path is empty or invalid.
    OSError: If there are other file system related errors.

Example:
    >>> # Extract from a single file to a specific markdown file
    >>> result = extract_function_stubs('my_module.py', 'output.md')
    >>> print(result)
    'Wrote 1 file(s) successfully.'
    
    >>> # Extract from a directory to individual markdown files
    >>> result = extract_function_stubs('./src/', './docs/', recursive=True)
    >>> print(result)
    'Wrote 5 file(s) successfully.'
    
    >>> # Extract from a directory to a single combined markdown file
    >>> result = extract_function_stubs('./src/', './docs/all_stubs.md', recursive=False)
    >>> print(result)
    'Wrote 3 file(s) successfully.'
"""
import unittest
import tempfile
import os
import json
from tools.functions.extract_function_stubs import extract_function_stubs


def _file_without_extension(file_path):
    """
    Helper method to get the file name without extension.
    """
    return os.path.splitext(os.path.basename(file_path))[0]


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality of extract_function_stubs."""

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

    def test_simple_function_with_type_hints_and_docstring(self):
        """
        GIVEN a temporary file with:
            def add_numbers(a: int, b: int) -> int:
                \"\"\"Add two numbers together.\"\"\"
                return a + b
        WHEN extract_function_stubs is called with output_dir
        THEN expect status message "Wrote 1 file(s) successfully."
        AND expect markdown file to be created with function stub
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
''')
            f.flush()

            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                # Check return value is status message
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains the function
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('add_numbers', content)
                    self.assertIn('Add two numbers together', content)
                    self.assertIn('a: int, b: int) -> int', content)
                    
            finally:
                os.unlink(f.name)

    def test_file_with_multiple_functions(self):
        """
        GIVEN a temporary file with:
            def func1(): pass
            def func2(): pass
            def func3(): pass
        WHEN extract_function_stubs is called with output_dir
        THEN expect status message "Wrote 1 file(s) successfully."
        AND expect markdown file to contain all 3 functions
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def func1(): pass
def func2(): pass
def func3(): pass
''')
            f.flush()
            print(f.name)
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func1', content)
                    self.assertIn('func2', content)
                    self.assertIn('func3', content)
            finally:
                os.unlink(f.name)
    
    def test_functions_with_no_type_hints(self):
        """
        GIVEN a temporary file with:
            def no_hints(a, b):
                return a + b
        WHEN extract_function_stubs is called with output_dir
        THEN expect status message "Wrote 1 file(s) successfully."
        AND expect markdown file to contain function without type annotations
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def no_hints(a, b):
    return a + b
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('no_hints', content)
                    self.assertIn('(a, b)', content)
                    self.assertNotIn(':', content.split('no_hints')[1].split('\n')[0])  # No type annotations in signature line
            finally:
                os.unlink(f.name)
    
    def test_functions_with_no_docstrings(self):
        """
        GIVEN a temporary file with:
            def no_docstring():
                pass
        WHEN extract_function_stubs is called with output_dir
        THEN expect status message "Wrote 1 file(s) successfully."
        AND expect markdown file to contain function with no docstring section
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def no_docstring():
    pass
''')
            f.flush()

            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('no_docstring', content)
            finally:
                os.unlink(f.name)
    
    def test_functions_with_both_type_hints_and_docstrings(self):
        """
        GIVEN a temporary file with:
            def complete_func(x: str) -> str:
                \"\"\"Returns the input string.\"\"\"
                return x
        WHEN extract_function_stubs is called with output_dir
        THEN expect status message "Wrote 1 file(s) successfully."
        AND expect markdown file to contain function with all information
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def complete_func(x: str) -> str:
    """Returns the input string."""
    return x
''')
            f.flush()

            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('complete_func', content)
                    self.assertIn('x: str) -> str', content)
                    self.assertIn('Returns the input string', content)
            finally:
                os.unlink(f.name)


class TestFunctionSignatureVariations(unittest.TestCase):
    """Test various function signature patterns."""
    
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

    def test_functions_with_no_parameters(self):
        """
        GIVEN a temporary file with:
            def no_params() -> None:
                pass
        WHEN extract_function_stubs is called
        THEN expect signature to be "() -> None"
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def no_params() -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('() -> None', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def pos_only(a, b, c):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('(a, b, c)', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def with_defaults(a: int, b: str = "default", c: bool = True):
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('b: str = "default"', content)
                    self.assertIn('c: bool = True', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''from typing import Any

def variadic(a: int, *args: str, **kwargs: Any) -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('*args: str', content)
                    self.assertIn('**kwargs: Any', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''from typing import Union, Optional, List, Dict

def complex_types(x: Union[int, str], y: Optional[List[Dict[str, int]]]) -> None:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('Union[int, str]', content)
                    self.assertIn('Optional[List[Dict[str, int]]]', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def returns_int() -> int:
    return 42
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()

                    self.assertIn('-> int', content)
            finally:
                os.unlink(f.name)


class TestClassAndMethodTests(unittest.TestCase):
    """Test detection of class methods vs standalone functions."""
    
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def standalone():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()

                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class MyClass:
    def instance_method(self, x: int) -> str:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both class and method
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('MyClass', content)
                    self.assertIn('instance_method', content)
                    self.assertIn('self, x: int', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class MyClass:
    @staticmethod
    def static_method(x: int) -> int:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                

                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both class and method
                with open(expected_file, 'r') as md_file:

                    content = md_file.read()

                # Find the static method stub by name
                self.assertIn('@staticmethod', content)
                self.assertIn('class MyClass', content)
                self.assertIn('def static_method', content)
                self.assertIn("* **Method:** False", content)
                self.assertIn('x: int', content)
                self.assertNotIn('self', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class MyClass:
    @classmethod
    def class_method(cls, x: int) -> int:
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that the markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('@classmethod', content)
                self.assertIn('MyClass', content)
                self.assertIn('cls, x: int', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class MyClass:
    @property
    def my_property(self) -> str:
        return "value"
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                # Properties might be included or excluded - test for either behavior
                if len(result) == 2:
                    # Find the property stub by name
                    property_stub = next(s for s in result if s['name'] == 'my_property')
                    self.assertEqual(property_stub['name'], 'my_property')
                    self.assertTrue(property_stub['is_method'])
                    self.assertEqual(property_stub['class_name'], 'MyClass')
                else:
                    self.assertEqual(result, "Wrote 1 file(s) successfully.")  # Just the class
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class Outer:
    class Inner:
        def inner_method(self):
            pass
    def outer_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that the markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('inner_method', content)
                self.assertIn('outer_method', content)
                self.assertIn('class Inner', content)
                self.assertIn('class Outer', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class Parent:
    def parent_method(self):
        pass

class Child(Parent):
    def child_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that the markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('parent_method', content)
                self.assertIn('child_method', content)
                self.assertIn('Parent', content)
                self.assertIn('Child', content)
            finally:
                os.unlink(f.name)


class TestAsyncFunctionTests(unittest.TestCase):
    """Test detection of async vs synchronous functions."""
    
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



    def test_regular_synchronous_functions(self):
        """
        GIVEN a temporary file with:
            def sync_func():
                pass
        WHEN extract_function_stubs is called
        THEN expect is_async = False
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def sync_func():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(
                    os.path.exists(expected_output_file), 
                    msg=f"""
                    Expected output file not found at '{expected_output_file}'
                    Python files in the test directory: {os.listdir(self.test_dir_path)}
                    """.strip()
                )
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('sync_func', content)
                self.assertIn('* **Async:** False', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''async def async_func():
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('async_func', content)
                self.assertIn('async def', content)
                self.assertIn('* **Async:** True', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class MyClass:
    async def async_method(self):
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('async_method', content)
                self.assertIn('MyClass', content)
                self.assertIn('async def', content)
                self.assertIn('* **Async:** True', content)
                self.assertIn('* **Method:** True', content)
            finally:
                os.unlink(f.name)


class TestDirectoryFunctionality(unittest.TestCase):
    """Test directory handling functionality."""

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



    def test_directory_with_single_python_file(self):
        """
        GIVEN a directory with one Python file containing functions
        WHEN extract_function_stubs is called on the directory
        THEN expect functions from that file to be extracted
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file in the directory
            python_file = os.path.join(self.test_dir_path, 'test_module.py')
            with open(python_file, 'w') as f:
                f.write('''def func1():
    """First function."""
    pass

def func2():
    """Second function."""
    pass
''')
            
            result = extract_function_stubs(self.test_dir_path, self.test_dir_path)
            
            self.assertEqual(result, "Wrote 1 file(s) successfully.")
            
            # Check that markdown file(s) were created
            found_stub_files = []
            for filename in os.listdir(self.test_dir_path):
                if filename.endswith('_stubs.md'):
                    found_stub_files.append(filename)
            
            self.assertTrue(len(found_stub_files) > 0)
            
            # Read one of the markdown files to verify content
            with open(os.path.join(self.test_dir_path, found_stub_files[0]), 'r') as f:
                content = f.read()
                self.assertTrue('func1' in content or 'func2' in content)
    
    def test_directory_with_multiple_python_files(self):
        """
        GIVEN a directory with multiple Python files
        WHEN extract_function_stubs is called on the directory  
        THEN expect functions from all files to be extracted
        """
        # Create first Python file
        file1 = os.path.join(self.test_dir_path, 'module1.py')
        with open(file1, 'w') as f:
            f.write('''
def func_from_file1():
    pass
''')
        
        # Create second Python file
        file2 = os.path.join(self.test_dir_path, 'module2.py')
        with open(file2, 'w') as f:
            f.write('''
def func_from_file2():
    pass
''')
        
        result = extract_function_stubs(self.test_dir_path, self.test_dir_path)
        
        self.assertEqual(result, "Wrote 2 file(s) successfully.")
        
        # Check that markdown file(s) were created
        found_stub_files = []
        for filename in os.listdir(self.test_dir_path):
            if filename.endswith('_stubs.md'):
                found_stub_files.append(filename)
        
        self.assertTrue(len(found_stub_files) >= 2)
        
        # Read all markdown files to verify both functions are present
        all_content = ""
        for stub_file in found_stub_files:
            with open(os.path.join(self.test_dir_path, stub_file), 'r') as f:
                all_content += f.read()
        
        self.assertIn('func_from_file1', all_content)
        self.assertIn('func_from_file2', all_content)
    
    def test_directory_with_subdirectories_recursive_true(self):
        """
        GIVEN a directory with subdirectories containing Python files
        WHEN extract_function_stubs is called with recursive=True
        THEN expect functions from all files including subdirectories
        """
        # Create file in root directory
        root_file = os.path.join(self.test_dir_path, 'root.py')
        with open(root_file, 'w') as f:
            f.write('''
def root_func():
    pass
''')
        
        # Create subdirectory with file
        subdir = os.path.join(self.test_dir_path, 'subdir')
        os.makedirs(subdir)
        sub_file = os.path.join(subdir, 'sub.py')
        with open(sub_file, 'w') as f:
            f.write('''
def sub_func():
    pass
''')
        
        result = extract_function_stubs(self.test_dir_path, self.test_dir_path, recursive=True)
        
        self.assertEqual(result, "Wrote 2 file(s) successfully.")
        
        # Check that markdown files were created for both directories
        found_stub_files = 0
        for filename in os.listdir(self.test_dir_path):
            if filename.endswith('_stubs.md'):
                found_stub_files += 1
        self.assertGreaterEqual(found_stub_files, 1)

    def test_directory_with_subdirectories_recursive_false(self):
        """
        GIVEN a directory with subdirectories containing Python files
        WHEN extract_function_stubs is called with recursive=False
        THEN expect functions only from root directory files
        """
        # Create file in root directory
        root_file = os.path.join(self.test_dir_path, 'root.py')
        with open(root_file, 'w') as f:
            f.write('''def root_func():
    pass
''')
        
        # Create subdirectory with file
        subdir = os.path.join(self.test_dir_path, 'subdir')
        os.makedirs(subdir)
        sub_file = os.path.join(subdir, 'sub.py')
        with open(sub_file, 'w') as f:
            f.write('''def sub_func():
    pass
''')
        
        result = extract_function_stubs(self.test_dir_path, self.test_dir_path, recursive=False)
        
        self.assertEqual(result, "Wrote 1 file(s) successfully.")
        
        # Check that only root-level markdown file was created (not recursive)
        found_stub_files = 0
        for filename in os.listdir(self.test_dir_path):
            if filename.endswith('_stubs.md'):
                found_stub_files += 1
        self.assertGreaterEqual(found_stub_files, 1)
    
    def test_directory_with_no_python_files(self):
        """
        GIVEN a directory with no Python files
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        # Create some non-Python files
        with open(os.path.join(self.test_dir_path, 'readme.txt'), 'w') as f:
            f.write('This is not Python')
        
        result = extract_function_stubs(self.test_dir_path, self.test_dir_path)
        
        self.assertEqual(result, "No files were written.")
    
    def test_directory_with_mixed_file_types(self):
        """
        GIVEN a directory with Python files and other file types
        WHEN extract_function_stubs is called
        THEN expect only Python files to be processed
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Python file
            python_file = os.path.join(self.test_dir_path, 'module.py')
            with open(python_file, 'w') as f:
                f.write('''def python_func():
    pass
''')
            
            # Create non-Python files
            with open(os.path.join(self.test_dir_path, 'readme.txt'), 'w') as f:
                f.write('Not Python')
            with open(os.path.join(self.test_dir_path, 'data.json'), 'w') as f:
                f.write('{"not": "python"}')
            
            result = extract_function_stubs(self.test_dir_path, self.test_dir_path)
            
            self.assertEqual(result, "Wrote 1 file(s) successfully.")
            
            # Check that markdown files were created - just check one exists
            found_stub_file = False
            for filename in os.listdir(self.test_dir_path):
                if filename.endswith('_stubs.md'):
                    found_stub_file = True
                    break
            self.assertTrue(found_stub_file)
    
    def test_directory_with_syntax_error_files(self):
        """
        GIVEN a directory with one valid Python file and one with syntax errors
        WHEN extract_function_stubs is called
        THEN expect functions from valid file to be extracted, invalid file to be skipped
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create valid Python file
            valid_file = os.path.join(self.test_dir_path, 'valid.py')
            with open(valid_file, 'w') as f:
                f.write('''def valid_func():
    pass
''')
            
            # Create invalid Python file
            invalid_file = os.path.join(self.test_dir_path, 'invalid.py')
            with open(invalid_file, 'w') as f:
                f.write('''def broken_syntax(
    # Missing closing parenthesis
''')
            
            result = extract_function_stubs(self.test_dir_path, self.test_dir_path)
            
            self.assertEqual(result, "Wrote 1 file(s) successfully.")
            
            # Check that a valid stub file was created
            found_valid_stub = False
            for filename in os.listdir(self.test_dir_path):
                if filename.endswith('_stubs.md'):
                    with open(os.path.join(self.test_dir_path, filename), 'r') as f:
                        content = f.read()
                        if 'valid_func' in content:
                            found_valid_stub = True
                            break
            self.assertTrue(found_valid_stub)


class TestDirectoryMarkdownOutput(unittest.TestCase):
    """Test markdown output for directory processing."""

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()


    def test_directory_markdown_output_multiple_files(self):
        """
        GIVEN a directory with multiple Python files
        WHEN extract_function_stubs is called with markdown_path
        THEN expect markdown file to be created with functions from all files
        """
        # Create multiple Python files
        file1 = os.path.join(self.test_dir_path, 'module1.py')
        with open(file1, 'w') as f:
            f.write('''
def func1():
    """Function from file 1."""
    pass
''')

        file2 = os.path.join(self.test_dir_path, 'module2.py')
        with open(file2, 'w') as f:
            f.write('''
def func2():
    """Function from file 2."""
    pass
''')
        # Create markdown output file
        md_file = os.path.join(self.test_dir_path, 'output.md')
        
        result = extract_function_stubs(self.test_dir_path, md_file)
        
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
    
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



    def test_empty_python_file(self):
        """
        GIVEN an empty file with no content
        WHEN extract_function_stubs is called
        THEN expect empty list returned
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "No files were written.")
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
# This is a comment
# Another comment
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "No files were written.")
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
import os
from typing import Any
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "No files were written.")
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
def broken_syntax(
    # Missing closing parenthesis and colon
''')
            f.flush()
            
            try:
                with self.assertRaises(SyntaxError):
                    result = extract_function_stubs(f.name, self.test_dir_path)
            finally:
                os.unlink(f.name)
    
    def test_empty_string_as_file_path(self):
        """
        GIVEN file_path = ""
        WHEN extract_function_stubs is called
        THEN expect ValueError to be raised
        """
        with self.assertRaises(ValueError):
            extract_function_stubs('', self.test_dir_path)
    
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
                    result = extract_function_stubs(f.name, self.test_dir_path)

                    self.assertEqual(result, "Wrote 1 file(s) successfully.")
                    
                    # Check that markdown file was created
                    expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                    self.assertTrue(os.path.exists(expected_file))
                    
                    # Verify content contains function with decorator
                    with open(expected_file, 'r') as md_file:
                        content = md_file.read()
                        self.assertIn('def valid_python', content)

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def test_func():
    pass
''')
            f.flush()
            
            try:
                # Set file to write-only (no read permissions)
                os.chmod(f.name, 0o200)
                
                with self.assertRaises(PermissionError):
                    extract_function_stubs(f.name, self.test_dir_path)
            finally:
                # Restore permissions to delete the file
                os.chmod(f.name, 0o600)
                os.unlink(f.name)


class TestDocstringVariations(unittest.TestCase):
    """Test handling of different docstring formats."""

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

    def test_single_line_docstrings(self):
        """
        GIVEN a file with:
            def func():
                \"\"\"Single line docstring.\"\"\"
                pass
        WHEN extract_function_stubs is called
        THEN expect docstring = "Single line docstring."
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def func():
                """Single line docstring."""
                pass
            ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with single line docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    self.assertIn('Single line docstring.', content)
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def func():
                """
                Multi-line docstring
                with multiple lines.
                """
                pass
            ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with multi-line docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    self.assertIn('Multi-line docstring', content)
                    self.assertIn('with multiple lines.', content)
            finally:
                os.unlink(f.name)

    def test_google_style_docstrings(self):
        """
        GIVEN a file with Google-style docstring including Args, Returns, Raises sections
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured with formatting preserved
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with Google-style docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    self.assertIn('Args:', content)
                    self.assertIn('Returns:', content)
                    self.assertIn('Raises:', content)
                    self.assertIn('Short description.', content)
                    self.assertIn('Input number.', content)
                    self.assertIn('Output number incremented by 1.', content)
                    self.assertIn('If input is negative.', content)
            finally:
                os.unlink(f.name)

    def test_numpy_style_docstrings(self):
        """
        GIVEN a file with NumPy-style docstring using Parameters, Returns sections
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with NumPy-style docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    self.assertIn('Parameters', content)
                    self.assertIn('Returns', content)
                    self.assertIn('Short description.', content)
                    self.assertIn('Input number.', content)
                    self.assertIn('Output number incremented by 1.', content)
            finally:
                os.unlink(f.name)

    def test_sphinx_style_docstrings(self):
        """
        GIVEN a file with Sphinx-style docstring using :param: and :returns: syntax
        WHEN extract_function_stubs is called
        THEN expect complete docstring to be captured
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with Sphinx-style docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    self.assertIn(':param a:', content)
                    self.assertIn(':returns:', content)
                    self.assertIn('Short description.', content)
                    self.assertIn('Input number.', content)
                    self.assertIn('Output number incremented by 1.', content)
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def func():
                x = 1
                return x
            ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with no docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func', content)
                    # Check that no docstring section appears
                    self.assertNotIn('**Docstring:**', content)
            finally:
                os.unlink(f.name)


class TestComplexPythonConstructs(unittest.TestCase):
    """Test handling of complex Python language constructs."""


    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
@decorator
@another_decorator(param='value')
def decorated_func():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with decorator
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('decorated_func', content)
                    self.assertIn('@decorator', content)
                    self.assertIn('@another_decorator', content)
            finally:
                os.unlink(f.name)

    def test_lambda_functions(self):
        """
        GIVEN a file with:
            my_lambda = lambda x: x + 1
        WHEN extract_function_stubs is called
        THEN expect lambda to be ignored (no stubs extracted)
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''my_lambda = lambda x: x + 1
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                # Lambda functions should be ignored (not extracted as stubs)
                self.assertEqual(result, "No files were written.")
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''def outer():
    def inner():
        pass
    return inner
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)

                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with decorator
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('def outer', content)
                    self.assertIn('def inner', content)
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''try:
    def func_in_try():
        pass
except:
    def func_in_except():
        pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both functions
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('func_in_try', content)
                    self.assertIn('func_in_except', content)
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''from typing import TypeVar
T = TypeVar('T')

def generic_func(x: T) -> T:
    return x
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that the markdown file was created
                expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_output_file))
                
                # Read and check the markdown content
                with open(expected_output_file, 'r') as output_f:
                    content = output_f.read()
                
                self.assertIn('x: T', content)
                self.assertIn('-> T', content)
            finally:
                os.unlink(f.name)


class TestOutputValidation(unittest.TestCase):
    """Test validation of output format and content."""

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

    def test_all_expected_keys_are_present(self):
        """
        GIVEN any valid function stub result
        WHEN examining the dictionary
        THEN expect keys: ['name', 'signature', 'docstring', 'is_async', 'is_method', 'decorators', 'class_name', 'file_path']
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
def another_func():
    pass
            ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Read and verify the content structure
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Verify the function is present
                    self.assertIn('another_func', content)
                    
                    # Verify expected markdown structure elements are present
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
async def async_func():
    """An async function."""
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Read and verify the content structure
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Verify the function is present
                    self.assertIn('async_func', content)
                    self.assertIn('An async function.', content)
                    self.assertIn('async def', content)
                    
                    # Verify metadata fields are present with correct types
                    self.assertIn('* **Async:** True', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
            finally:
                os.unlink(f.name)

    def test_is_method_flag_correctly_set(self):
        """
        GIVEN files with both standalone functions and class methods
        WHEN extract_function_stubs is called
        THEN expect is_method = True only for class methods, False for standalone functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
def standalone():
    pass

class MyClass:
    def method(self):
        pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both function and method with correct is_method flags
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check that both standalone function and method are present
                    self.assertIn('standalone', content)
                    self.assertIn('method', content)
                    
                    # Check is_method flags
                    self.assertIn('* **Method:** False', content)  # For standalone function
                    self.assertIn('* **Method:** True', content)   # For class method
            finally:
                os.unlink(f.name)

    def test_class_name_correctly_populated(self):
        """
        GIVEN class methods
        WHEN extract_function_stubs is called
        THEN expect class_name to match the containing class name exactly
        AND expect class_name = None for standalone functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
class MyClass:
    def method(self):
        pass

def standalone():
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both function and class with correct class associations
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check that both method and standalone function are present
                    self.assertIn('method', content)
                    self.assertIn('standalone', content)
                    
                    # Check class name associations
                    self.assertIn('**Class:** MyClass', content)
                    self.assertIn('**Class:** N/A', content)
            finally:
                os.unlink(f.name)

    def test_is_async_flag_correctly_set(self):
        """
        GIVEN mix of async and sync functions
        WHEN extract_function_stubs is called
        THEN expect is_async = True only for async functions
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
async def async_func():
    pass

def sync_func():
    pass
            ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both functions with correct async flags
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check that both functions are present
                    self.assertIn('async_func', content)
                    self.assertIn('sync_func', content)
                    
                    # Check async function is marked as async
                    self.assertIn('async def async_func', content)
                    self.assertIn('* **Async:** True', content)
                    
                    # Check sync function is marked as not async
                    self.assertIn('def sync_func', content) 
                    self.assertIn('* **Async:** False', content)
            finally:
                os.unlink(f.name)

    def test_if_decorators_are_detected(self):
        """
        GIVEN a file with decorated functions
        WHEN extract_function_stubs is called
        THEN expect decorators to be captured in the 'decorators' field
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
@my_decorator
def decorated_func():
    pass
    ''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains function with decorator
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('decorated_func', content)
                    self.assertIn('@my_decorator', content)
            finally:
                os.unlink(f.name)


class TestRealWorldScenarios(unittest.TestCase):
    """Test with real-world Python files and complex scenarios."""


    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()


    def test_actual_python_standard_library_modules(self):
        """
        GIVEN a standard library file like "/usr/lib/python3.x/json/__init__.py"
        WHEN extract_function_stubs is called
        THEN expect reasonable number of functions detected without errors
        AND expect all public functions to be found
        """
        import json
        json_path = json.__file__

        result = extract_function_stubs(json_path, self.test_dir_path)

        self.assertEqual(result, "Wrote 1 file(s) successfully.")
        
        # Check that the markdown file was created
        expected_output_file = os.path.join(self.test_dir_path, f"{_file_without_extension(json_path)}_stubs.md")
        print(f"Expected output file: {expected_output_file}")
        print(f"Files in test directory: {os.listdir(self.test_dir_path)}")
        self.assertTrue(os.path.exists(expected_output_file))
        
        # Read and check the markdown content
        with open(expected_output_file, 'r') as output_f:
            content = output_f.read()
            
            self.assertIn('def load', content)
            self.assertIn('def loads', content)
            self.assertIn('def dump', content)
            self.assertIn('def dumps', content)

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
            result = extract_function_stubs(unittest_path, self.test_dir_path)
            self.assertEqual(result, "Wrote 1 file(s) successfully.")
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
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains all classes and methods
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check for classes
                    self.assertIn('ClassA', content)
                    self.assertIn('ClassB', content)
                    
                    # Check for methods
                    self.assertIn('method1', content)
                    self.assertIn('method2', content)
                    self.assertIn('method3', content)
                    self.assertIn('method4', content)
                    
                    # Check that methods are correctly associated with classes
                    self.assertIn('**Class:** ClassA', content)
                    self.assertIn('**Class:** ClassB', content)
            finally:
                os.unlink(f.name)

    def test_presence_in_markdown(self):
        """
        GIVEN a file with various function types and a markdown output path
        WHEN extract_function_stubs is called with markdown_path parameter
        THEN expect all functions to be present in the markdown output with correct formatting
        """
        with tempfile.NamedTemporaryFile('w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                    self.assertEqual(result, "Wrote 1 file(s) successfully.")
                    
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
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class SimpleClass:
    """A simple class with a single line docstring."""
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('SimpleClass', content)
                    self.assertIn('A simple class with a single line docstring.', content)
                    self.assertIn('class SimpleClass', content)
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with multiline docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('ComplexClass', content)
                    self.assertIn('A complex class', content)
                    self.assertIn('Attributes:', content)
                    self.assertIn('attr1 (int): First attribute', content)
                    self.assertIn('attr2 (str): Second attribute', content)
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class NoDocClass:
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class without docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('NoDocClass', content)
                    self.assertIn('class NoDocClass', content)
                    self.assertNotIn('**Docstring:**', content)
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''class DocumentedClass:
    """Class-level documentation."""
    
    def method1(self):
        """Method-level documentation."""
        pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both class and method
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('DocumentedClass', content)
                    self.assertIn('Class-level documentation.', content)
                    self.assertIn('method1', content)
                    self.assertIn('Method-level documentation.', content)
            finally:
                os.unlink(f.name)


class TestClassDecorators(unittest.TestCase):
    """Test extraction of classes with decorators."""
    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''@dataclass
class DataClass:
    name: str
    age: int
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with decorator
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('DataClass', content)
                    self.assertIn('@dataclass', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
@decorator1
@decorator2(arg="value")
@decorator3
class MultiDecoratedClass:
    pass
            ''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with all decorators
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('MultiDecoratedClass', content)
                    self.assertIn('@decorator1', content)
                    self.assertIn('@decorator2(arg="value")', content)
                    self.assertIn('@decorator3', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''@singleton
class SingletonClass:
    """A singleton implementation."""
    pass
''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")

                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with decorator and docstring
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('SingletonClass', content)
                    self.assertIn('@singleton', content)
                    self.assertIn('A singleton implementation.', content)
                    self.assertIn('**Async:** False', content)
                    self.assertIn('**Method:** False', content)
                    self.assertIn('**Class:** N/A', content)

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both function and class with decorators
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('decorated_func', content)
                    self.assertIn('DecoratedClass', content)
                    self.assertIn('@function_decorator', content)
                    self.assertIn('@class_decorator', content)
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

    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()



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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
class ChildClass(ParentClass):
    pass
''')
            f.flush()
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with inheritance
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('ChildClass', content)
                    self.assertIn('ParentClass', content)
                    self.assertIn('class ChildClass(ParentClass)', content)
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
class MultiChild(Parent1, Parent2, Parent3):
    pass
            ''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with multiple inheritance
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('MultiChild', content)
                    self.assertIn('Parent1', content)
                    self.assertIn('Parent2', content)
                    self.assertIn('Parent3', content)
                    self.assertIn('class MultiChild(Parent1, Parent2, Parent3)', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
class CustomList(list):
    pass

class CustomDict(dict):
    pass

class CustomException(Exception):
    pass
            ''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains all classes with builtin inheritance
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('CustomList', content)
                    self.assertIn('CustomDict', content)
                    self.assertIn('CustomException', content)
                    self.assertIn('class CustomList(list)', content)
                    self.assertIn('class CustomDict(dict)', content)
                    self.assertIn('class CustomException(Exception)', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
from typing import Generic, TypeVar

T = TypeVar('T')

class GenericClass(Generic[T]):
    pass

class SpecificClass(GenericClass[str]):
    pass
            ''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both classes with generic inheritance
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    self.assertIn('GenericClass', content)
                    self.assertIn('SpecificClass', content)
                    self.assertIn('Generic[T]', content)
                    self.assertIn('GenericClass[str]', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
@dataclass
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class with all features
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check class name and decorator
                    self.assertIn('CompleteClass', content)
                    self.assertIn('@dataclass', content)
                    
                    # Check inheritance
                    self.assertIn('BaseClass', content)
                    self.assertIn('Interface1', content)
                    self.assertIn('Interface2', content)
                    self.assertIn('class CompleteClass(BaseClass, Interface1, Interface2)', content)
                    
                    # Check docstring
                    self.assertIn('A complete class with everything', content)
                    self.assertIn('This demonstrates inheritance', content)
                    
                    # Check metadata
                    self.assertIn('* **Async:** False', content)
                    self.assertIn('* **Method:** False', content)
                    self.assertIn('* **Class:** N/A', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
            f.write('''
class OuterClass:
    class InnerBase:
        pass
    
    class InnerChild(InnerBase):
        pass
            ''')
            f.flush()
            
            try:
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains all classes with correct inheritance
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check all classes are present
                    self.assertIn('OuterClass', content)
                    self.assertIn('InnerBase', content)
                    self.assertIn('InnerChild', content)
                    
                    # Check OuterClass has no inheritance
                    self.assertIn('class OuterClass', content)
                    
                    # Check InnerChild inherits from InnerBase
                    self.assertIn('class InnerChild(InnerBase)', content)
                    
                    # Check that inner classes appear in nested context
                    self.assertIn('class InnerBase', content)
            finally:
                os.unlink(f.name)


class TestClassExtractionComplexScenarios(unittest.TestCase):
    """Test complex combinations of class features."""


    def setUp(self):
        """Set up a temporary directory for test output."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_dir_path = self.test_dir.name

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.test_dir.cleanup()


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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains class and method with decorators
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check class with decorator, inheritance, and docstring
                    self.assertIn('AbstractBase', content)
                    self.assertIn('@dataclass', content)
                    self.assertIn('class AbstractBase(ABC)', content)
                    self.assertIn('Abstract base class.', content)
                    
                    # Check method with decorator and docstring
                    self.assertIn('required_method', content)
                    self.assertIn('@abstractmethod', content)
                    self.assertIn('Must be implemented by subclasses.', content)
                    self.assertIn('* **Method:** True', content)
                    self.assertIn('* **Class:** AbstractBase', content)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
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
                result = extract_function_stubs(f.name, self.test_dir_path)
                self.assertEqual(result, "Wrote 1 file(s) successfully.")
                
                # Check that markdown file was created
                expected_file = os.path.join(self.test_dir_path, f"{_file_without_extension(f.name)}_stubs.md")
                self.assertTrue(os.path.exists(expected_file))
                
                # Verify content contains both classes with correct features
                with open(expected_file, 'r') as md_file:
                    content = md_file.read()
                    
                    # Check MetaClass inherits from type
                    self.assertIn('MetaClass', content)
                    self.assertIn('class MetaClass(type)', content)
                    self.assertIn('A metaclass.', content)
                    
                    # Check ClassWithMeta has metaclass info
                    self.assertIn('ClassWithMeta', content)
                    self.assertIn('A class using a metaclass.', content)
                    self.assertIn('metaclass=MetaClass', content)
            finally:
                os.unlink(f.name)

# NOTE Keep this commented out as JSON serialization/output may be added in the future.
#     def test_serialization_to_json(self):
#         """
#         GIVEN a temporary file with various functions and classes
#         WHEN extract_function_stubs is called with markdown_path
#         THEN expect a JSON file to be created alongside the markdown file
#         AND expect the JSON to contain all extracted stubs in serializable format
#         """
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.test_dir_path, delete=False) as f:
#             f.write('''
# @dataclass
# class Person:
#     """A person class."""
#     name: str
#     age: int

#     def greet(self) -> str:
#         """Greet someone."""
#         return f"Hello, I'm {self.name}"

# async def fetch_data(url: str) -> dict:
#     """Fetch data from URL."""
#     pass

# def calculate(x: int, y: int = 5) -> int:
#     """Calculate sum."""
#     return x + y
# ''')
#             f.flush()
            
#             with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as md_file:
#                 try:
#                     result = extract_function_stubs(f.name, md_file.name)
                    
#                     # Verify stubs were extracted
#                     self.assertIsInstance(result, list)
#                     self.assertGreater(len(result), 0)
                    
#                     # Check JSON file was created
#                     json_path = md_file.name.replace('.md', '.json')
#                     self.assertTrue(os.path.exists(json_path))
                    
#                     # Load and verify JSON content
#                     with open(json_path, 'r', encoding='utf-8') as json_file:
#                         json_data = json.load(json_file)
                    
#                     self.assertIsInstance(json_data, list)
#                     self.assertEqual(len(json_data), len(result))
                    
#                     # Verify all expected items are in JSON
#                     names = [item['name'] for item in json_data]
#                     expected_names = ['Person', 'greet', 'fetch_data', 'calculate']
                    
#                     for expected_name in expected_names:
#                         self.assertIn(expected_name, names)
                    
#                     # Verify structure of JSON entries
#                     for item in json_data:
#                         self.assertIn('name', item)
#                         self.assertIn('signature', item)
#                         self.assertIn('is_async', item)
#                         self.assertIn('is_method', item)
#                         self.assertIn('decorators', item)
#                         self.assertIn('class_name', item)
#                         # docstring can be None
#                         self.assertIn('docstring', item)
                    
#                     # Clean up JSON file
#                     os.unlink(json_path)
                    
#                 finally:
#                     os.unlink(f.name)
#                     os.unlink(md_file.name)


if __name__ == '__main__':
    unittest.main()
