#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for class_diagram_to_python_files.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call, mock_open
from pathlib import Path
import sys
import tempfile
import os
import argparse
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype/class_diagram_to_python_files')
    from tools.cli.mermaid_to_prototype.class_diagram_to_python_files import ClassDiagramToPythonFiles
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestClassDiagramToPythonFilesInitialization(unittest.TestCase):
    """
    Test suite for ClassDiagramToPythonFiles initialization and dependency injection.
    
    Tests cover:
    - Proper dependency injection validation
    - Resource availability checks
    - Constructor error handling
    - Configuration parameter handling
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates mock objects for all required dependencies and configurations.
        """
        # Create mock dependencies
        self.mock_logger = MagicMock()
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()
        self.mock_configs = MagicMock()
        
        # Valid resources dictionary
        self.valid_resources = {
            'logger': self.mock_logger,
            'mermaid_parser': self.mock_mermaid_parser,
            'python_code_generator': self.mock_python_code_generator,
            'file_writer': self.mock_file_writer
        }

    def test_successful_initialization_with_all_resources(self):
        """
        Test successful initialization when all required resources are provided.
        
        Pseudocode:
        1. Create resources dictionary with all required dependencies
        2. Initialize ClassDiagramToPythonFiles with resources and configs
        3. Verify all dependencies are properly assigned
        4. Verify no exceptions are raised
        
        Expected behavior:
        - All resource properties should be assigned correctly
        - No ValueError should be raised
        - Instance should be ready for use
        """
        # Test initialization
        converter = ClassDiagramToPythonFiles(
            resources=self.valid_resources,
            configs=self.mock_configs
        )
        
        # Verify proper assignment
        self.assertEqual(converter._logger, self.mock_logger)
        self.assertEqual(converter._mermaid_parser, self.mock_mermaid_parser)
        self.assertEqual(converter._python_code_generator, self.mock_python_code_generator)
        self.assertEqual(converter._file_writer, self.mock_file_writer)
        self.assertEqual(converter.resources, self.valid_resources)
        self.assertEqual(converter.configs, self.mock_configs)

    def test_initialization_with_missing_logger(self):
        """
        Test initialization failure when logger dependency is missing.
        
        Pseudocode:
        1. Create resources dictionary without logger
        2. Attempt to initialize ClassDiagramToPythonFiles
        3. Verify ValueError is raised with appropriate message
        
        Expected behavior:
        - ValueError should be raised
        - Error message should mention missing logger resource
        """
        incomplete_resources = self.valid_resources.copy()
        del incomplete_resources['logger']
        
        with self.assertRaises(ValueError) as context:
            ClassDiagramToPythonFiles(
                resources=incomplete_resources,
                configs=self.mock_configs
            )
        
        self.assertIn("Missing required resource: logger", str(context.exception))

    def test_initialization_with_missing_mermaid_parser(self):
        """
        Test initialization failure when mermaid_parser dependency is missing.
        
        Pseudocode:
        1. Create resources dictionary without mermaid_parser
        2. Attempt to initialize ClassDiagramToPythonFiles
        3. Verify ValueError is raised with appropriate message
        
        Expected behavior:
        - ValueError should be raised
        - Error message should mention missing mermaid_parser resource
        """
        incomplete_resources = self.valid_resources.copy()
        del incomplete_resources['mermaid_parser']
        
        with self.assertRaises(ValueError) as context:
            ClassDiagramToPythonFiles(
                resources=incomplete_resources,
                configs=self.mock_configs
            )
        
        self.assertIn("Missing required resource: mermaid_parser", str(context.exception))

    def test_initialization_with_missing_python_code_generator(self):
        """
        Test initialization failure when python_code_generator dependency is missing.
        
        Pseudocode:
        1. Create resources dictionary without python_code_generator
        2. Attempt to initialize ClassDiagramToPythonFiles
        3. Verify ValueError is raised with appropriate message
        
        Expected behavior:
        - ValueError should be raised
        - Error message should mention missing python_code_generator resource
        """
        incomplete_resources = self.valid_resources.copy()
        del incomplete_resources['python_code_generator']
        
        with self.assertRaises(ValueError) as context:
            ClassDiagramToPythonFiles(
                resources=incomplete_resources,
                configs=self.mock_configs
            )
        
        self.assertIn("Missing required resource: python_code_generator", str(context.exception))

    def test_initialization_with_missing_file_writer(self):
        """
        Test initialization failure when file_writer dependency is missing.
        
        Pseudocode:
        1. Create resources dictionary without file_writer
        2. Attempt to initialize ClassDiagramToPythonFiles
        3. Verify ValueError is raised with appropriate message
        
        Expected behavior:
        - ValueError should be raised
        - Error message should mention missing file_writer resource
        """
        incomplete_resources = self.valid_resources.copy()
        del incomplete_resources['file_writer']
        
        with self.assertRaises(ValueError) as context:
            ClassDiagramToPythonFiles(
                resources=incomplete_resources,
                configs=self.mock_configs
            )
        
        self.assertIn("Missing required resource: file_writer", str(context.exception))

    def test_initialization_with_none_resources(self):
        """
        Test initialization failure when resources parameter is None.
        
        Pseudocode:
        1. Attempt to initialize with resources=None
        2. Verify appropriate exception is raised
        
        Expected behavior:
        - Should raise an exception (TypeError or KeyError)
        - Should fail gracefully without corrupting state
        """
        with self.assertRaises((TypeError, KeyError)):
            ClassDiagramToPythonFiles(
                resources=None,
                configs=self.mock_configs
            )


