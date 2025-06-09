"""
Comprehensive test suite for the convert_imports function.

This module implements all test cases outlined in the test plan for converting
between absolute and relative imports in Python files.
"""

import unittest
import tempfile
import os
import shutil
import stat
from pathlib import Path

# Import the function under test
from tools.cli.generate_test_files._generate_test_files._resolve_relative_imports_for_local_modules import convert_imports, convert_imports_batch


class TestConvertImportsFunction(unittest.TestCase):
    """
    Test suite for convert_imports function covering all specified test categories.
    
    This test class implements comprehensive testing for import conversion functionality,
    including basic conversions, edge cases, error handling, and real-world scenarios.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        
        Creates temporary directory structure and helper functions for testing.
        """
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def create_test_file(self, relative_path, content):
        """
        Helper function to create test files with specified content.
        
        Args:
            relative_path (str): Path relative to test directory
            content (str): File content to write
            
        Returns:
            str: Full path to created file
        """
        full_path = os.path.join(self.test_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def verify_file_content(self, file_path, expected_content):
        """
        Helper function to verify file content matches expected content.
        
        Args:
            file_path (str): Path to file to verify
            expected_content (str): Expected file content
            
        Returns:
            bool: True if content matches, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
            return actual_content.strip() == expected_content.strip()
        except Exception:
            return False
    
    def create_package_structure(self, layout_dict, base_path=None):
        """
        Helper function to create nested package structures.
        
        Args:
            layout_dict (dict): Dictionary describing package structure
            base_path (str): Base path for package creation
            
        Returns:
            str: Path to created package structure
        """
        if base_path is None:
            base_path = self.test_dir
        
        for name, content in layout_dict.items():
            full_path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(full_path, exist_ok=True)
                # Create __init__.py for packages
                init_file = os.path.join(full_path, '__init__.py')
                with open(init_file, 'w') as f:
                    f.write('# Package init file\n')
                self.create_package_structure(content, full_path)
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        return base_path

    # Test Category 1: Basic Import Conversion
    
    def test_absolute_to_relative_conversion(self):
        """
        Test converting absolute imports to relative imports.
        
        GIVEN: A Python file with absolute imports within the same package
        WHEN: convert_imports is called with to_relative=True
        THEN: Absolute imports should be converted to relative imports
        """
        # Create test file with absolute imports
        test_content = '''import os
import sys
from mypackage.module1 import function1
from mypackage.subpackage.module2 import Class2
from mypackage.utils.helpers import helper_func
from external_package import external_func
'''
        test_file = self.create_test_file('mypackage/module.py', test_content)
        
        # Create package structure to ensure imports are valid
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        self.create_test_file('mypackage/subpackage/__init__.py', '')
        self.create_test_file('mypackage/subpackage/module2.py', 'class Class2: pass')
        self.create_test_file('mypackage/utils/__init__.py', '')
        self.create_test_file('mypackage/utils/helpers.py', 'def helper_func(): pass')
        
        # Call function under test
        result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
        
        # Verify return value indicates changes were made
        self.assertTrue(result)
        
        # Verify the file content was actually changed
        with open(test_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Check that some absolute imports were converted to relative
        self.assertIn('from .module1 import function1', updated_content)
        self.assertIn('from .subpackage.module2 import Class2', updated_content)
        self.assertIn('from .utils.helpers import helper_func', updated_content)
        # External imports should remain unchanged
        self.assertIn('from external_package import external_func', updated_content)
    
    def test_relative_to_absolute_conversion(self):
        """
        Test converting relative imports to absolute imports.
        
        GIVEN: A Python file with relative imports
        WHEN: convert_imports is called with to_relative=False
        THEN: Relative imports should be converted to absolute imports
        """
        # Create test file with relative imports
        test_content = '''import os
import sys
from .module1 import function1
from .subpackage.module2 import Class2
from .utils.helpers import helper_func
from external_package import external_func
'''
        test_file = self.create_test_file('mypackage/module.py', test_content)
        
        # Create package structure to ensure imports are valid
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        self.create_test_file('mypackage/subpackage/__init__.py', '')
        self.create_test_file('mypackage/subpackage/module2.py', 'class Class2: pass')
        self.create_test_file('mypackage/utils/__init__.py', '')
        self.create_test_file('mypackage/utils/helpers.py', 'def helper_func(): pass')
        
        # Call function under test
        result = convert_imports(test_file, to_relative=False, application_directories=[self.test_dir])
        
        # Verify return value indicates changes were made
        self.assertTrue(result)
        
        # Verify the file content was actually changed
        with open(test_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Check that relative imports were converted to absolute
        self.assertIn('from mypackage.module1 import function1', updated_content)
        self.assertIn('from mypackage.subpackage.module2 import Class2', updated_content)
        self.assertIn('from mypackage.utils.helpers import helper_func', updated_content)
        # External imports should remain unchanged
        self.assertIn('from external_package import external_func', updated_content)
    
    def test_no_conversion_needed(self):
        """
        Test when no conversion is needed.
        
        GIVEN: A Python file already in the target import format
        WHEN: convert_imports is called
        THEN: No changes should be made and function should return False
        """
        # Create test file that doesn't need conversion (only stdlib and external imports)
        no_conversion_content = '''import os
import sys
from external_package import external_func
'''
        test_file = self.create_test_file('mypackage/module.py', no_conversion_content)
        
        # Call function under test
        result = convert_imports(test_file, application_directories=[self.test_dir])
        
        # Verify no changes were made
        self.assertFalse(result)

    # Test Category 2: Error Handling
    
    def test_file_outside_application_directories(self):
        """
        Test file outside all specified application directories.
        
        GIVEN: A Python file outside all application directories
        WHEN: convert_imports is called
        THEN: ValueError should be raised
        """
        # Create file outside test directory
        outside_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, outside_dir)
        
        test_file = os.path.join(outside_dir, 'module.py')
        with open(test_file, 'w') as f:
            f.write('import os\n')
        
        # Should raise ValueError since file is outside application directories
        with self.assertRaises(ValueError) as cm:
            convert_imports(test_file, application_directories=[self.test_dir])
        
        self.assertIn('cannot be resolved relative to any application directory', str(cm.exception))
    
    def test_invalid_python_syntax(self):
        """
        Test handling of files with syntax errors.
        
        GIVEN: A file with syntax errors
        WHEN: convert_imports attempts to process it
        THEN: SyntaxError should be raised
        """
        invalid_syntax = '''
import os
def invalid_function(
    # Missing closing parenthesis and colon
'''
        test_file = self.create_test_file('mypackage/invalid.py', invalid_syntax)
        
        with self.assertRaises(SyntaxError):
            convert_imports(test_file, application_directories=[self.test_dir])
    
    def test_non_utf8_encoding(self):
        """
        Test handling of files with non-UTF-8 encoding.
        
        GIVEN: A file with non-UTF-8 encoding
        WHEN: convert_imports attempts to read it
        THEN: UnicodeDecodeError should be raised
        """
        # Create file with Latin-1 encoding containing non-ASCII characters
        test_file_path = os.path.join(self.test_dir, 'latin1_file.py')
        with open(test_file_path, 'w', encoding='latin-1') as f:
            f.write('# This file has special characters: ñáéíóú\nimport os\n')
        
        with self.assertRaises(UnicodeDecodeError):
            convert_imports(test_file_path, application_directories=[self.test_dir])
    
    def test_empty_file(self):
        """
        Test handling of empty files.
        
        GIVEN: An empty file
        WHEN: convert_imports processes it
        THEN: Should return False and not raise errors
        """
        empty_file = self.create_test_file('mypackage/empty.py', '')
        
        result = convert_imports(empty_file, application_directories=[self.test_dir])
        self.assertFalse(result)
    
    def test_comments_only_file(self):
        """
        Test handling of files with only comments.
        
        GIVEN: A file with only comments
        WHEN: convert_imports processes it
        THEN: Should return False and not raise errors
        """
        comments_file = self.create_test_file('mypackage/comments.py', '''
# This file only has comments
# No import statements here
''')
        
        result = convert_imports(comments_file, application_directories=[self.test_dir])
        self.assertFalse(result)

    # Test Category 3: Dry Run Functionality
    
    def test_dry_run_detection(self):
        """
        Test dry run detection functionality.
        
        GIVEN: A file that would normally be modified
        WHEN: convert_imports is called with dry_run=True
        THEN: Function should return True but not modify file
        """
        test_content = '''from mypackage.module1 import function1
'''
        test_file = self.create_test_file('mypackage/module.py', test_content)
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        
        original_content = test_content
        
        result = convert_imports(test_file, to_relative=True, dry_run=True, application_directories=[self.test_dir])
        
        self.assertTrue(result)
        # Verify file content unchanged
        with open(test_file, 'r', encoding='utf-8') as f:
            actual_content = f.read()
        self.assertEqual(actual_content.strip(), original_content.strip())
    
    def test_dry_run_no_changes(self):
        """
        Test dry run when no changes are needed.
        
        GIVEN: A file that requires no modifications
        WHEN: convert_imports is called with dry_run=True
        THEN: Should return False and file should remain unchanged
        """
        no_changes_content = '''import os
from external_package import func
'''
        test_file = self.create_test_file('mypackage/module.py', no_changes_content)
        
        result = convert_imports(test_file, dry_run=True, application_directories=[self.test_dir])
        
        self.assertFalse(result)

    # Test Category 4: Batch Processing Tests
    
    def test_batch_processing_success(self):
        """
        Test successful batch processing.
        
        GIVEN: Multiple valid Python files with convertible imports
        WHEN: convert_imports_batch is called
        THEN: All files should be processed correctly
        """
        # Create multiple test files
        files = []
        for i in range(3):
            content = f'''from mypackage.module{i} import function{i}
'''
            file_path = self.create_test_file(f'mypackage/test{i}.py', content)
            files.append(file_path)
            
            # Create the imported modules
            self.create_test_file(f'mypackage/module{i}.py', f'def function{i}(): pass')
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        
        # Test batch conversion
        changed_count = convert_imports_batch(files, to_relative=True, application_directories=[self.test_dir])
        
        self.assertEqual(changed_count, 3)
    
    def test_batch_processing_mixed_results(self):
        """
        Test batch processing with mixed results.
        
        GIVEN: List with various file types and conditions
        WHEN: convert_imports_batch is called
        THEN: Valid conversions should succeed, errors handled per-file
        """
        # Create mixed file scenarios
        good_content = '''from mypackage.module1 import function1
'''
        good_file = self.create_test_file('mypackage/good.py', good_content)
        
        no_change_content = '''import os
'''
        no_change_file = self.create_test_file('mypackage/no_change.py', no_change_content)
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        
        files = [good_file, no_change_file, 'nonexistent.py']
        
        changed_count = convert_imports_batch(files, to_relative=True, application_directories=[self.test_dir])
        
        # Only the good file should be changed
        self.assertEqual(changed_count, 1)
    
    def test_batch_processing_empty_list(self):
        """
        Test batch processing with empty file list.
        
        GIVEN: Empty list of files
        WHEN: convert_imports_batch is called
        THEN: Should return 0 and handle gracefully
        """
        changed_count = convert_imports_batch([], application_directories=[self.test_dir])
        
        self.assertEqual(changed_count, 0)
    
    def test_batch_dry_run(self):
        """
        Test batch processing with dry run.
        
        GIVEN: Multiple files for batch processing
        WHEN: convert_imports_batch is called with dry_run=True
        THEN: Should return count without modifying files
        """
        files = []
        original_contents = []
        
        for i in range(2):
            content = f'''from mypackage.module{i} import function{i}
'''
            file_path = self.create_test_file(f'mypackage/test{i}.py', content)
            files.append(file_path)
            original_contents.append(content)
            
            # Create the imported modules
            self.create_test_file(f'mypackage/module{i}.py', f'def function{i}(): pass')
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        
        changed_count = convert_imports_batch(files, to_relative=True, dry_run=True, application_directories=[self.test_dir])
        
        self.assertEqual(changed_count, 2)
        
        # Verify files weren't actually changed
        for i, file_path in enumerate(files):
            with open(file_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
            self.assertEqual(actual_content.strip(), original_contents[i].strip())

    # Test Category 5: Complex Package Structures
    
    def test_nested_package_structure(self):
        """
        Test deep package hierarchy handling.
        
        GIVEN: Deep package hierarchy
        WHEN: Converting between import formats
        THEN: Correct relative depth should be calculated
        """
        # Create deep package structure
        package_structure = {
            'mypackage': {
                'subpackage': {
                    'subsubpackage': {
                        'module.py': '''from mypackage.subpackage.another_module import func
from mypackage.utils.helper import helper
''',
                        '__init__.py': ''
                    },
                    'another_module.py': 'def func(): pass\n',
                    '__init__.py': ''
                },
                'utils': {
                    'helper.py': 'def helper(): pass\n',
                    '__init__.py': ''
                },
                '__init__.py': ''
            }
        }
        
        self.create_package_structure(package_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/subpackage/subsubpackage/module.py')
        
        result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
        
        self.assertTrue(result)
        
        # Verify relative imports were created correctly
        with open(test_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        self.assertIn('from ..another_module import func', updated_content)
        self.assertIn('from ...utils.helper import helper', updated_content)
    
    def test_same_level_imports(self):
        """
        Test modules importing from the same directory level.
        
        GIVEN: Modules importing from the same directory level
        WHEN: Converting between import formats
        THEN: Single dot relative imports should be used correctly
        """
        package_structure = {
            'mypackage': {
                'module1.py': 'def func1(): pass\n',
                'module2.py': '''from mypackage.module1 import func1
''',
                '__init__.py': ''
            }
        }
        
        self.create_package_structure(package_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/module2.py')
        
        result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
        
        self.assertTrue(result)
        
        # Verify single dot relative import
        with open(test_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        self.assertIn('from .module1 import func1', updated_content)

    # Test Category 6: Parameter Validation
    
    def test_default_parameter_behavior(self):
        """
        Test default parameter behavior.
        
        GIVEN: Function calls with minimal parameters
        WHEN: convert_imports uses default values
        THEN: Default behavior should be applied correctly
        """
        test_content = '''from mypackage.module1 import function1
'''
        test_file = self.create_test_file('mypackage/module.py', test_content)
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        
        # Test with minimal parameters (should use defaults)
        result = convert_imports(test_file)
        
        # Default behavior is to convert to absolute (to_relative=False)
        # and use ['.', 'src'] as application_directories
        # Since our test file is in current directory, this should work
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,
        catchbreak=True
    )
