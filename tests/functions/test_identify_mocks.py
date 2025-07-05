import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from tools.functions.identify_mocks import identify_mocks


class TestIdentifyMocksBasicFunctionality(unittest.TestCase):
    """Test basic functionality of identify_mocks."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_file_with_obvious_mock_function(self):
        """
        GIVEN a Python file containing a function with name 'mock_database_connection'
        AND the function body contains 'raise NotImplementedError'
        WHEN identify_mocks is called with default parameters
        THEN expect:
            - Function returns a dictionary
            - 'mock_implementations' list contains at least one entry
            - Entry has 'name' == 'mock_database_connection'
            - Entry has 'confidence' >= 0.7 (default threshold)
            - 'total_functions' >= 1
            - 'mock_percentage' > 0
        """
        test_code = '''def mock_database_connection():
    """Mock database connection for testing."""
    raise NotImplementedError("This is a mock implementation")
'''
        test_file = os.path.join(self.temp_dir, 'test_mock.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertIsInstance(result, dict)
        self.assertIn('mock_implementations', result)
        self.assertGreater(len(result['mock_implementations']), 0)
        
        mock_found = any(impl['name'] == 'mock_database_connection' 
                        for impl in result['mock_implementations'])
        self.assertTrue(mock_found)
        
        mock_impl = next(impl for impl in result['mock_implementations'] 
                        if impl['name'] == 'mock_database_connection')
        self.assertGreaterEqual(mock_impl['confidence'], 0.7)
        self.assertGreaterEqual(result['total_functions'], 1)
        self.assertGreater(result['mock_percentage'], 0)

    def test_analyze_file_with_no_mock_implementations(self):
        """
        GIVEN a Python file containing only production code
        AND no mock indicators in function names, docstrings, or comments
        WHEN identify_mocks is called
        THEN expect:
            - 'mock_implementations' list is empty
            - 'total_functions' equals the actual function count
            - 'mock_percentage' == 0.0
            - 'patterns_found' is empty list
        """
        test_code = '''def calculate_interest(principal, rate, time):
    """Calculate compound interest."""
    return principal * (1 + rate) ** time

def validate_email(email):
    """Validate email format."""
    return "@" in email and "." in email
'''
        test_file = os.path.join(self.temp_dir, 'test_production.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertEqual(len(result['mock_implementations']), 0)
        self.assertEqual(result['total_functions'], 2)
        self.assertEqual(result['mock_percentage'], 0.0)
        self.assertEqual(len(result['patterns_found']), 0)

    def test_analyze_file_with_stub_pattern_in_docstring(self):
        """
        GIVEN a Python file with a function containing 'stub' in its docstring
        AND include_docstrings parameter is True (default)
        WHEN identify_mocks is called
        THEN expect:
            - Function is identified as mock implementation
            - 'patterns_found' includes 'stub'
            - Reason for classification mentions docstring analysis
        """
        test_code = '''def process_data(data):
    """This is a stub implementation for processing data."""
    return data
'''
        test_file = os.path.join(self.temp_dir, 'test_stub.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertIn('stub', result['patterns_found'])
        
        mock_impl = result['mock_implementations'][0]
        self.assertTrue(any('docstring' in reason.lower() for reason in mock_impl['reasons']))

    def test_analyze_file_with_placeholder_comment(self):
        """
        GIVEN a Python file with a function containing '# TODO: placeholder' comment
        AND include_comments parameter is True (default)
        WHEN identify_mocks is called
        THEN expect:
            - Function is identified as mock implementation
            - 'patterns_found' includes 'placeholder'
            - Reason for classification mentions comment analysis
        """
        test_code = '''def send_notification(message):
    # TODO: placeholder implementation
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_placeholder.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertIn('placeholder', result['patterns_found'])
        
        mock_impl = result['mock_implementations'][0]
        self.assertTrue(any('comment' in reason.lower() for reason in mock_impl['reasons']))

    def test_analyze_class_with_fake_prefix(self):
        """
        GIVEN a Python file containing a class named 'FakeUserRepository'
        WHEN identify_mocks is called
        THEN expect:
            - Class is identified in 'mock_implementations'
            - 'total_classes' >= 1
            - Entry type indicates it's a class, not a function
            - Confidence score is high due to 'Fake' prefix
        """
        test_code = '''class FakeUserRepository:
    """Fake implementation for testing."""
    
    def get_user(self, user_id):
        return {"id": user_id, "name": "Test User"}
'''
        test_file = os.path.join(self.temp_dir, 'test_fake_class.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertGreaterEqual(result['total_classes'], 1)
        
        class_impl = next((impl for impl in result['mock_implementations'] 
                          if impl['name'] == 'FakeUserRepository'), None)
        self.assertIsNotNone(class_impl)
        self.assertEqual(class_impl['type'], 'class')
        self.assertGreater(class_impl['confidence'], 0.8)

    def test_analyze_demonstration_method(self):
        """
        GIVEN a Python file with a class method named 'demonstration_workflow'
        WHEN identify_mocks is called
        THEN expect:
            - Method is identified as mock implementation
            - Entry indicates it's a method (includes class context)
            - 'patterns_found' includes 'demonstration'
        """
        test_code = '''class WorkflowManager:
    def demonstration_workflow(self):
        """Show how the workflow works."""
        print("This is a demo")
'''
        test_file = os.path.join(self.temp_dir, 'test_demo_method.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertIn('demonstration', result['patterns_found'])
        
        method_impl = next((impl for impl in result['mock_implementations'] 
                           if impl['name'] == 'demonstration_workflow'), None)
        self.assertIsNotNone(method_impl)
        self.assertEqual(method_impl['type'], 'method')


class TestIdentifyMocksParameterHandling(unittest.TestCase):
    """Test parameter handling and customization options."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_custom_patterns_parameter(self):
        """
        GIVEN a Python file with a function named 'sample_data_generator'
        AND custom_patterns=['sample', 'generator'] is provided
        WHEN identify_mocks is called with these patterns
        THEN expect:
            - Function is identified as mock implementation
            - 'patterns_found' includes both 'sample' and 'generator'
            - Default patterns still work (e.g., 'mock', 'fake')
        """
        test_code = '''def sample_data_generator():
    """Generate sample data."""
    return [1, 2, 3]

def mock_api_call():
    """Mock API call."""
    return {}
'''
        test_file = os.path.join(self.temp_dir, 'test_custom_patterns.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file, patterns=['sample', 'generator'])
        
        # Should find both functions
        self.assertGreaterEqual(len(result['mock_implementations']), 2)
        self.assertIn('sample', result['patterns_found'])
        self.assertIn('generator', result['patterns_found'])
        self.assertIn('mock', result['patterns_found'])

    def test_exclude_comments_analysis(self):
        """
        GIVEN a Python file with mock indicators only in comments
        AND include_comments=False parameter is set
        WHEN identify_mocks is called
        THEN expect:
            - Comments are not analyzed
            - Functions with mock indicators only in comments are not detected
            - 'mock_implementations' is empty
        """
        test_code = '''def process_data(data):
    # This is a mock implementation
    # TODO: fake data processing
    return data
'''
        test_file = os.path.join(self.temp_dir, 'test_no_comments.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file, include_comments=False)
        
        self.assertEqual(len(result['mock_implementations']), 0)

    def test_exclude_docstrings_analysis(self):
        """
        GIVEN a Python file with mock indicators only in docstrings
        AND include_docstrings=False parameter is set
        WHEN identify_mocks is called
        THEN expect:
            - Docstrings are not analyzed
            - Functions with mock indicators only in docstrings are not detected
            - 'mock_implementations' is empty
        """
        test_code = '''def process_data(data):
    """This is a stub implementation for demo purposes."""
    return data
'''
        test_file = os.path.join(self.temp_dir, 'test_no_docstrings.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file, include_docstrings=False)
        
        self.assertEqual(len(result['mock_implementations']), 0)

    def test_confidence_threshold_high(self):
        """
        GIVEN a Python file with functions having weak mock indicators
        AND confidence_threshold=0.9 (high threshold)
        WHEN identify_mocks is called
        THEN expect:
            - Only very obvious mocks are detected
            - Functions with confidence < 0.9 are excluded
            - 'mock_implementations' contains fewer entries than with default threshold
        """
        test_code = '''def maybe_mock_function():
    """Might be a demo."""
    pass

def definitely_mock_function():
    """This is clearly a fake stub placeholder implementation."""
    raise NotImplementedError("Mock implementation")
'''
        test_file = os.path.join(self.temp_dir, 'test_high_threshold.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result_default = identify_mocks(test_file, confidence_threshold=0.7)
        result_high = identify_mocks(test_file, confidence_threshold=0.9)
        
        self.assertLessEqual(len(result_high['mock_implementations']), 
                           len(result_default['mock_implementations']))

    def test_confidence_threshold_low(self):
        """
        GIVEN a Python file with functions having weak mock indicators
        AND confidence_threshold=0.3 (low threshold)
        WHEN identify_mocks is called
        THEN expect:
            - More functions are identified as potential mocks
            - Functions with confidence >= 0.3 are included
            - 'mock_implementations' contains more entries than with default threshold
        """
        test_code = '''def maybe_demo_function():
    """Might be a demo."""
    pass

def process_data(data):
    """Normal function."""
    return data
'''
        test_file = os.path.join(self.temp_dir, 'test_low_threshold.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result_default = identify_mocks(test_file, confidence_threshold=0.7)
        result_low = identify_mocks(test_file, confidence_threshold=0.3)
        
        self.assertGreaterEqual(len(result_low['mock_implementations']), 
                              len(result_default['mock_implementations']))

    def test_empty_patterns_list(self):
        """
        GIVEN patterns=[] (empty list) parameter
        WHEN identify_mocks is called
        THEN expect:
            - Default patterns are still used
            - Basic mock detection still works
            - 'patterns_found' contains default patterns if matches found
        """
        test_code = '''def mock_function():
    """Mock implementation."""
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_empty_patterns.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file, patterns=[])
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertIn('mock', result['patterns_found'])

    def test_none_patterns_uses_defaults(self):
        """
        GIVEN patterns=None (default)
        WHEN identify_mocks is called
        THEN expect:
            - Default patterns are used ('mock', 'fake', 'placeholder', etc.)
            - Standard mock detection works normally
            - 'patterns_found' contains matched default patterns
        """
        test_code = '''def fake_service():
    """Placeholder implementation."""
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_none_patterns.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file, patterns=None)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        self.assertIn('fake', result['patterns_found'])
        self.assertIn('placeholder', result['patterns_found'])


class TestIdentifyMocksErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_file_not_found(self):
        """
        GIVEN a file path that does not exist
        WHEN identify_mocks is called
        THEN expect FileNotFoundError to be raised
        """
        non_existent_file = '/path/that/does/not/exist.py'
        
        with self.assertRaises(FileNotFoundError):
            identify_mocks(non_existent_file)

    def test_non_python_file(self):
        """
        GIVEN a file path with non-.py extension (e.g., 'file.txt')
        WHEN identify_mocks is called
        THEN expect ValueError to be raised with message about .py extension
        """
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write("Some text content")
            
        with self.assertRaises(ValueError) as context:
            identify_mocks(test_file)
        self.assertIn('.py', str(context.exception))

    def test_permission_denied(self):
        """
        GIVEN a Python file that exists but cannot be read due to permissions
        WHEN identify_mocks is called
        THEN expect PermissionError to be raised
        """
        test_file = os.path.join(self.temp_dir, 'no_read.py')
        with open(test_file, 'w') as f:
            f.write("def test(): pass")
        os.chmod(test_file, 0o000)
        
        try:
            with self.assertRaises(PermissionError):
                identify_mocks(test_file)
        finally:
            os.chmod(test_file, 0o644)  # Restore permissions for cleanup

    def test_syntax_error_in_python_file(self):
        """
        GIVEN a Python file containing syntax errors
        WHEN identify_mocks is called
        THEN expect SyntaxError to be raised with details about the error
        """
        test_code = '''def invalid_syntax(
    # Missing closing parenthesis and colon
    pass
'''
        test_file = os.path.join(self.temp_dir, 'syntax_error.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        with self.assertRaises(SyntaxError):
            identify_mocks(test_file)

    def test_confidence_threshold_out_of_range_high(self):
        """
        GIVEN confidence_threshold > 1.0 (e.g., 1.5)
        WHEN identify_mocks is called
        THEN expect ValueError to be raised about threshold range
        """
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write("def test(): pass")
            
        with self.assertRaises(ValueError) as context:
            identify_mocks(test_file, confidence_threshold=1.5)
        self.assertIn('threshold', str(context.exception).lower())

    def test_confidence_threshold_out_of_range_low(self):
        """
        GIVEN confidence_threshold < 0.0 (e.g., -0.1)
        WHEN identify_mocks is called
        THEN expect ValueError to be raised about threshold range
        """
        test_file = os.path.join(self.temp_dir, 'test.py')
        with open(test_file, 'w') as f:
            f.write("def test(): pass")
            
        with self.assertRaises(ValueError) as context:
            identify_mocks(test_file, confidence_threshold=-0.1)
        self.assertIn('threshold', str(context.exception).lower())

    def test_empty_python_file(self):
        """
        GIVEN an empty Python file (0 bytes)
        WHEN identify_mocks is called
        THEN expect:
            - Function returns successfully
            - 'total_functions' == 0
            - 'total_classes' == 0
            - 'mock_implementations' is empty list
            - 'mock_percentage' == 0.0
        """
        test_file = os.path.join(self.temp_dir, 'empty.py')
        with open(test_file, 'w') as f:
            pass  # Create empty file
            
        result = identify_mocks(test_file)
        
        self.assertEqual(result['total_functions'], 0)
        self.assertEqual(result['total_classes'], 0)
        self.assertEqual(len(result['mock_implementations']), 0)
        self.assertEqual(result['mock_percentage'], 0.0)

    def test_io_error_during_read(self):
        """
        GIVEN a file that encounters an I/O error during reading
        WHEN identify_mocks is called
        THEN expect IOError to be raised
        """
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Simulated I/O error")
            
            with self.assertRaises(IOError):
                identify_mocks('test.py')


class TestIdentifyMocksOutputStructure(unittest.TestCase):
    """Test the structure and content of returned data."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_return_value_structure(self):
        """
        GIVEN a valid Python file
        WHEN identify_mocks is called
        THEN expect return value to be a dictionary containing all required keys:
            - 'mock_implementations' (list)
            - 'total_functions' (int)
            - 'total_classes' (int)
            - 'mock_percentage' (float)
            - 'confidence_scores' (dict)
            - 'patterns_found' (list)
            - 'file_metrics' (dict)
        """
        test_code = '''def test_function():
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_structure.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        required_keys = [
            'mock_implementations', 'total_functions', 'total_classes',
            'mock_percentage', 'confidence_scores', 'patterns_found', 'file_metrics'
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
            
        self.assertIsInstance(result['mock_implementations'], list)
        self.assertIsInstance(result['total_functions'], int)
        self.assertIsInstance(result['total_classes'], int)
        self.assertIsInstance(result['mock_percentage'], float)
        self.assertIsInstance(result['confidence_scores'], dict)
        self.assertIsInstance(result['patterns_found'], list)
        self.assertIsInstance(result['file_metrics'], dict)

    def test_mock_implementation_entry_structure(self):
        """
        GIVEN a Python file with a mock function
        WHEN identify_mocks is called
        THEN expect each entry in 'mock_implementations' to contain:
            - 'name' (str): Function/class/method name
            - 'line_numbers' (tuple/list): Start and end line numbers
            - 'confidence' (float): Confidence score
            - 'reasons' (list): List of reasons for classification
            - 'type' (str): 'function', 'method', or 'class'
        """
        test_code = '''def mock_function():
    """Mock implementation."""
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_entry_structure.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        
        entry = result['mock_implementations'][0]
        required_fields = ['name', 'line_numbers', 'confidence', 'reasons', 'type']
        
        for field in required_fields:
            self.assertIn(field, entry)
            
        self.assertIsInstance(entry['name'], str)
        self.assertIsInstance(entry['line_numbers'], (list, tuple))
        self.assertIsInstance(entry['confidence'], float)
        self.assertIsInstance(entry['reasons'], list)
        self.assertIsInstance(entry['type'], str)
        self.assertIn(entry['type'], ['function', 'method', 'class'])

    def test_confidence_scores_mapping(self):
        """
        GIVEN a Python file with multiple functions
        WHEN identify_mocks is called
        THEN expect 'confidence_scores' to:
            - Be a dictionary
            - Have keys matching all analyzed function/class names
            - Have float values between 0.0 and 1.0
            - Include both mock and non-mock implementations
        """
        test_code = '''def mock_function():
    """Mock implementation."""
    pass

def real_function():
    """Real implementation."""
    return 42

class TestClass:
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_confidence_mapping.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertIsInstance(result['confidence_scores'], dict)
        self.assertIn('mock_function', result['confidence_scores'])
        self.assertIn('real_function', result['confidence_scores'])
        self.assertIn('TestClass', result['confidence_scores'])
        
        for score in result['confidence_scores'].values():
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_file_metrics_content(self):
        """
        GIVEN a Python file with code
        WHEN identify_mocks is called
        THEN expect 'file_metrics' to contain:
            - 'total_lines' (int): Total lines in file
            - 'code_lines' (int): Non-empty, non-comment lines
            - 'comment_lines' (int): Comment line count
            - 'docstring_lines' (int): Docstring line count
        """
        test_code = '''# This is a comment
"""This is a docstring."""

def test_function():
    """Function docstring."""
    # Another comment
    return 42
'''
        test_file = os.path.join(self.temp_dir, 'test_file_metrics.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        metrics = result['file_metrics']
        required_metrics = ['total_lines', 'code_lines', 'comment_lines', 'docstring_lines']
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], int)
            self.assertGreaterEqual(metrics[metric], 0)

    def test_mock_percentage_calculation(self):
        """
        GIVEN a Python file with 3 functions where 1 is a mock
        WHEN identify_mocks is called
        THEN expect:
            - 'mock_percentage' equals (1/3) * 100 = 33.33...
            - Value is a float between 0.0 and 100.0
            - Calculation includes both functions and classes in denominator
        """
        test_code = '''def mock_function():
    """Mock implementation."""
    pass

def real_function_1():
    return 1

def real_function_2():
    return 2
'''
        test_file = os.path.join(self.temp_dir, 'test_percentage.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        expected_percentage = (1.0 / 3.0) * 100
        self.assertAlmostEqual(result['mock_percentage'], expected_percentage, places=1)
        self.assertGreaterEqual(result['mock_percentage'], 0.0)
        self.assertLessEqual(result['mock_percentage'], 100.0)

    def test_patterns_found_deduplication(self):
        """
        GIVEN a Python file where 'mock' pattern appears multiple times
        WHEN identify_mocks is called
        THEN expect:
            - 'patterns_found' contains 'mock' only once
            - List contains unique patterns only
            - Order reflects first occurrence
        """
        test_code = '''def mock_function_1():
    """Mock implementation."""
    pass

def mock_function_2():
    """Another mock implementation."""
    pass
'''
        test_file = os.path.join(self.temp_dir, 'test_deduplication.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_count = result['patterns_found'].count('mock')
        self.assertEqual(mock_count, 1)
        self.assertEqual(len(result['patterns_found']), len(set(result['patterns_found'])))

    def test_line_numbers_accuracy(self):
        """
        GIVEN a Python file with a mock function spanning lines 10-15
        WHEN identify_mocks is called
        THEN expect:
            - Mock entry 'line_numbers' shows (10, 15) or [10, 15]
            - Line numbers are 1-indexed, not 0-indexed
            - End line includes the last line of the function
        """
        test_code = '''# Line 1
# Line 2
# Line 3
# Line 4
# Line 5
# Line 6
# Line 7
# Line 8
# Line 9
def mock_function():  # Line 10
    """Mock implementation."""  # Line 11
    # Comment  # Line 12
    pass  # Line 13
    # End  # Line 14
# Line 15 after function
'''
        test_file = os.path.join(self.temp_dir, 'test_line_numbers.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        mock_impl = result['mock_implementations'][0]
        line_numbers = mock_impl['line_numbers']
        
        self.assertIsInstance(line_numbers, (list, tuple))
        self.assertEqual(len(line_numbers), 2)
        self.assertEqual(line_numbers[0], 10)  # Start line (1-indexed)
        self.assertGreaterEqual(line_numbers[1], 13)  # End line should be at least line 13


class TestIdentifyMocksComplexScenarios(unittest.TestCase):
    """Test complex scenarios and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_nested_functions_with_mock_indicators(self):
        """
        GIVEN a Python file with nested functions where inner function has mock indicators
        WHEN identify_mocks is called
        THEN expect:
            - Both outer and inner functions are analyzed
            - Inner function is correctly identified if it has mock indicators
            - Line numbers correctly reflect nested structure
        """
        test_code = '''def outer_function():
    """Real outer function."""
    
    def mock_inner_function():
        """Mock inner implementation."""
        raise NotImplementedError("Mock")
        
    return mock_inner_function()
'''
        test_file = os.path.join(self.temp_dir, 'test_nested.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        # Should find the inner mock function
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('mock_inner_function', mock_names)
        
        # Should analyze both functions
        self.assertGreaterEqual(result['total_functions'], 2)

    def test_class_with_mix_of_mock_and_real_methods(self):
        """
        GIVEN a class with some mock methods and some real implementations
        WHEN identify_mocks is called
        THEN expect:
            - Individual methods are analyzed separately
            - Only mock methods appear in 'mock_implementations'
            - Class itself is not marked as mock unless name indicates it
            - 'total_functions' includes all methods
        """
        test_code = '''class UserService:
    """Real user service class."""
    
    def get_user(self, user_id):
        """Real implementation."""
        return {"id": user_id}
        
    def mock_authenticate(self, credentials):
        """Mock authentication for testing."""
        return True
        
    def fake_send_email(self, email):
        """Fake email sending."""
        pass
'''
        test_file = os.path.join(self.temp_dir, 'test_mixed_class.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('mock_authenticate', mock_names)
        self.assertIn('fake_send_email', mock_names)
        self.assertNotIn('get_user', mock_names)
        
        # Class itself should not be marked as mock
        self.assertNotIn('UserService', mock_names)
        
        # Should count all methods
        self.assertGreaterEqual(result['total_functions'], 3)

    def test_async_mock_functions(self):
        """
        GIVEN async functions with mock indicators (async def mock_api_call)
        WHEN identify_mocks is called
        THEN expect:
            - Async functions are detected same as regular functions
            - Entry indicates it's an async function in some way
            - Confidence scoring works the same
        """
        test_code = '''import asyncio

async def mock_api_call():
    """Mock async API call."""
    await asyncio.sleep(0.1)
    return {"status": "mock"}

async def real_api_call():
    """Real async API call."""
    return {"status": "real"}
'''
        test_file = os.path.join(self.temp_dir, 'test_async.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('mock_api_call', mock_names)
        self.assertNotIn('real_api_call', mock_names)

    def test_decorator_preserved_mock_detection(self):
        """
        GIVEN functions with decorators that have mock implementations
        WHEN identify_mocks is called
        THEN expect:
            - Decorated functions are still analyzed
            - Mock indicators in decorated functions are detected
            - Function name extraction works despite decorators
        """
        test_code = '''from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def mock_decorated_function():
    """Mock implementation with decorator."""
    raise NotImplementedError("Mock")

@decorator
def real_decorated_function():
    """Real implementation with decorator."""
    return 42
'''
        test_file = os.path.join(self.temp_dir, 'test_decorated.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('mock_decorated_function', mock_names)
        self.assertNotIn('real_decorated_function', mock_names)

    def test_property_mock_detection(self):
        """
        GIVEN class properties decorated with @property that are mocks
        WHEN identify_mocks is called
        THEN expect:
            - Properties are analyzed for mock indicators
            - Entry type indicates it's a property
            - Getter/setter/deleter are analyzed separately if present
        """
        test_code = '''class TestClass:
    @property
    def mock_property(self):
        """Mock property implementation."""
        raise NotImplementedError("Mock property")
        
    @property
    def real_property(self):
        """Real property implementation."""
        return self._value
'''
        test_file = os.path.join(self.temp_dir, 'test_properties.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('mock_property', mock_names)
        self.assertNotIn('real_property', mock_names)

    def test_multiple_mock_indicators_increase_confidence(self):
        """
        GIVEN a function with multiple mock indicators:
            - Name contains 'fake'
            - Docstring mentions 'placeholder'
            - Body has 'NotImplementedError'
            - Comment says 'TODO: implement'
        WHEN identify_mocks is called
        THEN expect:
            - Confidence score is very high (close to 1.0)
            - All reasons are listed in the entry
            - Multiple patterns appear in 'patterns_found'
        """
        test_code = '''def fake_data_processor():
    """This is a placeholder implementation for demo purposes."""
    # TODO: implement real processing logic
    raise NotImplementedError("Stub implementation")
'''
        test_file = os.path.join(self.temp_dir, 'test_multiple_indicators.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        self.assertGreater(len(result['mock_implementations']), 0)
        mock_impl = result['mock_implementations'][0]
        
        self.assertGreater(mock_impl['confidence'], 0.9)
        self.assertGreater(len(mock_impl['reasons']), 2)
        
        expected_patterns = ['fake', 'placeholder', 'implement', 'stub']
        found_patterns = result['patterns_found']
        for pattern in expected_patterns:
            self.assertIn(pattern, found_patterns)

    def test_inheritance_mock_detection(self):
        """
        GIVEN a class inheriting from 'MockBase' or similar
        WHEN identify_mocks is called
        THEN expect:
            - Inheritance is considered in mock detection
            - Class has higher confidence due to mock base class
            - Reason mentions inheritance pattern
        """
        test_code = '''class MockBase:
    """Base class for mocks."""
    pass

class TestMockService(MockBase):
    """Service implementation for testing."""
    
    def process(self):
        return "mock result"

class RealService:
    """Real service implementation."""
    
    def process(self):
        return "real result"
'''
        test_file = os.path.join(self.temp_dir, 'test_inheritance.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        result = identify_mocks(test_file)
        
        mock_names = [impl['name'] for impl in result['mock_implementations']]
        self.assertIn('TestMockService', mock_names)
        self.assertNotIn('RealService', mock_names)
        
        # Find the mock service entry
        mock_service = next(impl for impl in result['mock_implementations'] 
                           if impl['name'] == 'TestMockService')
        self.assertGreater(mock_service['confidence'], 0.7)

    def test_large_file_performance(self):
        """
        GIVEN a large Python file (1000+ lines, 100+ functions)
        WHEN identify_mocks is called
        THEN expect:
            - Function completes without timeout
            - All functions are analyzed
            - Results are accurate despite file size
            - File metrics reflect actual size
        """
        # Generate a large file with many functions
        lines = ['# Large test file']
        for i in range(100):
            if i % 10 == 0:  # Every 10th function is a mock
                lines.extend([
                    f'def mock_function_{i}():',
                    f'    """Mock implementation {i}."""',
                    '    raise NotImplementedError("Mock")',
                    ''
                ])
            else:
                lines.extend([
                    f'def real_function_{i}():',
                    f'    """Real implementation {i}."""',
                    f'    return {i}',
                    ''
                ])
        
        # Add some padding to reach 1000+ lines
        while len(lines) < 1000:
            lines.append('# Padding comment')
            
        test_code = '\n'.join(lines)
        test_file = os.path.join(self.temp_dir, 'test_large.py')
        with open(test_file, 'w') as f:
            f.write(test_code)
            
        import time
        start_time = time.time()
        result = identify_mocks(test_file)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 30 seconds)
        self.assertLess(end_time - start_time, 30)
        
        # Should find all 100 functions
        self.assertEqual(result['total_functions'], 100)
        
        # Should find approximately 10 mock functions
        self.assertGreaterEqual(len(result['mock_implementations']), 8)
        self.assertLessEqual(len(result['mock_implementations']), 12)
        
        # File metrics should reflect actual size
        self.assertGreaterEqual(result['file_metrics']['total_lines'], 1000)

    def test_mocks_from_real_examples(self):
        """
        GIVEN a series of real examples taken from a code base
        WHEN identify_mocks is called
        THEN expect:
            - Function flags all mock implementations.
            - Function does not flag non-mock implementations
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        real_examples_dir = os.path.join(this_dir, 'identify_mocks_fixtures')
        
        for file in os.listdir(real_examples_dir):
            if file.endswith('.py'):
                with self.subTest(file=file):
                    test_file = os.path.join(real_examples_dir, file)
                    result = identify_mocks(test_file)

                    # Check if any mock implementations were found
                    self.assertGreater(len(result['mock_implementations']), 0, 
                                       f"No mock implementations found in {file}")
                    
                    # Ensure confidence scores are reasonable
                    for impl in result['mock_implementations']:
                        self.assertGreater(impl['confidence'], 0.5, 
                                           f"Low confidence for {impl['name']} in {file}")




if __name__ == '__main__':
    unittest.main()