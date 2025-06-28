"""Unit tests for the test change detector main function.

This module tests all success criteria defined in the PRD:
1. Change Detection Accuracy (with emphasis on minimizing false negatives)
2. Test Mapping Accuracy (with emphasis on minimizing false negatives)
3. Report Completeness
4. Code Coverage for Python constructs
5. JSON Validity (syntax and schema)

The program maintains state between runs to track changes over time.
"""

import unittest
import json
import tempfile
import os
import sys
import shutil
import time
from unittest.mock import patch, MagicMock
from io import StringIO
from pathlib import Path


class TestChangeDetectorMain(unittest.TestCase):
    """Test suite for the change detector main function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.target_dir = os.path.join(self.temp_dir, "codebase")
        self.state_dir = os.path.join(self.temp_dir, ".test_change_detector")
        
        os.makedirs(self.target_dir)
        os.makedirs(os.path.join(self.target_dir, "src"))
        os.makedirs(os.path.join(self.target_dir, "tests"))
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def _create_file(self, relative_path, content):
        """Helper to create a file with given content in the target directory."""
        filepath = os.path.join(self.target_dir, relative_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def _modify_file(self, relative_path, new_content):
        """Helper to modify an existing file."""
        filepath = os.path.join(self.target_dir, relative_path)
        # Small delay to ensure filesystem timestamp changes
        time.sleep(0.01)
        with open(filepath, 'w') as f:
            f.write(new_content)
        return filepath
    
    def _run_main(self, args):
        """Helper to run main with given arguments and capture output."""
        with patch('sys.argv', ['test_change_detector'] + args):
            with patch('sys.stdout', new=StringIO()) as fake_stdout:
                from tools.cli.flag_python_tests_that_need_updating.main import main
                try:
                    main()
                    output = fake_stdout.getvalue()
                    return json.loads(output)
                except SystemExit as e:
                    if e.code != 0:
                        raise
                    output = fake_stdout.getvalue()
                    return json.loads(output)
    
    # Test 1: Change Detection Accuracy Tests
    
    def test_detects_function_signature_change_between_runs(self):
        """Test detection of function signature changes between runs (minimize false negatives)."""
        # Initial state
        self._create_file("src/module.py", """
def add(x, y):
    '''Add two numbers.'''
    return x + y
""")
        
        self._create_file("tests/test_module.py", """
import unittest
from src.module import add

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
""")
        
        # First run - establish baseline
        result1 = self._run_main(['--path', self.target_dir])
        
        # Should report no changes on first run
        self.assertEqual(len(result1['changes']), 0)
        self.assertIn('metadata', result1)
        self.assertIn('first_run', result1['metadata'])
        self.assertTrue(result1['metadata']['first_run'])
        
        # Modify the function signature
        self._modify_file("src/module.py", """
def add(a, b):
    '''Add two numbers.'''
    return a + b
""")
        
        # Second run - should detect changes
        result2 = self._run_main(['--path', self.target_dir])
        
        # Should detect the change
        self.assertIn('changes', result2)
        self.assertEqual(len(result2['changes']), 1)
        self.assertEqual(result2['changes'][0]['element_name'], 'add')
        self.assertEqual(result2['changes'][0]['change_type'], 'signature_change')
        self.assertFalse(result2['metadata']['first_run'])
    
    def test_detects_function_implementation_change(self):
        """Test detection of function implementation changes."""
        # Initial state
        self._create_file("src/math_ops.py", """
