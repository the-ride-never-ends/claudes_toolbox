#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for class_diagram_to_python_files/factory.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from pathlib import Path
import sys
import tempfile
import os
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype')
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype/class_diagram_to_python_files')
    import tools.cli.mermaid_to_prototype.class_diagram_to_python_files.factory as factory
    from tools.cli.mermaid_to_prototype.class_diagram_to_python_files.class_diagram_to_python_files import ClassDiagramToPythonFiles
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestMakeClassDiagramToPythonFiles(unittest.TestCase):
    """
    Comprehensive unit tests for the make_class_diagram_to_python_files() factory function.
    
    Tests cover:
    - Factory function creation and dependency injection
    - Resource validation and configuration
    - Integration with logger, configs, and dependencies
    - Module imports and component wiring
    - Error handling for missing dependencies
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates mock objects for all dependencies that the factory function requires.
        """
        # Create mock logger
        self.mock_logger = MagicMock()
        self.mock_logger.info = MagicMock()
        self.mock_logger.error = MagicMock()
        self.mock_logger.warning = MagicMock()
        
        # Create mock configs
        self.mock_configs = MagicMock()
        self.mock_configs.name = "test_config"
        self.mock_configs.version = "1.0.0"
        
        # Create mock modules
        self.mock_mermaid_parser = MagicMock()
        self.mock_python_code_generator = MagicMock()
        self.mock_file_writer = MagicMock()

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Resets mock objects and clears any cached imports.
        """
        # Reset all mocks
        self.mock_logger.reset_mock()
        self.mock_configs.reset_mock()
        self.mock_mermaid_parser.reset_mock()
        self.mock_python_code_generator.reset_mock()
        self.mock_file_writer.reset_mock()

    @patch('factory.logger')
    @patch('factory.configs')
    @patch('factory.mermaid_parser')
    @patch('factory.python_code_generator')
    @patch('factory.file_writer')
    def test_make_class_diagram_to_python_files_success(self, mock_file_writer, mock_python_code_generator, 
                                                       mock_mermaid_parser, mock_configs, mock_logger):
        """
        Test successful creation of ClassDiagramToPythonFiles instance.
        
        Pseudocode:
        1. Mock all required dependencies (logger, configs, modules)
        2. Call make_class_diagram_to_python_files()
        3. Verify ClassDiagramToPythonFiles instance is created
        4. Verify all dependencies are properly injected
        5. Verify resources dictionary contains all required components
        6. Verify configs object is passed correctly
        
        Expected behavior:
        - Should return ClassDiagramToPythonFiles instance
        - Should inject all required dependencies
        - Should include logger, mermaid_parser, python_code_generator, file_writer in resources
        - Should pass configs object to constructor
        """
        # Setup mocks
        mock_logger.return_value = self.mock_logger
        mock_configs.return_value = self.mock_configs
        mock_mermaid_parser.return_value = self.mock_mermaid_parser
        mock_python_code_generator.return_value = self.mock_python_code_generator
        mock_file_writer.return_value = self.mock_file_writer
        
        # Test execution
        result = factory.make_class_diagram_to_python_files()
        
        # Verify return type
        self.assertIsInstance(result, ClassDiagramToPythonFiles)
        
        # Verify dependencies were injected
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.configs)
        
        # Verify resources dictionary contains all required components
        expected_resources = {'logger', 'mermaid_parser', 'python_code_generator', 'file_writer'}
        self.assertEqual(set(result.resources.keys()), expected_resources)
        
        # Verify each resource is properly assigned
        self.assertEqual(result.resources['logger'], mock_logger)
        self.assertEqual(result.resources['mermaid_parser'], mock_mermaid_parser)
        self.assertEqual(result.resources['python_code_generator'], mock_python_code_generator)
        self.assertEqual(result.resources['file_writer'], mock_file_writer)
        
        # Verify configs object
        self.assertEqual(result.configs, mock_configs)

    @patch('factory.make_class_diagram_to_python_files')
    def test_get_default_instance_delegates_to_factory(self, mock_factory):
        """
        Test that get_default_instance() delegates to make_class_diagram_to_python_files().
        
        Pseudocode:
        1. Mock make_class_diagram_to_python_files() function
        2. Call get_default_instance()
        3. Verify make_class_diagram_to_python_files() was called once
        4. Verify get_default_instance() returns the same result
        5. Verify no additional parameters are passed
        
        Expected behavior:
        - Should call make_class_diagram_to_python_files() exactly once
        - Should return the same instance returned by factory function
        - Should not modify or wrap the returned instance
        """
        # Setup mock
        mock_instance = MagicMock(spec=ClassDiagramToPythonFiles)
        mock_factory.return_value = mock_instance
        
        # Test execution
        result = factory.get_default_instance()
        
        # Verify delegation
        mock_factory.assert_called_once()
        
        # Verify no parameters passed
        call_args = mock_factory.call_args
        self.assertEqual(len(call_args.args), 0)
        self.assertEqual(len(call_args.kwargs), 0)
        
        # Verify return value
        self.assertEqual(result, mock_instance)


if __name__ == "__main__":
    unittest.main()