class TestClassDiagramToPythonFilesMakeMethod(unittest.TestCase):
    """
    Test suite for the make() factory method of ClassDiagramToPythonFiles.
    
    Tests cover:
    - Argument parsing and delegation to convert()
    - Return value handling (True/False based on success)
    - Error propagation from convert() method
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates a properly configured converter instance and mock arguments.
        """
        # Create mock dependencies
        self.mock_logger = MagicMock()
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()
        self.mock_configs = MagicMock()
        
        self.valid_resources = {
            'logger': self.mock_logger,
            'mermaid_parser': self.mock_mermaid_parser,
            'python_code_generator': self.mock_python_code_generator,
            'file_writer': self.mock_file_writer
        }
        
        self.converter = ClassDiagramToPythonFiles(
            resources=self.valid_resources,
            configs=self.mock_configs
        )
        
        # Create mock arguments
        self.mock_args = argparse.Namespace(
            input_file=Path("/test/input.md"),
            output_directory="/test/output",
            overwrite_existing=False,
            generate_init_files=True
        )

    def test_make_with_successful_conversion(self):
        """
        Test make() method when conversion succeeds.
        
        Pseudocode:
        1. Mock convert() method to return success result
        2. Call make() with valid arguments
        3. Verify convert() is called with correct parameters
        4. Verify True is returned
        
        Expected behavior:
        - convert() should be called with args from namespace
        - Should return True when conversion succeeds
        """
        # Mock successful conversion
        success_result = {
            'success': True,
            'generated_files': ['class1.py', 'class2.py'],
            'classes_generated': 2
        }
        
        with patch.object(self.converter, 'convert', return_value=success_result) as mock_convert:
            result = self.converter.make(self.mock_args)
            
            # Verify convert was called correctly
            mock_convert.assert_called_once_with(
                input_file_path=self.mock_args.input_file,
                output_directory=self.mock_args.output_directory,
                overwrite_existing=self.mock_args.overwrite_existing,
                generate_init_files=self.mock_args.generate_init_files
            )
            
            # Verify return value
            self.assertTrue(result)

    def test_make_with_failed_conversion(self):
        """
        Test make() method when conversion fails.
        
        Pseudocode:
        1. Mock convert() method to return failure result
        2. Call make() with valid arguments
        3. Verify False is returned
        
        Expected behavior:
        - Should return False when conversion fails
        - Error handling should be graceful
        """
        # Mock failed conversion
        failure_result = {
            'success': False,
            'errors': ['Parsing failed']
        }
        
        with patch.object(self.converter, 'convert', return_value=failure_result) as mock_convert:
            result = self.converter.make(self.mock_args)
            
            # Verify return value
            self.assertFalse(result)

    def test_make_with_convert_returning_none(self):
        """
        Test make() method when convert() returns None.
        
        Pseudocode:
        1. Mock convert() method to return None
        2. Call make() with valid arguments
        3. Verify False is returned
        
        Expected behavior:
        - Should return False when convert returns None
        - Should handle None gracefully
        """
        with patch.object(self.converter, 'convert', return_value=None) as mock_convert:
            result = self.converter.make(self.mock_args)
            
            # Verify return value
            self.assertFalse(result)


