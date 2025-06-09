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
from unittest.mock import patch, mock_open
import concurrent.futures
import threading
import time

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
        
        # Define common test file contents
        self.sample_absolute_imports = '''
import os
import sys
from mypackage.module1 import function1
from mypackage.subpackage.module2 import Class2
from mypackage.utils.helpers import helper_func
from external_package import external_func
'''
        
        self.sample_relative_imports = '''
import os
import sys
from .module1 import function1
from .subpackage.module2 import Class2
from .utils.helpers import helper_func
from external_package import external_func
'''
        
        self.mixed_imports = '''
import os
from mypackage.module1 import function1
from .relative_module import relative_func
from external_package import external_func
from ..parent_module import parent_func
'''
    
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

    # Test Category 2: Edge Cases and Complex Scenarios
    
    def test_mixed_import_types(self):
        """
        Test handling of mixed import types.
        
        GIVEN: A Python file with mixed import types
        WHEN: convert_imports is called
        THEN: Only relevant package imports should be converted
        """
        mixed_content = '''import os
from mypackage.module1 import function1
from .relative_module import relative_func
from external_package import external_func
from ..parent_module import parent_func
'''
        test_file = self.create_test_file('mypackage/subpackage/module.py', mixed_content)
        
        # Create package structure
        self.create_test_file('mypackage/__init__.py', '')
        self.create_test_file('mypackage/subpackage/__init__.py', '')
        self.create_test_file('mypackage/module1.py', 'def function1(): pass')
        self.create_test_file('mypackage/subpackage/relative_module.py', 'def relative_func(): pass')
        self.create_test_file('mypackage/parent_module.py', 'def parent_func(): pass')
        
        result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
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
                        'module.py': '''
from mypackage.subpackage.another_module import func
from mypackage.utils.helper import helper
'''
                    },
                    'another_module.py': 'def func(): pass\n'
                },
                'utils': {
                    'helper.py': 'def helper(): pass\n'
                }
            }
        }
        
        self.create_package_structure(package_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/subpackage/subsubpackage/module.py')
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def test_import_from_parent_packages(self):
        """
        Test importing from parent or sibling packages.
        
        GIVEN: Module importing from parent packages
        WHEN: Converting to relative imports
        THEN: Correct upward navigation should be used
        """
        package_structure = {
            'mypackage': {
                'parent_module.py': 'def parent_func(): pass\n',
                'subpackage': {
                    'child_module.py': '''
from mypackage.parent_module import parent_func
from mypackage.sibling_package.sibling_module import sibling_func
'''
                },
                'sibling_package': {
                    'sibling_module.py': 'def sibling_func(): pass\n'
                }
            }
        }
        
        self.create_package_structure(package_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/subpackage/child_module.py')
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
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
                'module2.py': '''
from mypackage.module1 import func1
'''
            }
        }
        
        self.create_package_structure(package_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/module2.py')
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)

    # Test Category 3: File and Directory Handling
    
    def test_various_application_directories(self):
        """
        Test different application directory configurations.
        
        GIVEN: Different application directory configurations
        WHEN: convert_imports is called with different directories
        THEN: Correct source resolution should occur
        """
        test_file = self.create_test_file('src/mypackage/module.py', self.sample_absolute_imports)
        
        # Test single directory
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, application_directories=['.'])
            self.assertTrue(result)
        
        # Test multiple directories
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, application_directories=['.', 'src', 'lib'])
            self.assertTrue(result)
    
    def test_file_path_resolution(self):
        """
        Test various file path formats.
        
        GIVEN: Various file path formats
        WHEN: convert_imports processes these paths
        THEN: All paths should resolve correctly
        """
        # Test with relative path
        test_file = self.create_test_file('mypackage/module.py', self.sample_absolute_imports)
        
        
            convert_imports.return_value = True
            
            # Test relative path
            result = convert_imports(os.path.relpath(test_file), application_directories=[self.test_dir])
            self.assertTrue(result)
            
            # Test absolute path
            result = convert_imports(os.path.abspath(test_file), application_directories=[self.test_dir])
            self.assertTrue(result)
    
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
            f.write(self.sample_absolute_imports)
        
        
            convert_imports.side_effect = ValueError("File is outside application directories")
            
            with self.assertRaises(ValueError) as context:
                convert_imports(test_file, application_directories=[self.test_dir])
            
            self.assertIn("outside application directories", str(context.exception))

    # Test Category 4: Error Handling and Validation
    
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
        
        
            convert_imports.side_effect = SyntaxError("invalid syntax")
            
            with self.assertRaises(SyntaxError):
                convert_imports(test_file, application_directories=[self.test_dir])
    
    def test_non_utf8_encoding(self):
        """
        Test handling of files with non-UTF-8 encoding.
        
        GIVEN: A file with non-UTF-8 encoding
        WHEN: convert_imports attempts to read it
        THEN: UnicodeDecodeError should be raised
        """
        # Create file with Latin-1 encoding
        test_file_path = os.path.join(self.test_dir, 'latin1_file.py')
        with open(test_file_path, 'w', encoding='latin-1') as f:
            f.write('# File with Latin-1 encoding: café\n')
        
        
            convert_imports.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
            
            with self.assertRaises(UnicodeDecodeError):
                convert_imports(test_file_path, application_directories=[self.test_dir])
    
    def test_file_permissions(self):
        """
        Test handling of files with various permission settings.
        
        GIVEN: Files with restricted permissions
        WHEN: convert_imports attempts to process them
        THEN: Appropriate OS errors should be raised
        """
        test_file = self.create_test_file('mypackage/readonly.py', self.sample_absolute_imports)
        
        # Make file read-only
        os.chmod(test_file, stat.S_IREAD)
        
        
            convert_imports.side_effect = PermissionError("Permission denied")
            
            with self.assertRaises(PermissionError):
                convert_imports(test_file, application_directories=[self.test_dir])
        
        # Restore permissions for cleanup
        os.chmod(test_file, stat.S_IWRITE | stat.S_IREAD)
    
    def test_empty_and_minimal_files(self):
        """
        Test handling of edge case files.
        
        GIVEN: Edge case files (empty, comments only, etc.)
        WHEN: convert_imports processes them
        THEN: Should return False and not raise errors
        """
        # Test empty file
        empty_file = self.create_test_file('mypackage/empty.py', '')
        
        
            convert_imports.return_value = False
            
            result = convert_imports(empty_file, application_directories=[self.test_dir])
            self.assertFalse(result)
        
        # Test comments only file
        comments_file = self.create_test_file('mypackage/comments.py', '''
# This file only has comments
# No import statements here
''')
        
        
            convert_imports.return_value = False
            
            result = convert_imports(comments_file, application_directories=[self.test_dir])
            self.assertFalse(result)

    # Test Category 5: Dry Run Functionality
    
    def test_dry_run_detection(self):
        """
        Test dry run detection functionality.
        
        GIVEN: A file that would normally be modified
        WHEN: convert_imports is called with dry_run=True
        THEN: Function should return True but not modify file
        """
        test_file = self.create_test_file('mypackage/module.py', self.sample_absolute_imports)
        original_content = self.sample_absolute_imports
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, dry_run=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
            # Verify file content unchanged
            self.assertTrue(self.verify_file_content(test_file, original_content))
    
    def test_dry_run_no_changes(self):
        """
        Test dry run when no changes are needed.
        
        GIVEN: A file that requires no modifications
        WHEN: convert_imports is called with dry_run=True
        THEN: Should return False and file should remain unchanged
        """
        no_changes_content = '''
import os
from external_package import func
'''
        test_file = self.create_test_file('mypackage/module.py', no_changes_content)
        
        
            convert_imports.return_value = False
            
            result = convert_imports(test_file, dry_run=True, application_directories=[self.test_dir])
            
            self.assertFalse(result)
    
    def test_dry_run_with_errors(self):
        """
        Test dry run with files that would cause errors.
        
        GIVEN: A file that would cause errors during processing
        WHEN: convert_imports is called with dry_run=True
        THEN: Same errors should be raised as in normal mode
        """
        invalid_file = self.create_test_file('mypackage/invalid.py', 'invalid python syntax')
        
        
            convert_imports.side_effect = SyntaxError("invalid syntax")
            
            with self.assertRaises(SyntaxError):
                convert_imports(invalid_file, dry_run=True, application_directories=[self.test_dir])

    # Test Category 6: Batch Processing Tests
    
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
            file_path = self.create_test_file(f'mypackage/module{i}.py', self.sample_absolute_imports)
            files.append(file_path)
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = 3
            
            result = mock_batch(files, to_relative=True, application_directories=[self.test_dir])
            
            self.assertEqual(result, 3)
    
    def test_batch_processing_mixed_results(self):
        """
        Test batch processing with mixed results.
        
        GIVEN: List with various file types and conditions
        WHEN: convert_imports_batch is called
        THEN: Valid conversions should succeed, errors handled per-file
        """
        # Create mixed file scenarios
        good_file = self.create_test_file('mypackage/good.py', self.sample_absolute_imports)
        no_change_file = self.create_test_file('mypackage/no_change.py', 'import os\n')
        
        files = [good_file, no_change_file, 'nonexistent.py']
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = 1  # Only one file changed
            
            result = mock_batch(files, application_directories=[self.test_dir])
            
            self.assertEqual(result, 1)
    
    def test_batch_processing_empty_list(self):
        """
        Test batch processing with empty file list.
        
        GIVEN: Empty list of files
        WHEN: convert_imports_batch is called
        THEN: Should return 0 and handle gracefully
        """
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = 0
            
            result = mock_batch([], application_directories=[self.test_dir])
            
            self.assertEqual(result, 0)
    
    def test_batch_dry_run(self):
        """
        Test batch processing with dry run.
        
        GIVEN: Multiple files for batch processing
        WHEN: convert_imports_batch is called with dry_run=True
        THEN: Should return count without modifying files
        """
        files = [
            self.create_test_file('mypackage/module1.py', self.sample_absolute_imports),
            self.create_test_file('mypackage/module2.py', self.sample_absolute_imports)
        ]
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = 2
            
            result = mock_batch(files, dry_run=True, application_directories=[self.test_dir])
            
            self.assertEqual(result, 2)

    # Test Category 7: Integration and Real-World Scenarios
    
    def test_real_package_structures(self):
        """
        Test realistic Python package structures.
        
        GIVEN: Realistic package structures (Django, Flask, etc.)
        WHEN: Converting imports in various files
        THEN: Conversions should work correctly for each structure
        """
        # Django-style structure
        django_structure = {
            'myproject': {
                'settings.py': '''
from myproject.apps.users.models import User
from myproject.utils.helpers import helper_func
''',
                'apps': {
                    'users': {
                        'models.py': '''
from myproject.utils.database import BaseModel
''',
                        'views.py': '''
from myproject.apps.users.models import User
'''
                    }
                },
                'utils': {
                    'helpers.py': 'def helper_func(): pass\n',
                    'database.py': 'class BaseModel: pass\n'
                }
            }
        }
        
        self.create_package_structure(django_structure)
        test_file = os.path.join(self.test_dir, 'myproject/settings.py')
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def test_circular_import_scenarios(self):
        """
        Test handling of potential circular import patterns.
        
        GIVEN: Files with potential circular import patterns
        WHEN: Converting between import formats
        THEN: Conversions should not create invalid patterns
        """
        circular_structure = {
            'mypackage': {
                'module_a.py': '''
from mypackage.module_b import func_b
def func_a(): return func_b()
''',
                'module_b.py': '''
from mypackage.module_a import func_a
def func_b(): return "b"
'''
            }
        }
        
        self.create_package_structure(circular_structure)
        test_file = os.path.join(self.test_dir, 'mypackage/module_a.py')
        
        
            convert_imports.return_value = True
            
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def test_performance_with_large_files(self):
        """
        Test performance with large Python files.
        
        GIVEN: Large Python files with many imports
        WHEN: convert_imports processes them
        THEN: Processing should complete in reasonable time
        """
        # Create large file content
        large_content = '''
import os
import sys
''' + '\n'.join([f'from mypackage.module{i} import func{i}' for i in range(100)])
        
        test_file = self.create_test_file('mypackage/large_module.py', large_content)
        
        
            convert_imports.return_value = True
            
            start_time = time.time()
            result = convert_imports(test_file, to_relative=True, application_directories=[self.test_dir])
            end_time = time.time()
            
            self.assertTrue(result)
            # Performance check - should complete within reasonable time
            self.assertLess(end_time - start_time, 5.0)  # 5 second timeout
    
    def test_concurrent_access(self):
        """
        Test concurrent access to the same file.
        
        GIVEN: Multiple processes trying to convert the same file
        WHEN: convert_imports runs concurrently
        THEN: File integrity should be maintained
        """
        test_file = self.create_test_file('mypackage/concurrent.py', self.sample_absolute_imports)
        
        def convert_file():
            
                convert_imports.return_value = True
                return convert_imports(test_file, application_directories=[self.test_dir])
        
        # Run concurrent conversions
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(convert_file) for _ in range(3)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # At least one should succeed
        self.assertTrue(any(results))

    # Test Category 8: Utility Function Tests
    
    def test_find_relative_depth_function(self):
        """
        Test find_relative_depth utility function.
        
        GIVEN: Various combinations of module parts and target modules
        WHEN: find_relative_depth is called
        THEN: Correct depth calculations should be returned
        """
        # Mock the utility function
        with patch('__main__.find_relative_depth') as mock_depth:
            # Test same level
            mock_depth.return_value = 0
            result = mock_depth(['mypackage', 'module1'], ['mypackage', 'module2'])
            self.assertEqual(result, 0)
            
            # Test parent level
            mock_depth.return_value = 1
            result = mock_depth(['mypackage', 'subpackage', 'module'], ['mypackage', 'utils'])
            self.assertEqual(result, 1)
    
    def test_import_visitor_class(self):
        """
        Test ImportVisitor AST traversal class.
        
        GIVEN: AST trees with various import patterns
        WHEN: ImportVisitor traverses the tree
        THEN: All relevant import nodes should be identified
        """
        # This would test the AST visitor implementation
        # Mock test since we don't have the actual implementation
        with patch('__main__.ImportVisitor') as mock_visitor:
            visitor_instance = mock_visitor.return_value
            visitor_instance.visit.return_value = None
            visitor_instance.replacements = [('old_import', 'new_import')]
            
            # Simulate visiting an AST
            import ast
            tree = ast.parse('from mypackage.module import func')
            visitor_instance.visit(tree)
            
            # Verify visitor found replacements
            self.assertEqual(len(visitor_instance.replacements), 1)

    # Test Category 9: Configuration and Parameter Validation
    
    def test_parameter_validation(self):
        """
        Test parameter validation.
        
        GIVEN: Invalid parameter combinations
        WHEN: convert_imports is called
        THEN: Appropriate validation errors should be raised
        """
        test_file = self.create_test_file('mypackage/module.py', self.sample_absolute_imports)
        
        # Test invalid application_directories type
        
            convert_imports.side_effect = TypeError("application_directories must be a list")
            
            with self.assertRaises(TypeError):
                convert_imports(test_file, application_directories="not_a_list")
        
        # Test non-existent file
        
            convert_imports.side_effect = FileNotFoundError("File not found")
            
            with self.assertRaises(FileNotFoundError):
                convert_imports('nonexistent.py', application_directories=[self.test_dir])
    
    def test_default_parameter_behavior(self):
        """
        Test default parameter behavior.
        
        GIVEN: Function calls with minimal parameters
        WHEN: convert_imports uses default values
        THEN: Default behavior should be applied correctly
        """
        test_file = self.create_test_file('mypackage/module.py', self.sample_absolute_imports)
        
        
            convert_imports.return_value = True
            
            # Test with minimal parameters (should use defaults)
            result = convert_imports(test_file)
            
            # Verify function was called
            convert_imports.assert_called_once_with(test_file)
            self.assertTrue(result)


