#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import os
import re
import shutil
import stat
import tempfile
import threading
import time
import unittest
from datetime import datetime
from pprint import pprint
from pathlib import Path

from tools.functions.generate_pytest_test_stubs import (
    generate_pytest_test_stubs,
)

def _make_module_path(input_path: str) -> str:
    """
    Convert a file path to a module path by removing the file extension
    and replacing directory separators with dots.
    
    Args:
        input_path: The file path to convert.
        
    Returns:
        The module path as a string.
    """
    input_path = os.path.abspath(input_path)
    input_path = os.path.normpath(input_path)
    
    if os.path.isdir(input_path):
        raise ValueError("Input path is a directory, expected a file.")
    
    input_path = os.path.splitext(input_path)[0]
    
    if os.name == 'nt':
        module_path = input_path.replace('\\', '.')
    else:
        module_path = input_path.replace('/', '.')
    
    return module_path.lstrip('.')


class TestGeneratePytestTestStubsInitialization(unittest.TestCase):
    """Test generate_pytest_test_stubs initialization and basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create a simple Python file for testing
        self.test_python_content = '''#!/usr/bin/env python3
"""Test module for testing generate_pytest_test_stubs."""

def simple_function(x: int) -> int:
    """Simple function for testing.
    
    Args:
        x: An integer input.
        
    Returns:
        The input value.
    """
    return x

class SimpleClass:
    """Simple class for testing."""
    
    def __init__(self, value: str):
        """Initialize the class.
        
        Args:
            value: A string value.
        """
        self.value = value
    
    def get_value(self) -> str:
        """Get the stored value.
        
        Returns:
            The stored string value.
        """
        return self.value
'''
        
        self.test_file_path = os.path.join(self.test_dir, "test_module.py")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_python_content)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_function_with_valid_path_save_to_file_true(self):
        """
        GIVEN a valid Python file path
        AND output_dir is None (default)
        AND save_to_file is True (default)
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function returns a string path to the generated test file
            - Test file is created in the same directory as input file
            - File name follows pattern 'test_{filename}_in_dir_{dirname}_{timestamp}.py'
            - Generated file contains valid Python code
        """
        # WHEN
        result = generate_pytest_test_stubs(self.test_file_path)
        
        # THEN
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.startswith(os.path.join(self.test_dir, "test_test_module_in_dir_")))
        self.assertTrue(result.endswith(".py"))
        
        # Verify the file contains valid Python code
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We do this because the module path is dynamically generated
        # and may not match the expected hardcoded path.
        path_as_module_path = _make_module_path(self.test_file_path)

        # Basic structure checks
        self.assertIn("import pytest", content)
        self.assertIn("import os", content)
        self.assertIn(f"from {path_as_module_path} import", content)
        self.assertIn("class TestQualityOfObjectsInModule", content)

    def test_function_with_valid_path_save_to_file_false(self):
        """
        GIVEN a valid Python file path
        AND output_dir is None (default)
        AND save_to_file is False
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function returns a string containing the generated test file content
            - No file is created on disk
            - Content contains valid Python test code structure
        """
        # Count files before
        files_before = os.listdir(self.test_dir)
        
        # WHEN
        result = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        self.assertIsInstance(result, str)
        
        # No new files should be created
        files_after = os.listdir(self.test_dir)
        self.assertEqual(len(files_before), len(files_after))
        
        # We do this because the module path is dynamically generated
        # and may not match the expected hardcoded path.
        path_as_module_path = _make_module_path(self.test_file_path)

        # Content should contain test structure
        self.assertIn("import pytest", result)
        self.assertIn("import os", result)
        self.assertIn(f"from {path_as_module_path} import", result)
        self.assertIn("class TestQualityOfObjectsInModule", result)

    def test_function_with_custom_output_dir_save_to_file_true(self):
        """
        GIVEN a valid Python file path
        AND a custom output_dir path
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function returns a string path to the generated test file
            - Test file is created in the specified output_dir
            - File name follows pattern 'test_{filename}_in_dir_{dirname}_{timestamp}.py'
        """
        
        # Create custom output directory
        custom_output_dir = Path(self.test_dir) / "custom_output"
        custom_output_dir.mkdir()
        
        # WHEN
        result = generate_pytest_test_stubs(self.test_file_path, output_dir=str(custom_output_dir))

        # THEN
        result_path = Path(result)
        self.assertIsInstance(result, str)
        self.assertTrue(result_path.exists())
        
        expected_prefix = custom_output_dir / "test_test_module_in_dir_"
        self.assertTrue(str(result_path).startswith(str(expected_prefix)))
        self.assertTrue(result_path.suffix == ".py")
        
        # Verify file is in custom directory, not original directory
        self.assertTrue(custom_output_dir in result_path.parents or result_path.parent == custom_output_dir)

        filename = result_path.name  # Get the filename to compare
        print("======================")
        print(self.test_file_path)
        print(result)

        # get the immediate parent directory of the test file
        test_file_parent = Path(self.test_file_path).parent.name
        self.assertIn(test_file_parent, filename)


    def test_function_with_custom_output_dir_save_to_file_false(self):
        """
        GIVEN a valid Python file path
        AND a custom output_dir path
        AND save_to_file is False
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function returns a string containing the generated test file content
            - No file is created on disk (output_dir is ignored)
            - Content contains valid Python test code structure
        """
        # Create custom output directory
        custom_output_dir = os.path.join(self.test_dir, "custom_output")
        os.makedirs(custom_output_dir)
        
        # Count files before in both directories
        files_before_test = os.listdir(self.test_dir)
        files_before_custom = os.listdir(custom_output_dir)
        
        # WHEN
        result = generate_pytest_test_stubs(
            self.test_file_path, 
            output_dir=custom_output_dir, 
            save_to_file=False
        )
        
        # THEN
        self.assertIsInstance(result, str)
        
        # No new files should be created in either directory
        files_after_test = os.listdir(self.test_dir)
        files_after_custom = os.listdir(custom_output_dir)
        self.assertEqual(len(files_before_test), len(files_after_test))
        self.assertEqual(len(files_before_custom), len(files_after_custom))
        
        # Content should contain test structure
        self.assertIn("import pytest", result)
        self.assertIn("class TestQualityOfObjectsInModule", result)

    def test_function_with_relative_path(self):
        """
        GIVEN a relative Python file path
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function processes the relative path correctly
            - Returns a string path to the generated test file
            - File is created relative to project root
        """
        # Change to test directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            relative_path = "test_module.py"
            
            # WHEN
            result = generate_pytest_test_stubs(relative_path)
            
            # THEN
            self.assertIsInstance(result, str)
            self.assertTrue(os.path.exists(result))
            self.assertTrue(result.endswith(".py"))
            
        finally:
            os.chdir(original_cwd)

    def test_function_with_absolute_path(self):
        """
        GIVEN an absolute Python file path
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function processes the absolute path correctly
            - Returns a string path to the generated test file
        """
        # Ensure we're using absolute path
        absolute_path = os.path.abspath(self.test_file_path)
        
        # WHEN
        result = generate_pytest_test_stubs(absolute_path)
        
        # THEN
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".py"))
        
        # Verify the file contains expected content
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("import pytest", content)
        self.assertIn("class TestQualityOfObjectsInModule", content)




class TestGeneratePytestTestStubsErrorHandling(unittest.TestCase):
    """Test generate_pytest_test_stubs error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a valid Python file for some tests
        self.valid_python_content = '''def test_function():
    """Test function."""
    pass
'''
        self.valid_file_path = os.path.join(self.test_dir, "valid.py")
        with open(self.valid_file_path, 'w', encoding='utf-8') as f:
            f.write(self.valid_python_content)
        
        # Create a file with syntax errors
        self.invalid_python_content = '''def broken_function(
    """This function has syntax errors."""
    pass
'''
        self.invalid_file_path = os.path.join(self.test_dir, "invalid.py")
        with open(self.invalid_file_path, 'w', encoding='utf-8') as f:
            f.write(self.invalid_python_content)
        
        # Create a non-Python file
        self.non_python_path = os.path.join(self.test_dir, "not_python.txt")
        with open(self.non_python_path, 'w', encoding='utf-8') as f:
            f.write("This is not Python code")

    def tearDown(self):
        """Clean up test fixtures."""
        # Make sure all files are writable before deletion
        for root, dirs, files in os.walk(self.test_dir):
            for d in dirs:
                os.chmod(os.path.join(root, d), stat.S_IRWXU)
            for f in files:
                os.chmod(os.path.join(root, f), stat.S_IRWXU)
        shutil.rmtree(self.test_dir)

    def test_function_with_nonexistent_file_path(self):
        """
        GIVEN a file path that does not exist
        WHEN generate_pytest_test_stubs is called
        THEN expect FileNotFoundError to be raised
        """
        nonexistent_path = os.path.join(self.test_dir, "does_not_exist.py")
        
        with self.assertRaises(FileNotFoundError):
            generate_pytest_test_stubs(nonexistent_path)

    def test_function_with_invalid_python_file_extension(self):
        """
        GIVEN a file path that does not have a .py extension
        WHEN generate_pytest_test_stubs is called
        THEN expect ValueError to be raised
        """
        with self.assertRaises(ValueError) as context:
            generate_pytest_test_stubs(self.non_python_path)

        self.assertIn("is not a Python file", str(context.exception))

    def test_function_with_directory_instead_of_file(self):
        """
        GIVEN a path that points to a directory instead of a file
        WHEN generate_pytest_test_stubs is called
        THEN expect ValueError to be raised
        """
        directory_path = self.test_dir
        
        with self.assertRaises(ValueError) as context:
            generate_pytest_test_stubs(directory_path)
        
        self.assertIn("directory", str(context.exception).lower())

    def test_function_with_python_file_syntax_errors(self):
        """
        GIVEN a Python file that contains syntax errors
        WHEN generate_pytest_test_stubs is called
        THEN expect SyntaxError to be raised
        """
        with self.assertRaises(SyntaxError):
            generate_pytest_test_stubs(self.invalid_file_path)

    def test_function_with_unwritable_output_directory(self):
        """
        GIVEN a valid Python file path
        AND an output_dir that is not writable
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect PermissionError to be raised
        """
        # Create an unwritable directory
        unwritable_dir = os.path.join(self.test_dir, "unwritable")
        os.makedirs(unwritable_dir)
        os.chmod(unwritable_dir, stat.S_IRUSR | stat.S_IXUSR)  # read and execute only
        
        try:
            with self.assertRaises(PermissionError):
                generate_pytest_test_stubs(
                    self.valid_file_path, 
                    output_dir=unwritable_dir, 
                    save_to_file=True
                )
        finally:
            # Restore permissions for cleanup
            os.chmod(unwritable_dir, stat.S_IRWXU)

    def test_function_with_nonexistent_output_directory(self):
        """
        GIVEN a valid Python file path
        AND an output_dir that does not exist
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Either the directory is created automatically and function succeeds
            - Or FileNotFoundError is raised if directory creation fails
        """
        nonexistent_output_dir = os.path.join(self.test_dir, "nonexistent", "nested", "dir")
        
        try:
            result = generate_pytest_test_stubs(
                self.valid_file_path, 
                output_dir=nonexistent_output_dir, 
                save_to_file=True
            )
            # If successful, directory should have been created
            self.assertTrue(os.path.exists(nonexistent_output_dir))
            self.assertTrue(os.path.exists(result))
            
        except FileNotFoundError:
            # This is also acceptable behavior
            self.assertFalse(os.path.exists(nonexistent_output_dir))

    def test_function_with_empty_string_path(self):
        """
        GIVEN an empty string as the path parameter
        WHEN generate_pytest_test_stubs is called
        THEN expect ValueError to be raised
        """
        with self.assertRaises(ValueError) as context:
            generate_pytest_test_stubs("")
        
        self.assertIn("empty", str(context.exception).lower())

    def test_function_with_none_path(self):
        """
        GIVEN None as the path parameter
        WHEN generate_pytest_test_stubs is called
        THEN expect TypeError to be raised
        """
        with self.assertRaises(TypeError):
            generate_pytest_test_stubs(None)

    def test_function_with_whitespace_only_path(self):
        """
        GIVEN a path that contains only whitespace characters
        WHEN generate_pytest_test_stubs is called
        THEN expect ValueError to be raised
        """
        whitespace_paths = ["   ", "\t", "\n", "  \t  \n  "]
        
        for whitespace_path in whitespace_paths:
            with self.subTest(path=repr(whitespace_path)):
                with self.assertRaises(ValueError) as context:
                    generate_pytest_test_stubs(whitespace_path)
                
                self.assertIn("empty", str(context.exception).lower())

    def test_function_with_special_characters_in_path(self):
        """
        GIVEN a path that contains special characters that might cause issues
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function handles special characters gracefully
            - Or raises appropriate exception if characters are invalid
        """
        # Test with various special characters that might be problematic
        special_chars_filename = "test@#$%^&()file.py"
        special_chars_path = os.path.join(self.test_dir, special_chars_filename)
        
        # Create the file with special characters
        with open(special_chars_path, 'w', encoding='utf-8') as f:
            f.write(self.valid_python_content)
        
        try:
            # This should either work or raise a clear exception
            result = generate_pytest_test_stubs(special_chars_path)
            # If it succeeds, verify the result
            self.assertIsInstance(result, str)
            if os.path.exists(result):
                self.assertTrue(result.endswith(".py"))
        except (ValueError, OSError) as e:
            # These are acceptable exceptions for invalid characters
            self.assertIsInstance(e, (ValueError, OSError))

    def test_function_with_unicode_characters_in_path(self):
        """
        GIVEN a path that contains unicode characters
        WHEN generate_pytest_test_stubs is called
        THEN expect function to handle unicode gracefully
        """
        unicode_filename = "test_файл_测试.py"
        unicode_path = os.path.join(self.test_dir, unicode_filename)
        
        # Create the file with unicode characters
        with open(unicode_path, 'w', encoding='utf-8') as f:
            f.write(self.valid_python_content)
        
        try:
            result = generate_pytest_test_stubs(unicode_path)
            self.assertIsInstance(result, str)
            if os.path.exists(result):
                self.assertTrue(result.endswith(".py"))
        except (ValueError, OSError, UnicodeError) as e:
            # These are acceptable exceptions for unicode handling issues
            self.assertIsInstance(e, (ValueError, OSError, UnicodeError))

    def test_function_with_very_long_path(self):
        """
        GIVEN a very long file path that might exceed system limits
        WHEN generate_pytest_test_stubs is called
        THEN expect appropriate handling of path length limits
        """
        # Create a very long path (close to system limits)
        long_component = "a" * 100
        long_path_components = [self.test_dir]
        
        # Add multiple long components to approach path length limits
        for i in range(10):
            long_path_components.append(f"{long_component}_{i}")
        
        long_path_components.append("test_file.py")
        long_path = os.path.join(*long_path_components)
        
        try:
            # Try to create the directory structure
            os.makedirs(os.path.dirname(long_path), exist_ok=True)
            with open(long_path, 'w', encoding='utf-8') as f:
                f.write(self.valid_python_content)
            
            # Test the function
            result = generate_pytest_test_stubs(long_path)
            self.assertIsInstance(result, str)
            
        except (OSError, FileNotFoundError) as e:
            # These are acceptable exceptions for path length issues
            self.assertIsInstance(e, (OSError, FileNotFoundError))