def multiply(x, y):
    '''Multiply two numbers.'''
    return x * y
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Change implementation
        self._modify_file("src/math_ops.py", """
def multiply(x, y):
    '''Multiply two numbers.'''
    result = 0
    for _ in range(y):
        result += x
    return result
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect the change
        changes = [c for c in result['changes'] if c['element_name'] == 'multiply']
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['change_type'], 'implementation_change')
    
    def test_no_false_negatives_for_subtle_changes(self):
        """Test that subtle changes are not missed (minimize false negatives)."""
        # Initial state
        self._create_file("src/processing.py", """
def process(data):
    '''Process data.'''
    return data.strip().lower()
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Subtle change in processing order
        self._modify_file("src/processing.py", """
def process(data):
    '''Process data.'''
    return data.lower().strip()
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Must detect this subtle change
        changes = [c for c in result['changes'] if c['element_name'] == 'process']
        self.assertEqual(len(changes), 1)
    
    def test_state_persistence_across_runs(self):
        """Test that state is properly maintained across multiple runs."""
        # Initial state
        self._create_file("src/evolving.py", """
def version():
    return "1.0"
""")
        
        # Run 1
        self._run_main(['--path', self.target_dir])
        
        # Change 1
        self._modify_file("src/evolving.py", """
def version():
    return "1.1"
""")
        
        # Run 2
        result2 = self._run_main(['--path', self.target_dir])
        self.assertEqual(len([c for c in result2['changes'] if c['element_name'] == 'version']), 1)
        
        # Change 2
        self._modify_file("src/evolving.py", """
def version():
    return "1.2"
""")
        
        # Run 3 - should only show changes since last run, not cumulative
        result3 = self._run_main(['--path', self.target_dir])
        version_changes = [c for c in result3['changes'] if c['element_name'] == 'version']
        self.assertEqual(len(version_changes), 1)
        self.assertEqual(version_changes[0]['change_type'], 'implementation_change')
    
    # Test 2: Test Mapping Accuracy Tests
    
    def test_maps_direct_function_imports(self):
        """Test mapping of tests that directly import functions."""
        # Initial setup
        self._create_file("src/math_ops.py", """
def divide(x, y):
    '''Divide x by y.'''
    return x / y
""")
        
        self._create_file("tests/test_math_ops.py", """
import unittest
from src.math_ops import divide

class TestDivide(unittest.TestCase):
    def test_divide_normal(self):
        self.assertEqual(divide(10, 2), 5)
    
    def test_divide_by_zero(self):
        # This will raise an exception
        divide(10, 0)
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify function
        self._modify_file("src/math_ops.py", """
def divide(x, y):
    '''Divide x by y.'''
    if y == 0:
        raise ValueError("Division by zero")
    return x / y
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should map both test methods
        changes = [c for c in result['changes'] if c['element_name'] == 'divide']
        self.assertEqual(len(changes), 1)
        affected_tests = changes[0]['affected_tests']
        self.assertIn('tests.test_math_ops.TestDivide.test_divide_normal', affected_tests)
        self.assertIn('tests.test_math_ops.TestDivide.test_divide_by_zero', affected_tests)
    
    def test_maps_indirect_usage_minimize_false_negatives(self):
        """Test mapping of tests that use functions indirectly (minimize false negatives)."""
        # Initial setup
        self._create_file("src/helpers.py", """
def validate_input(value):
    '''Validate input value.'''
    return True

def process_value(value):
    '''Process a value after validation.'''
    validate_input(value)
    return value * 2
""")
        
        self._create_file("tests/test_helpers.py", """
import unittest
from src.helpers import process_value

class TestProcessValue(unittest.TestCase):
    def test_process_valid(self):
        self.assertEqual(process_value(5), 10)
    
    def test_process_string(self):
        # This might work or fail depending on validation
        result = process_value("string")
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify validation function
        self._modify_file("src/helpers.py", """
def validate_input(value):
    '''Validate input value.'''
    if not isinstance(value, (int, float)):
        raise TypeError("Must be numeric")
    return True

def process_value(value):
    '''Process a value after validation.'''
    validate_input(value)
    return value * 2
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect that tests for process_value are affected by validate_input change
        changes = [c for c in result['changes'] if c['element_name'] == 'validate_input']
        self.assertEqual(len(changes), 1)
        affected_tests = changes[0]['affected_tests']
        # Tests that use process_value should be flagged since it depends on validate_input
        self.assertIn('tests.test_helpers.TestProcessValue.test_process_string', affected_tests)
    
    # Test 3: Report Completeness Tests
    
    def test_report_contains_all_required_fields(self):
        """Test that report contains all required fields for each change."""
        # Create initial state
        self._create_file("src/module.py", "def func(): return 1")
        self._create_file("tests/test_module.py", """
import unittest
from src.module import func

class TestFunc(unittest.TestCase):
    def test_func(self):
        self.assertEqual(func(), 1)
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Make change
        self._modify_file("src/module.py", "def func(): return 2")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Check metadata
        self.assertIn('metadata', result)
        self.assertIn('first_run', result['metadata'])
        self.assertIn('run_timestamp', result['metadata'])
        self.assertIn('target_path', result['metadata'])
        
        # Check each change has required fields
        self.assertIn('changes', result)
        for change in result['changes']:
            self.assertIn('element_type', change)
            self.assertIn('element_name', change)
            self.assertIn('file_path', change)
            self.assertIn('change_type', change)
            self.assertIn('affected_tests', change)
            
            # Validate field types
            self.assertIsInstance(change['element_type'], str)
            self.assertIsInstance(change['element_name'], str)
            self.assertIsInstance(change['file_path'], str)
            self.assertIsInstance(change['change_type'], str)
            self.assertIsInstance(change['affected_tests'], list)
    
    # Test 4: Code Coverage Tests
    
    def test_handles_regular_functions(self):
        """Test handling of regular function definitions (weight=1.0)."""
        self._create_file("src/funcs.py", "def regular(): pass")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify
        self._modify_file("src/funcs.py", "def regular(): return 1")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        changes = [c for c in result['changes'] if c['element_name'] == 'regular']
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['element_type'], 'function')
    
    def test_handles_async_functions(self):
        """Test handling of async function definitions (weight=0.8)."""
        self._create_file("src/async_mod.py", "async def fetch(): pass")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify
        self._modify_file("src/async_mod.py", "async def fetch(): return 'data'")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        changes = [c for c in result['changes'] if c['element_name'] == 'fetch']
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['element_type'], 'async_function')
    
    def test_handles_class_methods(self):
        """Test handling of class methods (instance, class, static)."""
        self._create_file("src/classes.py", """
class MyClass:
    def instance_method(self):
        return 1
    
    @classmethod
    def class_method(cls):
        return 2
    
    @staticmethod
    def static_method():
        return 3
    
    @property
    def prop(self):
        return 4
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify all methods
        self._modify_file("src/classes.py", """
class MyClass:
    def instance_method(self):
        return 10
    
    @classmethod
    def class_method(cls):
        return 20
    
    @staticmethod
    def static_method():
        return 30
    
    @property
    def prop(self):
        return 40
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Check all method types are detected
        method_names = {c['element_name'] for c in result['changes']}
        self.assertIn('instance_method', method_names)
        self.assertIn('class_method', method_names)
        self.assertIn('static_method', method_names)
        self.assertIn('prop', method_names)
    
    def test_handles_class_definitions(self):
        """Test handling of class definition changes (weight=1.0)."""
        self._create_file("src/classes.py", """
class OldClass:
    def __init__(self):
        self.value = 1
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify class
        self._modify_file("src/classes.py", """
class OldClass:
    def __init__(self, value=1):
        self.value = value
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect __init__ change
        changes = [c for c in result['changes'] if c['element_name'] == '__init__']
        self.assertEqual(len(changes), 1)
    
    def test_handles_module_variables_and_constants(self):
        """Test handling of module-level variables and constants."""
        self._create_file("src/config.py", """
# Module constant
API_KEY = "old_key"
DEFAULT_TIMEOUT = 30

# Module variable
counter = 0
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify constants
        self._modify_file("src/config.py", """
# Module constant
API_KEY = "new_key"
DEFAULT_TIMEOUT = 60

# Module variable
counter = 0
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect constant changes
        constant_changes = [c for c in result['changes'] 
                          if c['element_name'] in ['API_KEY', 'DEFAULT_TIMEOUT']]
        self.assertEqual(len(constant_changes), 2)
        for change in constant_changes:
            self.assertEqual(change['element_type'], 'module_constant')
    
    # Test 5: JSON Validity Tests
    
    def test_json_syntax_validity(self):
        """Test that output is syntactically valid JSON."""
        self._create_file("src/test.py", "def f(): return 1")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Make change
        self._modify_file("src/test.py", "def f(): return 2")
        
        # Second run - capture raw output
        with patch('sys.argv', ['test_change_detector', '--path', self.target_dir]):
            with patch('sys.stdout', new=StringIO()) as fake_stdout:
                from tools.cli.flag_python_tests_that_need_updating.main import main
                try:
                    main()
                except SystemExit:
                    pass
                output = fake_stdout.getvalue()
        
        # Should be valid JSON
        try:
            json.loads(output)
        except json.JSONDecodeError as e:
            self.fail(f"Output is not valid JSON: {e}")
    
    def test_json_schema_conformance(self):
        """Test that output conforms to the defined schema."""
        self._create_file("src/test.py", '''def f(): return "test"''')
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Make change
        self._modify_file("src/test.py", '''def f(): return "test2"''')
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Validate schema structure
        self.assertIsInstance(result, dict)
        self.assertIn('changes', result)
        self.assertIn('metadata', result)
        self.assertIsInstance(result['changes'], list)
        self.assertIsInstance(result['metadata'], dict)
        
        # Validate metadata
        self.assertIn('first_run', result['metadata'])
        self.assertIn('run_timestamp', result['metadata'])
        self.assertIn('target_path', result['metadata'])
        
        # Validate each change object
        for change in result['changes']:
            self.assertIsInstance(change, dict)
            # Required fields
            self.assertIn('element_type', change)
            self.assertIn('element_name', change)
            self.assertIn('file_path', change)
            self.assertIn('change_type', change)
            self.assertIn('affected_tests', change)
            
            # Correct types
            self.assertIsInstance(change['element_type'], str)
            self.assertIsInstance(change['element_name'], str)
            self.assertIsInstance(change['file_path'], str)
            self.assertIsInstance(change['change_type'], str)
            self.assertIsInstance(change['affected_tests'], list)
            
            # All affected tests should be strings
            for test in change['affected_tests']:
                self.assertIsInstance(test, str)
    
    def test_json_string_escaping(self):
        """Test that strings in JSON are properly escaped."""
        # Create file with special characters
        self._create_file("src/special.py", '''
def func():
    """Function with "quotes" and \\ backslashes."""
    return 'line1\\nline2'
''')
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify
        self._modify_file("src/special.py", '''
def func():
    """Function with "quotes" and \\ backslashes."""
    return 'line1\\nline2\\ttab'
''')
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # If we got here, JSON was parsed successfully
        changes = [c for c in result['changes'] if c['element_name'] == 'func']
        self.assertEqual(len(changes), 1)
    
    def test_json_unicode_handling(self):
        """Test that Unicode in JSON is handled correctly."""
        # Create file with Unicode
        self._create_file("src/unicode.py", '''
def greet():
    """Say hello in multiple languages."""
    return "Hello"
''')
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Modify with Unicode
        self._modify_file("src/unicode.py", '''
def greet():
    """Say hello in multiple languages: 你好, مرحبا, Здравствуйте."""
    return "Hello, 你好, مرحبا, Здравствуйте"
''')
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should handle Unicode without issues
        changes = [c for c in result['changes'] if c['element_name'] == 'greet']
        self.assertEqual(len(changes), 1)
    
    # Integration Tests
    
    def test_no_changes_between_identical_runs(self):
        """Test that no changes are reported when nothing changes."""
        self._create_file("src/stable.py", """
def stable_function():
    return 42
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Second run without changes
        result = self._run_main(['--path', self.target_dir])
        
        self.assertEqual(len(result['changes']), 0)
        self.assertFalse(result['metadata']['first_run'])
    
    def test_file_added(self):
        """Test detection of newly added files."""
        # First run with initial state
        self._run_main(['--path', self.target_dir])
        
        # Add new file
        self._create_file("src/new_module.py", """
def new_function():
    '''A new function.'''
    return 42
""")
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect new function
        changes = [c for c in result['changes'] if c['element_name'] == 'new_function']
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['change_type'], 'added')
    
    def test_file_removed(self):
        """Test detection of removed files."""
        # Create file with function
        self._create_file("src/removed_module.py", """
def removed_function():
    '''A function that will be removed.'''
    return 0
""")
        
        # Test that uses the function
        self._create_file("tests/test_removed.py", """
import unittest
from src.removed_module import removed_function

class TestRemoved(unittest.TestCase):
    def test_removed_function(self):
        self.assertEqual(removed_function(), 0)
""")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Remove the file
        os.remove(os.path.join(self.target_dir, "src/removed_module.py"))
        
        # Second run
        result = self._run_main(['--path', self.target_dir])
        
        # Should detect removed function
        changes = [c for c in result['changes'] if c['element_name'] == 'removed_function']
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]['change_type'], 'removed')
        # Test should be flagged as affected
        self.assertIn('tests.test_removed.TestRemoved.test_removed_function', 
                     changes[0]['affected_tests'])
    
    def test_state_file_corruption_recovery(self):
        """Test that the program can recover from corrupted state files."""
        # First run
        self._create_file("src/test.py", "def func(): return 1")
        result1 = self._run_main(['--path', self.target_dir])
        self.assertTrue(result1['metadata']['first_run'])
        
        # Corrupt the state file (assuming it's in .test_change_detector)
        state_dir = os.path.join(self.target_dir, '.test_change_detector')
        if os.path.exists(state_dir):
            for filename in os.listdir(state_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(state_dir, filename)
                    with open(filepath, 'w') as f:
                        f.write("corrupted data not json")
        
        # Make a change
        self._modify_file("src/test.py", "def func(): return 2")
        
        # Second run - should handle corruption gracefully
        result2 = self._run_main(['--path', self.target_dir])
        
        # Should either recover or treat as first run
        self.assertIn('metadata', result2)
        self.assertIn('changes', result2)
    
    def test_reset_state_option(self):
        """Test the ability to reset state and start fresh."""
        # Create initial state
        self._create_file("src/module.py", "def f(): return 1")
        
        # First run
        self._run_main(['--path', self.target_dir])
        
        # Make changes
        self._modify_file("src/module.py", "def f(): return 2")
        
        # Run with reset flag
        result = self._run_main(['--path', self.target_dir, '--reset-state'])
        
        # Should treat as first run
        self.assertTrue(result['metadata']['first_run'])
        self.assertEqual(len(result['changes']), 0)


if __name__ == '__main__':
    unittest.main()