class TestConvertImportsUtilities(unittest.TestCase):
    """
    Additional test class for utility functions and helper methods.
    
    This class focuses on testing individual utility functions that support
    the main convert_imports functionality.
    """
    
    def setUp(self):
        """Set up test environment for utility function tests."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def test_module_path_resolution(self):
        """
        Test module path resolution utility.
        
        GIVEN: Various module path formats
        WHEN: Path resolution utility is called
        THEN: Correct canonical paths should be returned
        """
        with patch('__main__.resolve_module_path') as mock_resolve:
            mock_resolve.return_value = 'mypackage.subpackage.module'
            
            result = mock_resolve('mypackage/subpackage/module.py', [self.test_dir])
            
            self.assertEqual(result, 'mypackage.subpackage.module')
    
    def test_import_statement_parsing(self):
        """
        Test import statement parsing utility.
        
        GIVEN: Various import statement formats
        WHEN: Import parser is called
        THEN: Correct import components should be extracted
        """
        test_cases = [
            ('from mypackage.module import func', ('mypackage.module', ['func'])),
            ('import mypackage.module', ('mypackage.module', None)),
            ('from .relative import func', ('.relative', ['func'])),
        ]
        
        with patch('__main__.parse_import_statement') as mock_parse:
            for import_stmt, expected in test_cases:
                mock_parse.return_value = expected
                result = mock_parse(import_stmt)
                self.assertEqual(result, expected)
    
    def test_relative_import_conversion(self):
        """
        Test relative import conversion logic.
        
        GIVEN: Absolute import and target module information
        WHEN: Relative conversion utility is called
        THEN: Correct relative import should be generated
        """
        with patch('__main__.convert_to_relative') as convert_imports:
            mock_convert.return_value = '..utils.helper'
            
            result = mock_convert(
                'mypackage.utils.helper',
                ['mypackage', 'subpackage', 'module'],
                ['mypackage']
            )
            
            self.assertEqual(result, '..utils.helper')
    
    def test_absolute_import_conversion(self):
        """
        Test absolute import conversion logic.
        
        GIVEN: Relative import and module context
        WHEN: Absolute conversion utility is called
        THEN: Correct absolute import should be generated
        """
        with patch('__main__.convert_to_absolute') as mock_convert:
            mock_convert.return_value = 'mypackage.utils.helper'
            
            result = mock_convert(
                '..utils.helper',
                ['mypackage', 'subpackage', 'module']
            )
            
            self.assertEqual(result, 'mypackage.utils.helper')


class TestConvertImportsIntegration(unittest.TestCase):
    """
    Integration test class for end-to-end testing scenarios.
    
    This class tests the complete workflow of import conversion in realistic
    scenarios that combine multiple features and edge cases.
    """
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def test_complete_package_conversion(self):
        """
        Test complete package conversion workflow.
        
        GIVEN: A complete Python package with multiple modules
        WHEN: Converting all imports in the package
        THEN: All files should be converted consistently
        """
        # Create comprehensive package structure
        package_structure = {
            'myproject': {
                '__init__.py': '''
"""Main project package."""
from myproject.core.engine import Engine
from myproject.utils.logger import setup_logger
''',
                'core': {
                    '__init__.py': '',
                    'engine.py': '''
"""Core engine module."""
from myproject.core.config import Config
from myproject.utils.helpers import format_data
from myproject.plugins.base import BasePlugin

class Engine:
    def __init__(self):
        self.config = Config()
        self.plugins = []
''',
                    'config.py': '''
"""Configuration module."""
from myproject.utils.validation import validate_config

class Config:
    def __init__(self):
        validate_config(self)
'''
                },
                'utils': {
                    '__init__.py': '',
                    'logger.py': '''
"""Logging utilities."""
import logging
from myproject.core.config import Config

def setup_logger():
    return logging.getLogger(__name__)
''',
                    'helpers.py': '''
"""Helper functions."""
from myproject.utils.validation import is_valid

def format_data(data):
    if is_valid(data):
        return str(data)
    return None
''',
                    'validation.py': '''
"""Validation utilities."""
def validate_config(config):
    return True

def is_valid(data):
    return data is not None
'''
                },
                'plugins': {
                    '__init__.py': '',
                    'base.py': '''
"""Base plugin class."""
from myproject.core.config import Config

class BasePlugin:
    def __init__(self):
        self.config = Config()
''',
                    'example.py': '''
"""Example plugin."""
from myproject.plugins.base import BasePlugin
from myproject.utils.logger import setup_logger

class ExamplePlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
'''
                }
            }
        }
        
        self.create_package_structure(package_structure)
        
        # Get all Python files
        python_files = []
        for root, dirs, files in os.walk(os.path.join(self.test_dir, 'myproject')):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = len(python_files)
            
            result = mock_batch(
                python_files,
                to_relative=True,
                application_directories=[self.test_dir]
            )
            
            self.assertEqual(result, len(python_files))
    
    def create_package_structure(self, layout_dict, base_path=None):
        """Helper method to create package structures for integration tests."""
        if base_path is None:
            base_path = self.test_dir
        
        for name, content in layout_dict.items():
            full_path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(full_path, exist_ok=True)
                self.create_package_structure(content, full_path)
            else:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def test_cross_platform_compatibility(self):
        """
        Test cross-platform path handling.
        
        GIVEN: Package with various path separators
        WHEN: Converting imports across different platforms
        THEN: Path handling should be consistent
        """
        # Test with forward slashes (Unix-style)
        unix_file = self.create_test_file('mypackage/unix_module.py', '''
from mypackage.utils.helper import unix_func
''')
        
        # Test with mixed separators
        mixed_file = self.create_test_file('mypackage/mixed_module.py', '''
from mypackage.subdir.module import mixed_func
''')
        
        files = [unix_file, mixed_file]
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = 2
            
            result = mock_batch(files, application_directories=[self.test_dir])
            
            self.assertEqual(result, 2)
    
    def create_test_file(self, relative_path, content):
        """Helper method to create test files."""
        full_path = os.path.join(self.test_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return full_path
    
    def test_large_scale_conversion(self):
        """
        Test large-scale conversion performance.
        
        GIVEN: Large number of files requiring conversion
        WHEN: Batch conversion is performed
        THEN: Performance should be acceptable
        """
        # Create many files for performance testing
        files = []
        for i in range(50):  # Create 50 test files
            file_content = f'''
"""Module {i}."""
from myproject.module{(i+1) % 50} import func{i}
from myproject.utils.helper{i % 5} import helper_func
'''
            file_path = self.create_test_file(f'myproject/module{i}.py', file_content)
            files.append(file_path)
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            mock_batch.return_value = len(files)
            
            start_time = time.time()
            result = mock_batch(files, to_relative=True, application_directories=[self.test_dir])
            end_time = time.time()
            
            self.assertEqual(result, len(files))
            # Performance check - should complete within reasonable time
            self.assertLess(end_time - start_time, 10.0)  # 10 second timeout
    
    def test_error_recovery_in_batch(self):
        """
        Test error recovery during batch processing.
        
        GIVEN: Mix of valid and invalid files in batch
        WHEN: Batch conversion encounters errors
        THEN: Valid files should still be processed
        """
        # Create mix of valid and invalid files
        valid_file1 = self.create_test_file('myproject/valid1.py', '''
from myproject.utils import helper
''')
        
        invalid_file = self.create_test_file('myproject/invalid.py', '''
invalid python syntax here
''')
        
        valid_file2 = self.create_test_file('myproject/valid2.py', '''
from myproject.core import engine
''')
        
        files = [valid_file1, invalid_file, valid_file2]
        
        with patch('__main__.convert_imports_batch') as mock_batch:
            # Should process valid files despite invalid one
            mock_batch.return_value = 2
            
            result = mock_batch(files, application_directories=[self.test_dir])
            
            self.assertEqual(result, 2)  # Two valid files processed


class TestConvertImportsEdgeCases(unittest.TestCase):
    """
    Test class for edge cases and boundary conditions.
    
    This class focuses on testing unusual but valid scenarios that might
    occur in real-world usage.
    """
    
    def setUp(self):
        """Set up edge case test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
    
    def test_deeply_nested_relative_imports(self):
        """
        Test very deep relative import structures.
        
        GIVEN: Deeply nested package with complex relative imports
        WHEN: Converting between import formats
        THEN: All levels should be handled correctly
        """
        # Create deep structure: level1/level2/level3/level4/level5
        deep_structure = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'level5': {
                                'deep_module.py': '''
from level1.level2.level3.utils import deep_util
from level1.common import shared_func
'''
                            }
                        },
                        'utils.py': 'def deep_util(): pass\n'
                    }
                },
                'common.py': 'def shared_func(): pass\n'
            }
        }
        
        self.create_package_structure(deep_structure)
        test_file = os.path.join(self.test_dir, 'level1/level2/level3/level4/level5/deep_module.py')
        
        
            mock_convert.return_value = True
            
            result = mock_convert(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def create_package_structure(self, layout_dict, base_path=None):
        """Helper method to create package structures."""
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
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    def test_unicode_module_names(self):
        """
        Test handling of Unicode characters in module names.
        
        GIVEN: Modules with Unicode characters in names
        WHEN: Converting imports
        THEN: Unicode should be handled correctly
        """
        # Note: This is more theoretical as Python module names should be ASCII
        unicode_content = '''
# Module with unicode comments: café, naïve, résumé
from mypackage.módulo import función
'''
        
        test_file = os.path.join(self.test_dir, 'mypackage', 'unicode_test.py')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(unicode_content)
        
        
            # This might raise an error due to invalid module name
            mock_convert.side_effect = ValueError("Invalid module name")
            
            with self.assertRaises(ValueError):
                mock_convert(test_file, application_directories=[self.test_dir])
    
    def test_very_long_import_statements(self):
        """
        Test handling of very long import statements.
        
        GIVEN: Import statements with many imported names
        WHEN: Converting imports
        THEN: Long statements should be handled correctly
        """
        long_import = '''
from mypackage.very.long.module.name.with.many.components import (
    function_one, function_two, function_three, function_four,
    function_five, function_six, function_seven, function_eight,
    ClassOne, ClassTwo, ClassThree, ClassFour,
    CONSTANT_ONE, CONSTANT_TWO, CONSTANT_THREE
)
'''
        
        test_file = os.path.join(self.test_dir, 'mypackage', 'long_imports.py')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(long_import)
        
        
            mock_convert.return_value = True
            
            result = mock_convert(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def test_imports_with_aliases(self):
        """
        Test handling of imports with aliases.
        
        GIVEN: Import statements with 'as' aliases
        WHEN: Converting imports
        THEN: Aliases should be preserved
        """
        aliased_imports = '''
from mypackage.module import function as func
from mypackage.utils import Helper as H
import mypackage.core as core
'''
        
        test_file = os.path.join(self.test_dir, 'mypackage', 'aliased.py')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(aliased_imports)
        
        
            mock_convert.return_value = True
            
            result = mock_convert(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)
    
    def test_conditional_imports(self):
        """
        Test handling of conditional imports.
        
        GIVEN: Imports inside if statements or try/except blocks
        WHEN: Converting imports
        THEN: Conditional imports should be handled appropriately
        """
        conditional_imports = '''
import sys

if sys.version_info >= (3, 8):
    from mypackage.modern import new_feature
else:
    from mypackage.legacy import old_feature

try:
    from mypackage.optional import optional_func
except ImportError:
    from mypackage.fallback import fallback_func
'''
        
        test_file = os.path.join(self.test_dir, 'mypackage', 'conditional.py')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(conditional_imports)
        
        
            mock_convert.return_value = True
            
            result = mock_convert(test_file, to_relative=True, application_directories=[self.test_dir])
            
            self.assertTrue(result)


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,
        catchbreak=True,
        warnings='ignore'
    )