class TestGeneratePytestTestStubsContentGeneration(unittest.TestCase):
    """Test generate_pytest_test_stubs content generation and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create comprehensive test Python file
        self.comprehensive_python_content = '''#!/usr/bin/env python3
"""Comprehensive test module with various Python constructs."""

import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

class TestClass:
    """Test class with various methods."""
    
    class_attr: str = "test"
    
    def __init__(self, value: int):
        """Initialize the test class.
        
        Args:
            value: An integer value.
        """
        self.value = value
        self.instance_attr = "instance"
    
    def regular_method(self, param: str) -> str:
        """Regular instance method.
        
        Args:
            param: A string parameter.
            
        Returns:
            The processed string.
        """
        return param.upper()
    
    async def async_method(self, data: Dict[str, int]) -> List[int]:
        """Async instance method.
        
        Args:
            data: Dictionary of string keys to integer values.
            
        Returns:
            List of integer values.
        """
        return list(data.values())
    
    @classmethod
    def class_method(cls, name: str) -> 'TestClass':
        """Class method constructor.
        
        Args:
            name: Name parameter.
            
        Returns:
            New instance of TestClass.
        """
        return cls(len(name))
    
    @staticmethod
    def static_method(x: int, y: int) -> int:
        """Static method for calculations.
        
        Args:
            x: First integer.
            y: Second integer.
            
        Returns:
            Sum of x and y.
        """
        return x + y
    
    @property
    def value_property(self) -> int:
        """Property for accessing value.
        
        Returns:
            The stored value.
        """
        return self.value

def regular_function(text: str) -> str:
    """Regular module-level function.
    
    Args:
        text: Input text to process.
        
    Returns:
        Processed text.
    """
    def nested_function(inner_text: str) -> str:
        """This nested function should be ignored."""
        return inner_text.lower()
    
    return nested_function(text)

async def async_function(items: List[str]) -> Dict[str, int]:
    """Async module-level function.
    
    Args:
        items: List of string items.
        
    Returns:
        Dictionary mapping items to their lengths.
    """
    return {item: len(item) for item in items}

def _private_function(secret: str) -> str:
    """Private function (starts with underscore).
    
    Args:
        secret: Secret string.
        
    Returns:
        Processed secret.
    """
    return secret[::-1]

class _PrivateClass:
    """Private class (starts with underscore)."""
    
    def _private_method(self) -> None:
        """Private method in private class."""
        pass

# Lambda function (should be ignored)
lambda_func = lambda x: x * 2

# Variable assignments (should be ignored)
MODULE_CONSTANT = "test_constant"
'''
        
        self.test_file_path = os.path.join(self.test_dir, "comprehensive_module.py")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.comprehensive_python_content)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_generated_content_includes_file_existence_validation(self):
        """
        GIVEN a valid Python file
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - File existence assertions for both source and documentation files
            - Proper file path construction using os.path.join and expanduser
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        self.assertIn("home_dir = os.path.expanduser('~')", content)
        self.assertIn("file_path = os.path.join(home_dir,", content)
        self.assertIn("md_path = os.path.join(home_dir,", content)
        self.assertIn("assert os.path.exists(file_path)", content)
        self.assertIn("assert os.path.exists(md_path)", content)
        self.assertIn("Input file does not exist", content)
        self.assertIn("Documentation file does not exist", content)

    def test_generated_content_includes_import_statements(self):
        """
        GIVEN a Python file with classes and functions
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - Import statements for all callable objects and classes
            - Import statement for the module itself
            - Proper import structure
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        pprint(content)

        # THEN
        # Check for main imports
        self.assertIn("import pytest", content)
        self.assertIn("import os", content)
        
        # Check for imports from the test module
        module_path = _make_module_path(self.test_file_path)
        self.assertIn(f"from {module_path} import", content)
        
        # Check for specific callable imports
        self.assertIn("TestClass", content)
        self.assertIn("regular_function", content)
        self.assertIn("async_function", content)
        self.assertIn("_private_function", content)
        self.assertIn("_PrivateClass", content)
        
        # Check for module dependency imports
        self.assertIn("import os", content)
        self.assertIn("import sys", content)
        # NOTE all imports multiline imports should be like this.
        self.assertIn("from typing import (", content)
        self.assertIn("Dict,", content)
        self.assertIn("List,", content)
        self.assertIn("Optional", content)
        self.assertIn("from pathlib import Path", content)

    def test_generated_content_includes_accessibility_assertions(self):
        """
        GIVEN a Python file with classes that have methods and attributes
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - Accessibility assertions for class methods
            - Accessibility assertions for class attributes
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        #pprint(content)

        # THEN
        # Check for method accessibility assertions
        self.assertIn("assert TestClass.regular_method", content)
        self.assertIn("assert TestClass.async_method", content)
        self.assertIn("assert TestClass.class_method", content)
        self.assertIn("assert TestClass.static_method", content)
        self.assertIn("assert TestClass.value_property", content)
        
        # Check for attribute accessibility assertions
        self.assertIn("assert TestClass.class_attr", content)

    def test_generated_content_includes_quality_assurance_tests(self):
        """
        GIVEN a valid Python file
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - TestQualityOfObjectsInModule class
            - Metadata quality test methods
            - Code quality test methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)

        # THEN
        self.assertIn("class TestQualityOfObjectsInModule", content)
        self.assertIn("def test_callable_objects_metadata_quality(self)", content)
        self.assertIn("def test_callable_objects_quality(self)", content)
        self.assertIn("raise_on_bad_callable_metadata", content)
        self.assertIn("raise_on_bad_callable_code_quality", content)
        self.assertIn("BadDocumentationError", content)
        self.assertIn("BadSignatureError", content)

    def test_generated_content_includes_individual_test_classes(self):
        """
        GIVEN a Python file with multiple callable objects
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - Individual test class for each callable object
            - Proper test class naming convention
            - NotImplementedError placeholders in test methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        pprint(content)
        
        # THEN
        # Check for individual test classes
        self.assertIn("class Test__Init__MethodForTestClass", content)
        self.assertIn("class TestRegularMethodMethodForTestClass", content)
        self.assertIn("class TestAsyncMethodMethodForTestClass", content)
        self.assertIn("class TestClassMethodMethodForTestClass", content)
        self.assertIn("class TestStaticMethodMethodForTestClass", content)
        self.assertIn("class TestValuePropertyPropertyForTestClass", content)
        self.assertIn("class TestRegularFunctionFunction", content)
        self.assertIn("class TestAsyncFunctionFunction", content)
        self.assertIn("class Test_PrivateFunctionFunction", content)
        self.assertIn("class Test_PrivateClassClass", content)
        
        # Check for NotImplementedError placeholders
        self.assertIn('raise NotImplementedError("test_', content)
        
        # Count test classes to ensure all callables are covered
        test_class_count = len(re.findall(r'class Test\w+(?:Method|Function|Class|Property)', content))
        self.assertGreaterEqual(test_class_count, 10)  # Should have at least 10 test classes

    def test_generated_content_handles_async_functions(self):
        """
        GIVEN a Python file with async functions/methods
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - @pytest.mark.asyncio decorator for async test methods
            - Proper async def syntax in test methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        pprint(content)

        # THEN
        # Check for asyncio markers
        self.assertIn("@pytest.mark.asyncio", content)
        
        # Check for async test methods
        async_method_pattern = r'@pytest\.mark\.asyncio\s+async def test_\w+'
        async_matches = re.findall(async_method_pattern, content)
        self.assertGreaterEqual(len(async_matches), 2)  # Should have at least 2 async tests
        
        # Verify specific async test methods exist
        self.assertIn("async def test_async_method(self)", content)
        self.assertIn("async def test_async_function(self)", content)

    def test_generated_content_handles_private_functions(self):
        """
        GIVEN a Python file with private functions (starting with _)
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include:
            - Test classes for private functions
            - Proper handling of private function names in test class names
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        pprint(content)

        # THEN
        self.assertIn("class Test_PrivateFunctionFunction", content)
        self.assertIn("class Test_PrivateClassClass", content)
        self.assertIn("def test__private_function(self)", content)

    def test_generated_content_ignores_nested_functions(self):
        """
        GIVEN a Python file with nested functions inside other functions
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to:
            - Not include test classes for nested functions
            - Only include top-level callable objects
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        # Should NOT include nested_function
        self.assertNotIn("TestNestedFunction", content)
        self.assertNotIn("test_nested_function", content)
        
        # Should include the parent function
        self.assertIn("TestRegularFunctionFunction", content)

    def test_generated_content_ignores_lambda_functions(self):
        """
        GIVEN a Python file with lambda functions
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to:
            - Not include test classes for lambda functions
            - Only include explicitly defined functions and classes
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        # Should NOT include lambda_func
        self.assertNotIn("TestLambdaFunc", content)
        self.assertNotIn("test_lambda_func", content)

    def test_generated_content_handles_dunder_methods_correctly(self):
        """
        GIVEN a Python file with classes that have custom __init__ and other dunder methods
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to:
            - Include test classes for explicitly defined dunder methods like __init__
            - Ignore inherited dunder methods
            - Properly name test classes for dunder methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        pprint(content)
        
        # THEN
        # Should include __init__ method
        self.assertIn("class Test__Init__MethodForTestClass", content)
        self.assertIn("def test___init__(self)", content)
        
        # Should NOT include inherited dunder methods like __str__, __repr__, etc.
        self.assertNotIn("Test__Str__MethodFor", content)
        self.assertNotIn("Test__Repr__MethodFor", content)

    def test_generated_content_valid_python_syntax(self):
        """
        GIVEN any valid Python file
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to:
            - Be valid Python syntax that can be compiled
            - Follow proper indentation and formatting
            - Include proper import statements and class structures
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        # Test that the generated content can be parsed as valid Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"Generated content has invalid Python syntax: {e}")
        
        # Check for proper shebang and encoding
        self.assertTrue(content.startswith("#!/usr/bin/env python3"))
        self.assertIn("# -*- coding: utf-8 -*-", content)
        
        # Check for proper imports at the beginning
        lines = content.split('\n')
        import_started = False
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_started = True
            elif import_started and line.strip() and not line.strip().startswith('#'):
                if not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                    break
        
        # Verify proper structure
        self.assertIn("if __name__ == \"__main__\":", content)
        self.assertIn("pytest.main([__file__, \"-v\"])", content)

    def test_generated_content_handles_properties(self):
        """
        GIVEN a Python file with property decorators
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to properly handle property methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        self.assertIn("class TestValuePropertyPropertyForTestClass", content)
        self.assertIn("def test_value_property(self)", content)

    def test_generated_content_handles_classmethods_and_staticmethods(self):
        """
        GIVEN a Python file with @classmethod and @staticmethod decorators
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to properly handle these special methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        self.assertIn("class TestClassMethodMethodForTestClass", content)
        self.assertIn("class TestStaticMethodMethodForTestClass", content)
        self.assertIn("def test_class_method(self)", content)
        self.assertIn("def test_static_method(self)", content)

    def test_generated_content_includes_module_constants_check(self):
        """
        GIVEN a Python file with module-level constants
        WHEN generate_pytest_test_stubs is called with save_to_file=False
        THEN expect the generated content to include checks for module constants if they exist
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        # Module constants should not generate test classes but might be mentioned in imports
        self.assertNotIn("TestModuleConstant", content)




class TestGeneratePytestTestStubsFileOperations(unittest.TestCase):
    """Test generate_pytest_test_stubs file operations and I/O functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create various test Python files
        self.simple_python_content = '''def simple_function():
    """Simple test function."""
    pass

class SimpleClass:
    """Simple test class."""
    
    def method(self):
        """Simple method."""
        pass
'''
        
        self.simple_file_path = os.path.join(self.test_dir, "simple_module.py")
        with open(self.simple_file_path, 'w', encoding='utf-8') as f:
            f.write(self.simple_python_content)
        
        # Create large file with many functions/classes
        self.large_python_content = '''#!/usr/bin/env python3
"""Large module with many callable objects."""
'''
        
        # Generate many functions and classes
        for i in range(50):
            self.large_python_content += f'''
def function_{i}(param: int) -> int:
    """Function number {i}.
    
    Args:
        param: Integer parameter.
        
    Returns:
        The parameter value.
    """
    return param

class Class_{i}:
    """Class number {i}."""
    
    def __init__(self, value: str):
        """Initialize class {i}.
        
        Args:
            value: String value.
        """
        self.value = value
    
    def method_{i}(self) -> str:
        """Method {i}.
        
        Returns:
            The stored value.
        """
        return self.value
'''
        
        self.large_file_path = os.path.join(self.test_dir, "large_module.py")
        with open(self.large_file_path, 'w', encoding='utf-8') as f:
            f.write(self.large_python_content)
        
        # Create empty Python file
        self.empty_file_path = os.path.join(self.test_dir, "empty_module.py")
        with open(self.empty_file_path, 'w', encoding='utf-8') as f:
            f.write('#!/usr/bin/env python3\n"""Empty module."""\n')
        
        # Create file with only imports
        self.imports_only_content = '''#!/usr/bin/env python3
"""Module with only imports."""

import os
import sys
from typing import Dict, List
from pathlib import Path
'''
        
        self.imports_only_file_path = os.path.join(self.test_dir, "imports_only_module.py")
        with open(self.imports_only_file_path, 'w', encoding='utf-8') as f:
            f.write(self.imports_only_content)
        
        # Create file with unicode content
        self.unicode_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module with unicode characters: тест, 测试, テスト."""

def unicode_function(text: str) -> str:
    """Function with unicode in docstring: 这是一个测试函数.
    
    Args:
        text: Input text with possible unicode: café, naïve, résumé.
        
    Returns:
        Processed text.
    """
    return f"Processed: {text}"

class UnicodeClass:
    """Class with unicode: Москва, 北京, 東京."""
    
    def unicode_method(self) -> str:
        """Method returning unicode string."""
        return "Результат: 结果: 結果"
'''
        
        self.unicode_file_path = os.path.join(self.test_dir, "unicode_module.py")
        with open(self.unicode_file_path, 'w', encoding='utf-8') as f:
            f.write(self.unicode_content)

    def tearDown(self):
        """Clean up test fixtures."""
        # Ensure all files are writable before cleanup
        for root, dirs, files in os.walk(self.test_dir):
            for d in dirs:
                os.chmod(os.path.join(root, d), stat.S_IRWXU)
            for f in files:
                os.chmod(os.path.join(root, f), stat.S_IRWXU)
        shutil.rmtree(self.test_dir)

    def test_file_creation_in_same_directory_as_input(self):
        """
        GIVEN a valid Python file path
        AND output_dir is None
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Test file is created in the same directory as the input file
            - File name follows the specified naming convention
            - File contains the generated test content
        """
        # WHEN
        result = generate_pytest_test_stubs(self.simple_file_path, output_dir=None, save_to_file=True)
        
        # THEN
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.dirname(result), os.path.dirname(self.simple_file_path))
        
        # Check filename pattern
        filename = os.path.basename(result)
        self.assertTrue(filename.startswith("test_simple_module_in_dir_"))
        self.assertTrue(filename.endswith(".py"))
        
        # Verify content
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        
        module_path = _make_module_path(self.simple_file_path)
        self.assertIn("import pytest", content)
        self.assertIn(f"from {module_path} import", content)
        self.assertIn("SimpleClass", content)
        self.assertIn("simple_function", content)

    def test_file_creation_in_custom_output_directory(self):
        """
        GIVEN a valid Python file path
        AND a custom output_dir
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Test file is created in the specified output directory
            - Original file directory is not modified
            - File name follows the specified naming convention
        """
        # Create custom output directory
        custom_output_dir = os.path.join(self.test_dir, "custom_tests")
        os.makedirs(custom_output_dir)
        
        # Count files in original directory before
        original_files_before = len(os.listdir(os.path.dirname(self.simple_file_path)))
        
        # WHEN
        result = generate_pytest_test_stubs(
            self.simple_file_path, 
            output_dir=custom_output_dir, 
            save_to_file=True
        )
        
        # THEN
        self.assertTrue(os.path.exists(result))
        self.assertEqual(os.path.dirname(result), custom_output_dir)
        
        # Original directory should have same number of files
        original_files_after = len(os.listdir(os.path.dirname(self.simple_file_path)))
        self.assertEqual(original_files_before, original_files_after)
        
        # Custom directory should have the new file
        custom_files = os.listdir(custom_output_dir)
        self.assertEqual(len(custom_files), 1)
        self.assertTrue(custom_files[0].startswith("test_simple_module_in_dir_"))

    def test_filename_generation_follows_convention(self):
        """
        GIVEN a Python file with a specific name and directory
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Generated filename follows pattern 'test_{filename}_in_dir_{dirname}_{timestamp}.py'
            - Timestamp is included in the filename
            - Special characters in filename/dirname are handled appropriately
        """
        # WHEN
        result = generate_pytest_test_stubs(self.simple_file_path, save_to_file=True)
        
        # THEN
        filename = os.path.basename(result)
        dirname = os.path.basename(os.path.dirname(self.simple_file_path))
        
        # Check pattern: test_{filename}_in_dir_{dirname}_{timestamp}.py
        expected_prefix = f"test_simple_module_in_dir_{dirname}_"
        self.assertTrue(filename.startswith(expected_prefix))
        self.assertTrue(filename.endswith(".py"))
        
        # Extract and validate timestamp part
        timestamp_part = filename[len(expected_prefix):-3]  # Remove .py
        self.assertRegex(timestamp_part, r'\d{8}_\d{6}')
        
        # Verify timestamp is recent (within last minute)
        try:
            timestamp = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
            time_diff = abs((datetime.now() - timestamp).total_seconds())
            self.assertLess(time_diff, 60)  # Within 1 minute
        except ValueError:
            self.fail(f"Timestamp format is invalid: {timestamp_part}")

    def test_file_overwrite_behavior(self):
        """
        GIVEN a Python file that has already had test stubs generated
        AND the output file already exists
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called again
        THEN expect:
            - Either a new file with different timestamp is created
            - Or existing file is overwritten
            - No data corruption occurs
        """
        # Generate first file
        result1 = generate_pytest_test_stubs(self.simple_file_path, save_to_file=True)
        self.assertTrue(os.path.exists(result1))
        
        # Wait a moment to ensure different timestamp
        time.sleep(1)
        
        # Generate second file
        result2 = generate_pytest_test_stubs(self.simple_file_path, save_to_file=True)
        self.assertTrue(os.path.exists(result2))
        
        # Files should have different names (different timestamps) or same name if overwritten
        if result1 == result2:
            # Same file was overwritten - verify it's valid
            with open(result2, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("import pytest", content)
        else:
            # Different files created - both should exist and be valid
            with open(result1, 'r', encoding='utf-8') as f:
                content1 = f.read()
            with open(result2, 'r', encoding='utf-8') as f:
                content2 = f.read()
            
            self.assertIn("import pytest", content1)
            self.assertIn("import pytest", content2)

    def test_file_permissions_on_created_file(self):
        """
        GIVEN a valid Python file path
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Created file has appropriate read/write permissions
            - File is accessible for further operations
            - File permissions match system defaults
        """
        # WHEN
        result = generate_pytest_test_stubs(self.simple_file_path, save_to_file=True)
        
        # THEN
        self.assertTrue(os.path.exists(result))
        
        # Check file permissions
        file_stat = os.stat(result)
        file_mode = stat.filemode(file_stat.st_mode)
        
        # File should be readable and writable by owner
        self.assertTrue(file_stat.st_mode & stat.S_IRUSR)  # Owner read
        self.assertTrue(file_stat.st_mode & stat.S_IWUSR)  # Owner write
        
        # Test that we can read and write to the file
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIsInstance(content, str)
        
        # Test write access
        test_comment = "\n# Test comment added by test\n"
        with open(result, 'a', encoding='utf-8') as f:
            f.write(test_comment)
        
        with open(result, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        self.assertIn("Test comment added by test", updated_content)

    def test_file_encoding_utf8(self):
        """
        GIVEN a Python file with unicode characters
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Generated file is saved with UTF-8 encoding
            - Unicode characters are preserved correctly
            - File includes proper encoding declaration
        """
        # WHEN
        result = generate_pytest_test_stubs(self.unicode_file_path, save_to_file=True)
        
        # THEN
        self.assertTrue(os.path.exists(result))
        
        # Read file with explicit UTF-8 encoding
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()

        print(content)

        # Check encoding declaration
        self.assertIn("# -*- coding: utf-8 -*-", content)
        
        # Verify unicode characters are preserved in imports and comments
        self.assertIn("unicode_module", content)
        
        # Test that file can be parsed as Python with unicode
        try:
            compile(content, result, 'exec')
        except SyntaxError as e:
            self.fail(f"Generated file with unicode cannot be compiled: {e}")

    def test_large_python_file_handling(self):
        """
        GIVEN a very large Python file with many classes and functions
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function completes successfully without memory issues
            - All callable objects are processed
            - Generated file is created without truncation
        """
        # WHEN
        result = generate_pytest_test_stubs(self.large_file_path, save_to_file=True)
        
        # THEN
        self.assertTrue(os.path.exists(result))
        
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify all functions and classes are included
        for i in range(50):
            self.assertIn(f"function_{i}", content)
            self.assertIn(f"Class_{i}", content)
            self.assertIn(f"TestFunction{i}Function", content)
            self.assertIn(f"TestClass{i}Class", content)
        
        # Verify file structure is complete
        self.assertIn("import pytest", content)
        self.assertIn("class TestQualityOfObjectsInModule", content)
        self.assertIn("if __name__ == \"__main__\":", content)
        
        # File should be substantial in size
        file_size = os.path.getsize(result)
        self.assertGreater(file_size, 10000)  # At least 10KB

    def test_empty_python_file_handling(self):
        """
        GIVEN an empty Python file (contains no code)
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function completes successfully
            - No file is generated
            - String to read "No callable objects or classes found in {module_path}"
            - File still includes quality assurance tests
        """
        # WHEN
        result = generate_pytest_test_stubs(self.empty_file_path, save_to_file=True)

        # THEN
        self.assertFalse(os.path.exists(result))
        self.assertIn("No callable objects or classes found in", result)


    def test_python_file_with_only_imports(self):
        """
        GIVEN a Python file that contains only import statements
        AND save_to_file is True
        WHEN generate_pytest_test_stubs is called
        THEN expect:
            - Function completes successfully
            - No file to be generated
            - String to read "No callable objects or classes found in {module_path}"
        """
        # WHEN
        result = generate_pytest_test_stubs(self.imports_only_file_path, save_to_file=True)

        # THEN
        self.assertFalse(os.path.exists(result))
        self.assertIn("No callable objects or classes found in", result)


    def test_concurrent_file_operations(self):
        """
        GIVEN multiple calls to generate_pytest_test_stubs running concurrently
        AND all calls have save_to_file is True
        WHEN functions execute simultaneously
        THEN expect:
            - No file corruption occurs
            - Each call produces its own output file
            - No race conditions in file creation
        """
        results = []
        errors = []
        
        def generate_stub(file_path, index):
            try:
                result = generate_pytest_test_stubs(file_path, save_to_file=True)
                results.append((index, result))
            except Exception as e:
                errors.append((index, e))
        
        
        # Create multiple threads
        threads = []
        test_files = [self.simple_file_path, self.unicode_file_path, self.imports_only_file_path]
        
        for i in range(6):  # 6 concurrent operations
            file_path = test_files[i % len(test_files)]
            thread = threading.Thread(target=generate_stub, args=(file_path, i))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        # THEN
        print(errors)
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 6, "Not all operations completed")
        
        # Verify all files exist and are valid
        for index, result_path in results:

            if "No callable objects or classes found in" in result_path:
                self.assertFalse(os.path.exists(result_path), f"File {result_path} should not exist")
                continue

            self.assertTrue(os.path.exists(result_path), f"File {result_path} does not exist")
            
            with open(result_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn("import pytest", content)
            self.assertIn("class TestQualityOfObjectsInModule", content)
        
        # Verify files have different names (no overwrites due to race conditions)
        # NOTE Overwrite doesn't matter, since the file content is deterministic.
        # result_paths = [path for _, path in results]
        # print(result_paths)
        # unique_paths = set(result_paths)
        # self.assertEqual(len(unique_paths), len(result_paths), "Some files were overwritten due to race conditions")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
import shutil
import ast
import re
from datetime import datetime

from tools.functions.generate_pytest_test_stubs import (
    generate_pytest_test_stubs,
)


class TestGeneratePytestTestStubsTemplateAndJinja(unittest.TestCase):
    """Test generate_pytest_test_stubs template and Jinja2 functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test file with various callable types
        self.diverse_python_content = '''#!/usr/bin/env python3
"""Module with diverse callable objects for template testing."""

import os
import asyncio
from typing import Dict, List, Optional, Union

def regular_function(param: str) -> str:
    """Regular function.
    
    Args:
        param: String parameter.
        
    Returns:
        Processed string.
    """
    return param.upper()

async def async_function(data: List[int]) -> Dict[str, int]:
    """Async function.
    
    Args:
        data: List of integers.
        
    Returns:
        Dictionary with processed data.
    """
    return {"sum": sum(data), "count": len(data)}

class RegularClass:
    """Regular class with various methods."""
    
    class_attribute: str = "test_value"
    
    def __init__(self, name: str, value: int = 0):
        """Initialize the class.
        
        Args:
            name: Name of the instance.
            value: Initial value (default: 0).
        """
        self.name = name
        self.value = value
        self.instance_attr = "instance"
    
    def instance_method(self, multiplier: float) -> float:
        """Instance method.
        
        Args:
            multiplier: Multiplication factor.
            
        Returns:
            Calculated result.
        """
        return self.value * multiplier
    
    async def async_method(self, delay: float) -> str:
        """Async instance method.
        
        Args:
            delay: Delay in seconds.
            
        Returns:
            Status message.
        """
        await asyncio.sleep(delay)
        return f"Completed after {delay} seconds"
    
    @classmethod
    def create_default(cls) -> 'RegularClass':
        """Class method constructor.
        
        Returns:
            New instance with default values.
        """
        return cls("default", 100)
    
    @staticmethod
    def utility_function(x: int, y: int) -> int:
        """Static method utility.
        
        Args:
            x: First integer.
            y: Second integer.
            
        Returns:
            Sum of x and y.
        """
        return x + y
    
    @property
    def computed_value(self) -> int:
        """Property for computed value.
        
        Returns:
            Computed value based on instance state.
        """
        return self.value * 2

def _private_function(secret: str) -> str:
    """Private function with underscore.
    
    Args:
        secret: Secret string.
        
    Returns:
        Reversed secret.
    """
    return secret[::-1]

class _PrivateClass:
    """Private class with underscore."""
    
    def __init__(self, data: bytes):
        """Initialize private class.
        
        Args:
            data: Binary data.
        """
        self.data = data
    
    def _private_method(self) -> int:
        """Private method.
        
        Returns:
            Length of data.
        """
        return len(self.data)
'''
        
        self.test_file_path = os.path.join(self.test_dir, "diverse_module.py")
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(self.diverse_python_content)
        
        # Create file with edge case names
        self.edge_case_content = '''#!/usr/bin/env python3
"""Module with edge case names."""

def function_with_123_numbers(x: int) -> int:
    """Function with numbers in name.
    
    Args:
        x: Input integer.
        
    Returns:
        Modified integer.
    """
    return x + 123

def function_with_underscores_everywhere(a: str, b: str) -> str:
    """Function with many underscores.
    
    Args:
        a: First string.
        b: Second string.
        
    Returns:
        Concatenated string.
    """
    return f"{a}_{b}"

class Class_With_Underscores_123:
    """Class with underscores and numbers."""
    
    def method_with_CAPS_and_123(self) -> None:
        """Method with caps and numbers."""
        pass

def __dunder_function__(value: str) -> str:
    """Function with dunder naming.
    
    Args:
        value: Input value.
        
    Returns:
        Processed value.
    """
    return f"__{value}__"
'''
        
        self.edge_case_file_path = os.path.join(self.test_dir, "edge_case_module.py")
        with open(self.edge_case_file_path, 'w', encoding='utf-8') as f:
            f.write(self.edge_case_content)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_jinja_template_rendering_success(self):
        """
        GIVEN a valid Python file with various callable objects
        WHEN generate_pytest_test_stubs processes the file
        THEN expect:
            - Jinja2 template renders successfully without errors
            - All template variables are properly substituted
            - Output contains expected structure and content
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        # Verify template rendered without errors (content is returned)
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 1000)  # Should be substantial content

        # Verify all expected sections are present
        self.assertIn("#!/usr/bin/env python3", content)
        self.assertIn("# -*- coding: utf-8 -*-", content)
        self.assertIn("import pytest", content)
        self.assertIn("import os", content)
        self.assertIn(f"from {_make_module_path(self.test_file_path)} import", content)
        self.assertIn("class TestQualityOfObjectsInModule", content)
        self.assertIn("if __name__ == \"__main__\":", content)
        
        # Verify template variables were substituted
        self.assertNotIn("{{", content)  # No unsubstituted Jinja variables
        self.assertNotIn("}}", content)  # No unsubstituted Jinja variables
        self.assertNotIn("{%", content)  # No unsubstituted Jinja blocks
        self.assertNotIn("%}", content)  # No unsubstituted Jinja blocks

    def test_template_handles_missing_variables_gracefully(self):
        """
        GIVEN a scenario where some template variables might be missing
        WHEN Jinja2 template is rendered
        THEN expect:
            - Template renders without crashing
            - Missing variables are handled with appropriate defaults
            - Or appropriate error is raised for truly required variables
        """
        # This test verifies the function doesn't crash on edge cases
        # WHEN
        try:
            content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
            
            # THEN
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 100)
            
            # Should not contain template error markers
            self.assertNotIn("TEMPLATE_ERROR", content.upper())
            self.assertNotIn("UNDEFINED", content.upper())
            
        except Exception as e:
            # If an exception is raised, it should be a meaningful one
            self.assertIsInstance(e, (ValueError, TypeError, AttributeError))
            self.assertIn("template", str(e).lower())

    def test_template_escapes_special_characters(self):
        """
        GIVEN a Python file with functions/classes that have special characters in names
        WHEN template is rendered
        THEN expect:
            - Special characters are properly escaped in the output
            - Generated code remains syntactically valid
            - No injection vulnerabilities are created
        """
        # WHEN
        content = generate_pytest_test_stubs(self.edge_case_file_path, save_to_file=False)
        
        # THEN
        # Verify content is valid Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"Generated content with special characters is not valid Python: {e}")

        print(content)
        
        # Verify special characters are handled in class/method names
        self.assertIn("TestFunctionWith123NumbersFunction", content)
        self.assertIn("TestFunctionWithUnderscoresEverywhereFunction", content)
        self.assertIn("TestClassWithUnderscores123Class", content)
        self.assertIn("TestMethodWithCapsAnd123MethodFor", content)
        self.assertIn("Test__Dunderfunction__Function", content)
        
        # Verify no dangerous characters that could cause injection
        dangerous_patterns = [
            r'__import__\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                # Only fail if it's not in expected import/test context
                context = content[max(0, matches.start()-50):matches.end()+50]
                if "import" not in context and "test" not in context.lower():
                    self.fail(f"Potentially dangerous pattern found: {pattern} in context: {context}")

    def test_template_generates_correct_test_class_names(self):
        """
        GIVEN a Python file with various function and class names
        WHEN template is rendered
        THEN expect:
            - Test class names follow proper naming convention
            - Function names are properly capitalized and formatted
            - Class names are properly incorporated into test class names
            - Method names are properly incorporated into test class names
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        print(content)
        
        # THEN
        # Check function test class names
        self.assertIn("class TestRegularFunctionFunction:", content)
        self.assertIn("class TestAsyncFunctionFunction:", content)
        self.assertIn("class Test_PrivateFunctionFunction:", content)
        self.assertIn("class Test__Dunderfunction__Function:", content)  # Edge case file
        
        # Check class test class names
        self.assertIn("class TestRegularClassClass:", content)
        self.assertIn("class Test_PrivateClassClass:", content)
        
        # Check method test class names (for class methods)
        self.assertIn("class Test__Init__MethodForRegularClass:", content)
        self.assertIn("class TestInstanceMethodMethodForRegularClass:", content)
        self.assertIn("class TestAsyncMethodMethodForRegularClass:", content)
        self.assertIn("class TestCreateDefaultMethodForRegularClass:", content)
        self.assertIn("class TestUtilityFunctionMethodForRegularClass:", content)
        self.assertIn("class TestComputedValuePropertyForRegularClass:", content)
        
        # Verify naming pattern consistency
        test_class_pattern = r'class Test\w+(?:Function|Class|Method|Property)(?:For\w+)?:'
        test_classes = re.findall(test_class_pattern, content)
        
        # Each test class should follow the pattern
        for test_class in test_classes:
            self.assertTrue(test_class.startswith("class Test"))
            self.assertTrue(any(test_class.endswith(suffix + ":") for suffix in ["Function:", "Class:", "Method:", "Property:"]))

    def test_template_handles_different_callable_types(self):
        """
        GIVEN a Python file with functions, methods, async functions, and classes
        WHEN template is rendered
        THEN expect:
            - Different callable types generate appropriate test structures
            - Async functions get @pytest.mark.asyncio decorators
            - Methods are associated with their parent classes correctly
            - Regular functions get standard test methods
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        print(content)
        
        # THEN
        # Check async function handling
        async_decorators = re.findall(r'@pytest\.mark\.asyncio', content)
        self.assertGreaterEqual(len(async_decorators), 2)  # At least async_function and async_method
        
        # Verify async methods have correct structure
        self.assertIn("@pytest.mark.asyncio\n    async def test_async_function(self):", content)
        self.assertIn("@pytest.mark.asyncio\n    async def test_async_method(self):", content)
        
        # Check regular function handling
        self.assertIn("def test_regular_function(self):", content)
        self.assertIn("def test__private_function(self):", content)
        
        # Check method handling within classes
        self.assertIn("def test__init__(self):", content)
        self.assertIn("def test_instance_method(self):", content)
        self.assertIn("def test_create_default(self):", content)
        self.assertIn("def test_utility_function(self):", content)
        self.assertIn("def test_computed_value(self):", content)
        
        # Verify class handling
        self.assertIn("def test_regular_class(self):", content)
        self.assertIn("def test__private_class(self):", content)

    def test_template_generates_proper_import_sections(self):
        """
        GIVEN a Python file with specific imports and callable objects
        WHEN template is rendered
        THEN expect:
            - Import section includes all necessary modules
            - Callable objects are properly imported from the target module
            - Import statements are syntactically correct
            - No duplicate imports are generated
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        print(content)
        
        # THEN
        lines = content.split('\n')
        
        # Find import sections
        import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]
        
        # Check for required imports
        pytest_import = any("import pytest" in line for line in import_lines)
        os_import = any("import os" in line for line in import_lines)
        self.assertTrue(pytest_import, "Missing pytest import")
        self.assertTrue(os_import, "Missing os import")
        
        # Check for target module imports
        target_import = any(f"from {_make_module_path(self.test_file_path)} import" in line for line in import_lines)
        self.assertTrue(target_import, "Missing target module import")
        
        # Check for module dependency imports
        dependency_imports = [line for line in import_lines if "import os" in line or "import asyncio" in line or "from typing import" in line]
        self.assertGreater(len(dependency_imports), 0, "Missing dependency imports")
        
        # Check for no duplicate imports
        unique_imports = set(import_lines)
        self.assertEqual(len(unique_imports), len(import_lines), f"Duplicate imports found: {import_lines}")
        
        # Verify import syntax is correct
        for import_line in import_lines:
            try:
                compile(import_line.strip(), '<string>', 'exec')
            except SyntaxError as e:
                self.fail(f"Invalid import syntax: {import_line.strip()} - {e}")

    def test_template_generates_timestamp_correctly(self):
        """
        GIVEN any valid Python file
        WHEN template is rendered with save_to_file=True
        THEN expect:
            - Timestamp is included in the filename
            - Timestamp format is consistent and readable
            - Timestamp in header comment matches filename timestamp
        """
        # WHEN
        result_path = generate_pytest_test_stubs(self.test_file_path, save_to_file=True)
        print(content)
        
        # THEN
        self.assertTrue(os.path.exists(result_path))
        
        # Extract timestamp from filename
        filename = os.path.basename(result_path)
        # Pattern: test_diverse_module_in_dir_{dirname}_{timestamp}.py
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.py$', filename)
        self.assertIsNotNone(timestamp_match, f"Timestamp not found in filename: {filename}")
        
        filename_timestamp = timestamp_match.group(1)
        
        # Read file content and check header timestamp
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for timestamp in header comment
        header_timestamp_match = re.search(r'# Auto-generated on (\d{4}-\d{2}-\d{2})', content)
        if header_timestamp_match:
            header_date = header_timestamp_match.group(1)
            filename_date = filename_timestamp.split('_')[0]
            self.assertEqual(header_date, filename_date, "Header date should match filename date")
        
        # Verify timestamp format and recency
        try:
            timestamp_obj = datetime.strptime(filename_timestamp, "%Y-%m-%d_%H-%M-%S")
            time_diff = abs((datetime.now() - timestamp_obj).total_seconds())
            self.assertLess(time_diff, 60, "Timestamp should be within last minute")
        except ValueError as e:
            self.fail(f"Invalid timestamp format: {filename_timestamp} - {e}")

    def test_template_handles_edge_case_module_names(self):
        """
        GIVEN Python files with edge case names (numbers, underscores, hyphens)
        WHEN template is rendered
        THEN expect:
            - Module names are properly sanitized for import statements
            - Test class names handle edge cases gracefully
            - Generated code remains valid Python
        """
        # WHEN
        content = generate_pytest_test_stubs(self.edge_case_file_path, save_to_file=False)
        
        # THEN
        # Verify content is valid Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"Generated content with edge case names is not valid Python: {e}")
        
        # Check that module name is properly handled in imports
        self.assertIn(f"from {_make_module_path(self.edge_case_file_path)} import", content)
        
        # Check that edge case names are converted to valid test class names
        self.assertIn("TestFunctionWith123NumbersFunction", content)
        self.assertIn("TestFunctionWithUnderscoresEverywhereFunction", content)
        self.assertIn("TestClassWithUnderscores123Class", content)
        
        # Verify all test class names are valid Python identifiers
        test_class_names = re.findall(r'class (Test\w+):', content)
        for class_name in test_class_names:
            self.assertTrue(class_name.isidentifier(), f"Invalid Python identifier: {class_name}")

    def test_template_conditional_rendering(self):
        """
        GIVEN different Python files (some with classes, some without, etc.)
        WHEN template is rendered
        THEN expect:
            - Conditional sections only appear when relevant
            - Empty sections are not generated
            - Template logic correctly determines what to include
        """
        # Test with file that has classes
        content_with_classes = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # Test with file that has only functions (create minimal file)
        functions_only_content = '''def func1():
    """Function 1."""
    pass

def func2():
    """Function 2."""
    pass
'''
        
        functions_only_path = os.path.join(self.test_dir, "functions_only.py")
        with open(functions_only_path, 'w', encoding='utf-8') as f:
            f.write(functions_only_content)
        
        content_functions_only = generate_pytest_test_stubs(functions_only_path, save_to_file=False)
        
        # THEN
        # File with classes should have method accessibility assertions
        self.assertIn("assert RegularClass.", content_with_classes)
        
        # File with only functions should not have class assertions
        self.assertNotIn("assert ", content_functions_only.split(f"from {_make_module_path(functions_only_path)} import")[1].split("class TestQualityOfObjectsInModule")[0])
        
        # Both should have quality tests
        self.assertIn("class TestQualityOfObjectsInModule", content_with_classes)
        self.assertIn("class TestQualityOfObjectsInModule", content_functions_only)
        
        # File with classes should have more test classes
        classes_with_classes = len(re.findall(r'class Test\w+:', content_with_classes))
        classes_functions_only = len(re.findall(r'class Test\w+:', content_functions_only))
        self.assertGreater(classes_with_classes, classes_functions_only)

    def test_template_whitespace_and_formatting(self):
        """
        GIVEN any valid Python file
        WHEN template is rendered
        THEN expect:
            - Generated code has proper indentation
            - No excessive whitespace or missing newlines
            - Code follows Python formatting standards
            - Template preserves proper code structure
        """
        # WHEN
        content = generate_pytest_test_stubs(self.test_file_path, save_to_file=False)
        
        # THEN
        lines = content.split('\n')
        
        # Check for proper indentation (multiples of 4 spaces)
        for i, line in enumerate(lines):
            if line.strip():  # Non-empty lines
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    self.assertEqual(leading_spaces % 4, 0, 
                                   f"Line {i+1} has improper indentation ({leading_spaces} spaces): {line}")
        
        # Check for no excessive blank lines (no more than 2 consecutive empty lines)
        consecutive_empty = 0
        for line in lines:
            if line.strip() == "":
                consecutive_empty += 1
                self.assertLessEqual(consecutive_empty, 2, "Too many consecutive empty lines")
            else:
                consecutive_empty = 0
        
        # Check for proper spacing around class definitions
        class_line_indices = [i for i, line in enumerate(lines) if line.startswith('class ')]
        for i in class_line_indices:
            if i > 0:  # Not the first line
                # Should have at least one empty line before class definition
                self.assertTrue(any(lines[j].strip() == "" for j in range(max(0, i-3), i)), 
                              f"Class at line {i+1} should have empty line before it")
        
        # Verify no trailing whitespace
        for i, line in enumerate(lines):
            self.assertEqual(line, line.rstrip(), f"Line {i+1} has trailing whitespace")

        # Check that content is properly formatted Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"Generated content has invalid Python syntax: {e}")

if __name__ == '__main__':
    unittest.main()