class TestClassDiagramToPythonFilesConvertMethod(unittest.TestCase):
    """
    Test suite for the convert() method of ClassDiagramToPythonFiles.
    
    Tests cover:
    - Complete conversion pipeline execution
    - Input validation
    - File reading and parsing
    - Code generation and file writing
    - Error handling and reporting
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates converter instance with mocked dependencies and temporary files.
        """
        # Create temporary test directory and files
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "test_diagram.md")
        self.output_dir = os.path.join(self.test_dir, "output")
        
        # Create test input file
        test_content = """
        ```mermaid
        classDiagram
            class Animal {
                +String name
                +int age
                +makeSound()
            }
        ```
        """
        with open(self.input_file, 'w') as f:
            f.write(test_content)
        
        # Create mock dependencies
        self.mock_logger = MagicMock()
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()
        self.mock_configs = MagicMock()
        
        self.valid_resources = {
            'logger': self.mock_logger,
            'mermaid_parser': self.mock_mermaid_parser,
            'python_code_generator': self.mock_python_code_generator,
            'file_writer': self.mock_file_writer
        }
        
        self.converter = ClassDiagramToPythonFiles(
            resources=self.valid_resources,
            configs=self.mock_configs
        )

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Removes temporary files and directories created during testing.
        """
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_convert_successful_complete_pipeline(self):
        """
        Test complete successful conversion pipeline.
        
        Pseudocode:
        1. Setup mocks for all pipeline steps to succeed
        2. Call convert() with valid parameters
        3. Verify each pipeline step is called in correct order
        4. Verify successful result is returned
        
        Expected behavior:
        - All pipeline steps should be executed in order
        - Result should indicate success
        - Generated files should be listed in result
        """
        # Setup mock responses
        parsed_data = {
            'classes': [
                {'name': 'Animal', 'attributes': ['name', 'age'], 'methods': ['makeSound']}
            ]
        }
        self.mock_mermaid_parser.parse_class_diagram.return_value = parsed_data
        
        generated_code = "class Animal:\n    def __init__(self):\n        pass"
        self.mock_python_code_generator.generate_class_code.return_value = generated_code
        self.mock_python_code_generator.generate_init_file.return_value = "# Init file"
        
        self.mock_file_writer.ensure_directory_exists.return_value = None
        self.mock_file_writer.write_python_file.return_value = None
        
        # Execute conversion
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=self.output_dir
        )
        
        # Verify pipeline execution
        self.mock_mermaid_parser.parse_class_diagram.assert_called_once()
        self.mock_python_code_generator.generate_class_code.assert_called_once()
        self.mock_python_code_generator.generate_init_file.assert_called_once()
        self.mock_file_writer.ensure_directory_exists.assert_called_once_with(self.output_dir)
        
        # Verify successful result
        self.assertTrue(result['success'])
        self.assertEqual(result['classes_generated'], 1)
        self.assertIn('animal.py', result['generated_files'])
        self.assertIn('__init__.py', result['generated_files'])
        self.assertEqual(len(result['errors']), 0)

    def test_convert_with_invalid_input_file_path(self):
        """
        Test convert() with non-existent input file.
        
        Pseudocode:
        1. Call convert() with path to non-existent file
        2. Verify appropriate error result is returned
        3. Verify no pipeline steps are executed
        
        Expected behavior:
        - Should return failure result
        - Error should mention file not found
        - No parsing or generation should occur
        """
        non_existent_file = "/path/to/nonexistent/file.md"
        
        result = self.converter.convert(
            input_file_path=non_existent_file,
            output_directory=self.output_dir
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("not found", result['errors'][0].lower())
        
        # Verify no pipeline execution
        self.mock_mermaid_parser.parse_class_diagram.assert_not_called()

    def test_convert_with_empty_input_file_path(self):
        """
        Test convert() with empty input file path.
        
        Pseudocode:
        1. Call convert() with empty string as input path
        2. Verify validation error occurs
        3. Verify appropriate error result is returned
        
        Expected behavior:
        - Should return failure result
        - Error should mention empty file path
        """
        result = self.converter.convert(
            input_file_path="",
            output_directory=self.output_dir
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("empty", result['errors'][0].lower())

    def test_convert_with_empty_output_directory(self):
        """
        Test convert() with empty output directory.
        
        Pseudocode:
        1. Call convert() with empty string as output directory
        2. Verify validation error occurs
        3. Verify appropriate error result is returned
        
        Expected behavior:
        - Should return failure result
        - Error should mention empty output directory
        """
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=""
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("empty", result['errors'][0].lower())

    def test_convert_with_parsing_failure(self):
        """
        Test convert() when Mermaid parsing fails.
        
        Pseudocode:
        1. Mock parser to raise exception
        2. Call convert() with valid parameters
        3. Verify error is caught and returned in result
        4. Verify no generation steps are executed
        
        Expected behavior:
        - Should return failure result
        - Error should be captured and reported
        - No code generation should occur
        """
        # Mock parser to raise exception
        self.mock_mermaid_parser.parse_class_diagram.side_effect = ValueError("Invalid syntax")
        
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=self.output_dir
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("Invalid syntax", result['errors'][0])
        
        # Verify no generation occurred
        self.mock_python_code_generator.generate_class_code.assert_not_called()

    def test_convert_with_code_generation_failure(self):
        """
        Test convert() when Python code generation fails for some classes.
        
        Pseudocode:
        1. Setup successful parsing
        2. Mock code generator to fail for one class
        3. Call convert() and verify partial success
        4. Verify warnings are generated for failed classes
        
        Expected behavior:
        - Should continue processing other classes after failure
        - Failed classes should be reported as warnings
        - Overall conversion should still succeed if some classes work
        """
        # Setup parsing success
        parsed_data = {
            'classes': [
                {'name': 'Animal', 'attributes': [], 'methods': []},
                {'name': 'Dog', 'attributes': [], 'methods': []}
            ]
        }
        self.mock_mermaid_parser.parse_class_diagram.return_value = parsed_data
        
        # Mock generator to fail for second class
        def generate_side_effect(class_def, options):
            if class_def['name'] == 'Dog':
                raise ValueError("Generation failed for Dog")
            return f"class {class_def['name']}:\n    pass"
        
        self.mock_python_code_generator.generate_class_code.side_effect = generate_side_effect
        self.mock_python_code_generator.generate_init_file.return_value = "# Init"
        
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=self.output_dir
        )
        
        # Verify partial success
        self.assertTrue(result['success'])
        self.assertEqual(result['classes_generated'], 1)  # Only Animal succeeded
        self.assertGreater(len(result['warnings']), 0)
        self.assertIn("Dog", result['warnings'][0])

    def test_convert_with_file_writing_failure(self):
        """
        Test convert() when file writing fails.
        
        Pseudocode:
        1. Setup successful parsing and generation
        2. Mock file writer to raise exception
        3. Call convert() and verify error handling
        
        Expected behavior:
        - Should return failure result
        - Error should mention file writing issue
        """
        # Setup successful parsing and generation
        parsed_data = {'classes': [{'name': 'Animal', 'attributes': [], 'methods': []}]}
        self.mock_mermaid_parser.parse_class_diagram.return_value = parsed_data
        self.mock_python_code_generator.generate_class_code.return_value = "class Animal: pass"
        self.mock_python_code_generator.generate_init_file.return_value = "# Init"
        
        # Mock file writer to fail
        self.mock_file_writer.write_python_file.side_effect = IOError("Permission denied")
        
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=self.output_dir
        )
        
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn("Permission denied", result['errors'][0])

    def test_convert_with_custom_options(self):
        """
        Test convert() with custom generation options.
        
        Pseudocode:
        1. Call convert() with custom options (no init files, no docstrings, etc.)
        2. Verify options are passed correctly to generation steps
        3. Verify behavior changes based on options
        
        Expected behavior:
        - Custom options should be passed to generators
        - Init file generation should be skipped when requested
        - All custom options should be respected
        """
        # Setup successful pipeline
        parsed_data = {'classes': [{'name': 'Animal', 'attributes': [], 'methods': []}]}
        self.mock_mermaid_parser.parse_class_diagram.return_value = parsed_data
        self.mock_python_code_generator.generate_class_code.return_value = "class Animal: pass"
        
        result = self.converter.convert(
            input_file_path=self.input_file,
            output_directory=self.output_dir,
            overwrite_existing=True,
            generate_init_files=False,
            include_docstrings=False,
            include_type_hints=False,
            naming_convention='preserve'
        )
        
        # Verify options were passed correctly
        call_args = self.mock_python_code_generator.generate_class_code.call_args
        options = call_args[0][1]  # Second argument is options
        
        self.assertTrue(options['overwrite_existing'])
        self.assertFalse(options['generate_init_files'])
        self.assertFalse(options['include_docstrings'])
        self.assertFalse(options['include_type_hints'])
        self.assertEqual(options['naming_convention'], 'preserve')
        
        # Verify init file not generated
        self.mock_python_code_generator.generate_init_file.assert_not_called()
        self.assertNotIn('__init__.py', result['generated_files'])


class TestClassDiagramToPythonFilesHelperMethods(unittest.TestCase):
    """
    Test suite for helper methods of ClassDiagramToPythonFiles.
    
    Tests cover:
    - Input validation logic
    - Filename generation
    - File extension validation
    - Naming convention handling
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        """
        # Create mock dependencies
        self.mock_logger = MagicMock()
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()
        
        self.valid_resources = {
            'logger': self.mock_logger,
            'mermaid_parser': self.mock_mermaid_parser,
            'python_code_generator': self.mock_python_code_generator,
            'file_writer': self.mock_file_writer
        }
        
        self.converter = ClassDiagramToPythonFiles(
            resources=self.valid_resources,
            configs=MagicMock()
        )
        
        # Create temporary test files
        self.test_dir = tempfile.mkdtemp()
        self.valid_file = os.path.join(self.test_dir, "test.md")
        with open(self.valid_file, 'w') as f:
            f.write("test content")

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_class_filename_snake_case(self):
        """
        Test filename generation with snake_case convention.
        
        Pseudocode:
        1. Call _get_class_filename with CamelCase class name
        2. Verify conversion to snake_case
        3. Test various naming patterns
        
        Expected behavior:
        - CamelCase should convert to snake_case
        - Proper .py extension should be added
        """
        options = {'naming_convention': 'snake_case'}
        
        # Test various class name patterns
        test_cases = [
            ('Animal', 'animal.py'),
            ('DogBreed', 'dog_breed.py'),
            ('XMLHttpRequest', 'x_m_l_http_request.py'),
            ('SimpleClass', 'simple_class.py')
        ]
        
        for class_name, expected_filename in test_cases:
            result = self.converter._get_class_filename(class_name, options)
            self.assertEqual(result, expected_filename)

    def test_get_class_filename_preserve_convention(self):
        """
        Test filename generation with preserve convention.
        
        Pseudocode:
        1. Call _get_class_filename with preserve option
        2. Verify original class name is preserved
        3. Verify .py extension is added
        
        Expected behavior:
        - Original class name should be preserved exactly
        - Only .py extension should be added
        """
        options = {'naming_convention': 'preserve'}
        
        test_cases = [
            ('Animal', 'Animal.py'),
            ('DogBreed', 'DogBreed.py'),
            ('XMLHttpRequest', 'XMLHttpRequest.py')
        ]
        
        for class_name, expected_filename in test_cases:
            result = self.converter._get_class_filename(class_name, options)
            self.assertEqual(result, expected_filename)

    def test_get_class_filename_default_convention(self):
        """
        Test filename generation with default/unspecified convention.
        
        Pseudocode:
        1. Call _get_class_filename without naming_convention in options
        2. Verify default behavior (should be snake_case)
        
        Expected behavior:
        - Should default to snake_case conversion
        """
        options = {}  # No naming_convention specified
        
        result = self.converter._get_class_filename('DogBreed', options)
        self.assertEqual(result, 'dog_breed.py')

    def test_validate_inputs_with_valid_parameters(self):
        """
        Test _validate_inputs with valid file and directory.
        
        Pseudocode:
        1. Call _validate_inputs with valid file path and output directory
        2. Verify no exceptions are raised
        
        Expected behavior:
        - No exceptions should be raised for valid inputs
        """
        try:
            self.converter._validate_inputs(self.valid_file, "/tmp/output")
        except Exception as e:
            self.fail(f"Validation failed unexpectedly: {e}")

    def test_validate_inputs_with_nonexistent_file(self):
        """
        Test _validate_inputs with non-existent input file.
        
        Pseudocode:
        1. Call _validate_inputs with non-existent file path
        2. Verify FileNotFoundError is raised
        
        Expected behavior:
        - FileNotFoundError should be raised
        """
        with self.assertRaises(FileNotFoundError):
            self.converter._validate_inputs("/nonexistent/file.md", "/tmp/output")

    def test_validate_inputs_with_empty_file_path(self):
        """
        Test _validate_inputs with empty input file path.
        
        Pseudocode:
        1. Call _validate_inputs with empty string as file path
        2. Verify ValueError is raised
        
        Expected behavior:
        - ValueError should be raised with appropriate message
        """
        with self.assertRaises(ValueError) as context:
            self.converter._validate_inputs("", "/tmp/output")
        
        self.assertIn("Input file path cannot be empty", str(context.exception))

    def test_validate_inputs_with_empty_output_directory(self):
        """
        Test _validate_inputs with empty output directory.
        
        Pseudocode:
        1. Call _validate_inputs with empty string as output directory
        2. Verify ValueError is raised
        
        Expected behavior:
        - ValueError should be raised with appropriate message
        """
        with self.assertRaises(ValueError) as context:
            self.converter._validate_inputs(self.valid_file, "")
        
        self.assertIn("Output directory cannot be empty", str(context.exception))

    def test_validate_inputs_with_directory_as_input_file(self):
        """
        Test _validate_inputs when input path points to a directory instead of file.
        
        Pseudocode:
        1. Create a directory and pass it as input file path
        2. Call _validate_inputs
        3. Verify ValueError is raised
        
        Expected behavior:
        - ValueError should be raised indicating path is not a file
        """
        test_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(test_dir)
        
        with self.assertRaises(ValueError) as context:
            self.converter._validate_inputs(test_dir, "/tmp/output")
        
        self.assertIn("Input path is not a file", str(context.exception))

    def test_validate_inputs_with_invalid_file_extension_warning(self):
        """
        Test _validate_inputs with unexpected file extension.
        
        Pseudocode:
        1. Create file with unexpected extension (e.g., .txt)
        2. Call _validate_inputs
        3. Verify warning is logged but no exception is raised
        
        Expected behavior:
        - Should not raise exception
        - Should log warning about unexpected extension
        """
        invalid_ext_file = os.path.join(self.test_dir, "test.xyz")
        with open(invalid_ext_file, 'w') as f:
            f.write("test content")
        
        # Should not raise exception
        try:
            self.converter._validate_inputs(invalid_ext_file, "/tmp/output")
        except Exception as e:
            self.fail(f"Validation failed unexpectedly: {e}")
        
        # Verify warning was logged
        self.mock_logger.warning.assert_called()
        warning_call = self.mock_logger.warning.call_args[0][0]
        self.assertIn("Unexpected file extension", warning_call)

    def test_parse_mermaid_content_successful(self):
        """
        Test _parse_mermaid_content with valid Mermaid content.
        
        Pseudocode:
        1. Setup mock parser to return valid parsed data
        2. Call _parse_mermaid_content with sample content
        3. Verify parser is called correctly
        4. Verify parsed data is returned
        
        Expected behavior:
        - Parser should be called with provided content
        - Parsed data should be returned unchanged
        - Success should be logged
        """
        test_content = "classDiagram\n    class Animal"
        expected_data = {'classes': [{'name': 'Animal'}]}
        
        self.mock_mermaid_parser.parse_class_diagram.return_value = expected_data
        
        result = self.converter._parse_mermaid_content(test_content)
        
        # Verify parser call
        self.mock_mermaid_parser.parse_class_diagram.assert_called_once_with(test_content)
        
        # Verify result
        self.assertEqual(result, expected_data)
        
        # Verify logging
        self.mock_logger.info.assert_any_call("Parsing Mermaid class diagram content")

    def test_parse_mermaid_content_with_syntax_validation(self):
        """
        Test _parse_mermaid_content when parser has syntax validation.
        
        Pseudocode:
        1. Add validate_syntax method to mock parser
        2. Set validation to return True
        3. Call _parse_mermaid_content
        4. Verify validation is called before parsing
        
        Expected behavior:
        - validate_syntax should be called if available
        - Parsing should proceed if validation passes
        """
        test_content = "classDiagram\n    class Animal"
        expected_data = {'classes': [{'name': 'Animal'}]}
        
        # Add validate_syntax method to parser
        self.mock_mermaid_parser.validate_syntax = MagicMock(return_value=True)
        self.mock_mermaid_parser.parse_class_diagram.return_value = expected_data
        
        result = self.converter._parse_mermaid_content(test_content)
        
        # Verify validation was called
        self.mock_mermaid_parser.validate_syntax.assert_called_once_with(test_content)
        
        # Verify parsing proceeded
        self.mock_mermaid_parser.parse_class_diagram.assert_called_once_with(test_content)
        self.assertEqual(result, expected_data)

    def test_parse_mermaid_content_with_failed_syntax_validation(self):
        """
        Test _parse_mermaid_content when syntax validation fails.
        
        Pseudocode:
        1. Add validate_syntax method that returns False
        2. Call _parse_mermaid_content
        3. Verify ValueError is raised
        4. Verify parsing is not attempted
        
        Expected behavior:
        - ValueError should be raised for invalid syntax
        - Parsing should not be attempted after validation failure
        """
        test_content = "invalid mermaid content"
        
        # Add validate_syntax method that fails
        self.mock_mermaid_parser.validate_syntax = MagicMock(return_value=False)
        
        with self.assertRaises(ValueError) as context:
            self.converter._parse_mermaid_content(test_content)
        
        self.assertIn("Invalid Mermaid class diagram syntax", str(context.exception))
        
        # Verify parsing was not attempted
        self.mock_mermaid_parser.parse_class_diagram.assert_not_called()

    def test_parse_mermaid_content_with_empty_result(self):
        """
        Test _parse_mermaid_content when parser returns empty/None data.
        
        Pseudocode:
        1. Mock parser to return None or empty data
        2. Call _parse_mermaid_content
        3. Verify ValueError is raised
        
        Expected behavior:
        - ValueError should be raised when no data is extracted
        """
        test_content = "classDiagram\n    # empty diagram"
        
        self.mock_mermaid_parser.parse_class_diagram.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.converter._parse_mermaid_content(test_content)
        
        self.assertIn("Failed to parse Mermaid content - no data extracted", str(context.exception))


class TestClassDiagramToPythonFilesGenerationMethods(unittest.TestCase):
    """
    Test suite for code generation methods of ClassDiagramToPythonFiles.
    
    Tests cover:
    - Python class code generation pipeline
    - Init file generation
    - Error handling during generation
    - Options passing and handling
    """

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        # Create mock dependencies
        self.mock_logger = MagicMock()
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()
        
        self.valid_resources = {
            'logger': self.mock_logger,
            'mermaid_parser': self.mock_mermaid_parser,
            'python_code_generator': self.mock_python_code_generator,
            'file_writer': self.mock_file_writer
        }
        
        self.converter = ClassDiagramToPythonFiles(
            resources=self.valid_resources,
            configs=MagicMock()
        )

    def test_generate_python_classes_successful(self):
        """
        Test _generate_python_classes with successful generation.
        
        Pseudocode:
        1. Setup parsed data with multiple classes
        2. Mock code generator to return valid Python code
        3. Call _generate_python_classes
        4. Verify all classes are processed
        5. Verify init file is generated
        
        Expected behavior:
        - Each class should be processed individually
        - Generated code should be collected properly
        - Init file should be generated when requested
        """
        parsed_data = {
            'classes': [
                {'name': 'Animal', 'attributes': ['name'], 'methods': ['move']},
                {'name': 'Dog', 'attributes': ['breed'], 'methods': ['bark']}
            ]
        }
        
        options = {'generate_init_files': True, 'naming_convention': 'snake_case'}
        
        # Mock code generation
        def generate_class_side_effect(class_def, opts):
            return f"class {class_def['name']}:\n    pass"
        
        self.mock_python_code_generator.generate_class_code.side_effect = generate_class_side_effect
        self.mock_python_code_generator.generate_init_file.return_value = "# Init file content"
        
        result = self.converter._generate_python_classes(parsed_data, options)
        
        # Verify all classes processed
        self.assertEqual(len(result['classes']), 2)
        self.assertEqual(result['classes'][0]['name'], 'Animal')
        self.assertEqual(result['classes'][1]['name'], 'Dog')
        
        # Verify filenames
        self.assertEqual(result['classes'][0]['filename'], 'animal.py')
        self.assertEqual(result['classes'][1]['filename'], 'dog.py')
        
        # Verify init file
        self.assertIn('init_file', result)
        self.assertEqual(result['init_file']['filename'], '__init__.py')
        
        # Verify files list
        expected_files = ['animal.py', 'dog.py', '__init__.py']
        self.assertEqual(sorted(result['files']), sorted(expected_files))

    def test_generate_python_classes_with_generation_errors(self):
        """
        Test _generate_python_classes when some classes fail to generate.
        
        Pseudocode:
        1. Setup parsed data with multiple classes
        2. Mock generator to fail for one class
        3. Call _generate_python_classes
        4. Verify successful classes are processed
        5. Verify failures are recorded as warnings
        
        Expected behavior:
        - Should continue processing after individual failures
        - Failures should be recorded as warnings
        - Successful classes should still be included in result
        """
        parsed_data = {
            'classes': [
                {'name': 'Animal', 'attributes': [], 'methods': []},
                {'name': 'InvalidClass', 'attributes': [], 'methods': []},
                {'name': 'Dog', 'attributes': [], 'methods': []}
            ]
        }
        
        options = {'generate_init_files': True}
        
        # Mock generator to fail for middle class
        def generate_class_side_effect(class_def, opts):
            if class_def['name'] == 'InvalidClass':
                raise ValueError("Generation failed for InvalidClass")
            return f"class {class_def['name']}:\n    pass"
        
        self.mock_python_code_generator.generate_class_code.side_effect = generate_class_side_effect
        self.mock_python_code_generator.generate_init_file.return_value = "# Init"
        
        result = self.converter._generate_python_classes(parsed_data, options)
        
        # Verify successful classes
        self.assertEqual(len(result['classes']), 2)
        class_names = [cls['name'] for cls in result['classes']]
        self.assertIn('Animal', class_names)
        self.assertIn('Dog', class_names)
        self.assertNotIn('InvalidClass', class_names)
        
        # Verify warning recorded
        self.assertEqual(len(result['warnings']), 1)
        self.assertIn('InvalidClass', result['warnings'][0])
        self.assertIn('Generation failed', result['warnings'][0])

    def test_generate_python_classes_without_init_files(self):
        """
        Test _generate_python_classes when init file generation is disabled.
        
        Pseudocode:
        1. Setup parsed data with classes
        2. Set generate_init_files option to False
        3. Call _generate_python_classes
        4. Verify init file is not generated
        5. Verify only class files are in result
        
        Expected behavior:
        - Init file should not be generated
        - generate_init_file should not be called
        - Only class files should be in files list
        """
        parsed_data = {
            'classes': [{'name': 'Animal', 'attributes': [], 'methods': []}]
        }
        
        options = {'generate_init_files': False}
        
        self.mock_python_code_generator.generate_class_code.return_value = "class Animal: pass"
        
        result = self.converter._generate_python_classes(parsed_data, options)
        
        # Verify no init file
        self.assertNotIn('init_file', result)
        self.assertNotIn('__init__.py', result['files'])
        
        # Verify init file generator not called
        self.mock_python_code_generator.generate_init_file.assert_not_called()

    def test_write_files_successful(self):
        """
        Test _write_files with successful file writing.
        
        Pseudocode:
        1. Setup class data with multiple files
        2. Mock file writer for success
        3. Call _write_files
        4. Verify directory creation
        5. Verify all files are written
        
        Expected behavior:
        - Output directory should be created
        - Each class file should be written
        - Init file should be written if present
        """
        class_data = {
            'classes': [
                {'name': 'Animal', 'code': 'class Animal: pass', 'filename': 'animal.py'},
                {'name': 'Dog', 'code': 'class Dog: pass', 'filename': 'dog.py'}
            ],
            'init_file': {'filename': '__init__.py', 'code': '# Init file'}
        }
        
        options = {'overwrite_existing': True, 'validate_syntax': False}
        output_dir = "/test/output"
        
        self.converter._write_files(class_data, output_dir, options)
        
        # Verify directory creation
        self.mock_file_writer.ensure_directory_exists.assert_called_once_with(output_dir)
        
        # Verify file writes
        expected_calls = [
            call('/test/output/animal.py', 'class Animal: pass', True),
            call('/test/output/dog.py', 'class Dog: pass', True),
            call('/test/output/__init__.py', '# Init file', True)
        ]
        
        self.mock_file_writer.write_python_file.assert_has_calls(expected_calls, any_order=True)

    def test_write_files_with_syntax_validation(self):
        """
        Test _write_files with syntax validation enabled.
        
        Pseudocode:
        1. Setup class data
        2. Add validate_python_syntax method to file writer
        3. Set validation to fail for one file
        4. Call _write_files
        5. Verify warning is logged for invalid syntax
        
        Expected behavior:
        - Syntax validation should be called for each file
        - Warnings should be logged for files with syntax issues
        - Files should still be written despite syntax warnings
        """
        class_data = {
            'classes': [
                {'name': 'Animal', 'code': 'class Animal: pass', 'filename': 'animal.py'},
                {'name': 'Invalid', 'code': 'invalid python code', 'filename': 'invalid.py'}
            ]
        }
        
        options = {'validate_syntax': True, 'overwrite_existing': False}
        output_dir = "/test/output"
        
        # Add syntax validation method
        def validate_syntax_side_effect(code):
            return "invalid python code" not in code
        
        self.mock_file_writer.validate_python_syntax = MagicMock(side_effect=validate_syntax_side_effect)
        
        self.converter._write_files(class_data, output_dir, options)
        
        # Verify syntax validation calls
        self.mock_file_writer.validate_python_syntax.assert_any_call('class Animal: pass')
        self.mock_file_writer.validate_python_syntax.assert_any_call('invalid python code')
        
        # Verify warning logged for invalid syntax
        warning_calls = [call[0][0] for call in self.mock_logger.warning.call_args_list]
        invalid_warnings = [w for w in warning_calls if 'Invalid' in w and 'syntax issues' in w]
        self.assertGreater(len(invalid_warnings), 0)


if __name__ == "__main__":
    unittest.main()