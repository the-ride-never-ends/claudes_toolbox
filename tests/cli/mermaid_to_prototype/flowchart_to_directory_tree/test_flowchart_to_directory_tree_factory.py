#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for flowchart_to_directory_tree/factory.py
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
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype/flowchart_to_directory_tree')
    import tools.cli.mermaid_to_prototype.flowchart_to_directory_tree.factory as factory
    from tools.cli.mermaid_to_prototype.flowchart_to_directory_tree.flowchart_to_directory_tree import FlowchartToDirectoryTree
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestMakeFlowchartToDirectoryTree(unittest.TestCase):
    """
    Comprehensive unit tests for the make_flowchart_to_directory_tree() factory function.
    
    Tests cover:
    - Factory function creation with default dependencies
    - Custom resource and config injection
    - Component instantiation and wiring
    - Error handling for missing dependencies
    - Resource merging and overrides
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates mock objects for all components that the factory function requires.
        """
        # Create mock components
        self.mock_parser = MagicMock()
        self.mock_validator = MagicMock()
        self.mock_converter = MagicMock()
        self.mock_creator = MagicMock()
        self.mock_logger = MagicMock()
        self.mock_configs = MagicMock()

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Resets all mock objects.
        """
        for mock_obj in [self.mock_parser, self.mock_validator, self.mock_converter, 
                        self.mock_creator, self.mock_logger, self.mock_configs]:
            mock_obj.reset_mock()

    @patch('factory.MermaidParser')
    @patch('factory.FlowchartValidator')
    @patch('factory.DirectoryTreeConverter')
    @patch('factory.DirectoryCreator')
    @patch('factory.logger')
    @patch('factory.configs')
    def test_make_flowchart_to_directory_tree_default_creation(self, mock_configs, mock_logger,
                                                             mock_creator_class, mock_converter_class,
                                                             mock_validator_class, mock_parser_class):
        """
        Test factory function with default parameters.
        
        Pseudocode:
        1. Mock all component classes and dependencies
        2. Call make_flowchart_to_directory_tree() with no parameters
        3. Verify FlowchartToDirectoryTree instance is created
        4. Verify all component classes are instantiated
        5. Verify resources dictionary contains all required components
        6. Verify configs object is passed correctly
        
        Expected behavior:
        - Should return FlowchartToDirectoryTree instance
        - Should instantiate all required component classes
        - Should inject all components into resources dictionary
        - Should use imported configs and logger
        """
        # Setup mocks
        mock_parser_class.return_value = self.mock_parser
        mock_validator_class.return_value = self.mock_validator
        mock_converter_class.return_value = self.mock_converter
        mock_creator_class.return_value = self.mock_creator
        
        # Test execution
        result = factory.make_flowchart_to_directory_tree()
        
        # Verify return type
        self.assertIsInstance(result, FlowchartToDirectoryTree)
        
        # Verify component instantiation
        mock_parser_class.assert_called_once()
        mock_validator_class.assert_called_once()
        mock_converter_class.assert_called_once()
        mock_creator_class.assert_called_once()
        
        # Verify resources were injected
        self.assertIsNotNone(result.resources)
        self.assertIsNotNone(result.configs)
        
        # Verify all required components in resources
        expected_resources = {'parser', 'validator', 'converter', 'creator', 'logger'}
        self.assertEqual(set(result.resources.keys()), expected_resources)

    @patch('factory.make_flowchart_to_directory_tree')
    def test_get_default_instance_delegates_to_factory(self, mock_factory):
        """
        Test that get_default_instance() properly delegates to main factory.
        
        Pseudocode:
        1. Mock make_flowchart_to_directory_tree() function
        2. Call get_default_instance()
        3. Verify factory function is called with no parameters
        4. Verify same result is returned
        
        Expected behavior:
        - Should call make_flowchart_to_directory_tree() with no parameters
        - Should return the same instance from factory function
        """
        mock_instance = MagicMock(spec=FlowchartToDirectoryTree)
        mock_factory.return_value = mock_instance
        
        # Test execution
        result = factory.get_default_instance()
        
        # Verify delegation
        mock_factory.assert_called_once_with()
        self.assertEqual(result, mock_instance)


if __name__ == "__main__":
    unittest.main()
