#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for main.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from pathlib import Path
import sys
import tempfile
import os
from typing import Dict, List, Any, Optional
import argparse

# Import modules under test
try:
    # We need to mock the imports since they're relative imports in the actual module
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype')
    import tools.cli.mermaid_to_prototype.main as main
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestMainFunction(unittest.TestCase):
    """
    Comprehensive unit tests for the main() function in main.py.
    
    Tests cover:
    - Argument parsing validation
    - File existence validation
    - Chart type selection logic
    - Error handling scenarios
    - Success path execution
    - Integration with maker modules
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates temporary files and directories for testing,
        and sets up mock objects for external dependencies.
        """
        # Create temporary directory and files for testing
        self.test_dir = tempfile.mkdtemp()
        self.valid_input_file = Path(self.test_dir) / "test_diagram.md"
        self.valid_input_file.write_text("# Test Mermaid Diagram\n```mermaid\nclassDiagram\n```")
        
        self.invalid_input_file = Path(self.test_dir) / "nonexistent.md"
        self.output_file = Path(self.test_dir) / "output.py"
        
        # Mock maker objects
        self.mock_class_maker = MagicMock()
        self.mock_class_maker.make.return_value = True
        
        self.mock_flowchart_maker = MagicMock()
        self.mock_flowchart_maker.make.return_value = True
        
        self.mock_erd_maker = MagicMock()
        self.mock_erd_maker.make.return_value = True

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Removes temporary files and directories created during testing.
        """
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('main.make_class_diagram_to_python_files')
    @patch('main.make_flowchart_to_directory_tree')
    @patch('main.make_entity_relationship_diagram_to_sql_schema')
    @patch('sys.argv')
    def test_main_with_valid_input_all_types(self, mock_argv, mock_erd_factory, 
                                           mock_flowchart_factory, mock_class_factory):
        """
        Test main() function with valid input file and 'all' chart types.
        
        Pseudocode:
        1. Mock sys.argv with valid arguments for 'all' type
        2. Mock factory functions to return maker objects
        3. Call main() function
        4. Verify all maker objects are created and called
        5. Verify success message and exit code
        
        Expected behavior:
        - All three maker factories should be called
        - Each maker.make() should be called with parsed args
        - Function should exit with code 0
        - Success message should be printed
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'all'
        ][x]
        mock_argv.__len__.return_value = 4
        
        mock_class_factory.return_value = self.mock_class_maker
        mock_flowchart_factory.return_value = self.mock_flowchart_maker
        mock_erd_factory.return_value = self.mock_erd_maker
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify factory calls
            mock_class_factory.assert_called_once()
            mock_flowchart_factory.assert_called_once()
            mock_erd_factory.assert_called_once()
            
            # Verify maker.make() calls
            self.mock_class_maker.make.assert_called_once()
            self.mock_flowchart_maker.make.assert_called_once()
            self.mock_erd_maker.make.assert_called_once()
            
            # Verify success exit
            mock_exit.assert_called_once_with(0)
            mock_print.assert_called_with(
                f"Successfully converted {self.valid_input_file} to output.py"
            )

    @patch('main.make_class_diagram_to_python_files')
    @patch('sys.argv')
    def test_main_with_class_diagram_type_only(self, mock_argv, mock_class_factory):
        """
        Test main() function with 'class_diagram' type specification.
        
        Pseudocode:
        1. Mock sys.argv with arguments for 'class_diagram' type only
        2. Mock class diagram factory function
        3. Call main() function
        4. Verify only class diagram maker is created and called
        5. Verify other makers are not called
        
        Expected behavior:
        - Only class diagram factory should be called
        - Only class diagram maker.make() should be called
        - Function should exit with code 0
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'class_diagram'
        ][x]
        mock_argv.__len__.return_value = 4
        
        mock_class_factory.return_value = self.mock_class_maker
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify only class diagram factory called
            mock_class_factory.assert_called_once()
            self.mock_class_maker.make.assert_called_once()
            
            # Verify success
            mock_exit.assert_called_once_with(0)

    @patch('sys.argv')
    def test_main_with_invalid_input_file(self, mock_argv):
        """
        Test main() function with non-existent input file.
        
        Pseudocode:
        1. Mock sys.argv with path to non-existent file
        2. Call main() function
        3. Verify error message is printed
        4. Verify function exits with code 1
        
        Expected behavior:
        - Error message about invalid file should be printed
        - Function should exit with code 1
        - No maker objects should be created
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.invalid_input_file)
        ][x]
        mock_argv.__len__.return_value = 2
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify error handling
            mock_print.assert_called_with(
                f"Error: '{self.invalid_input_file}' is not a valid file."
            )
            mock_exit.assert_called_once_with(1)

    @patch('main.make_class_diagram_to_python_files')
    @patch('sys.argv')
    def test_main_with_maker_exception(self, mock_argv, mock_class_factory):
        """
        Test main() function when maker.make() raises an exception.
        
        Pseudocode:
        1. Mock sys.argv with valid arguments
        2. Mock class factory to return maker that raises exception
        3. Call main() function
        4. Verify RuntimeError is raised with proper message
        5. Verify original exception is preserved as cause
        
        Expected behavior:
        - RuntimeError should be raised
        - Original exception should be preserved in the chain
        - Error message should include exception type and message
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'class_diagram'
        ][x]
        mock_argv.__len__.return_value = 4
        
        # Make the maker raise an exception
        test_exception = ValueError("Test parsing error")
        self.mock_class_maker.make.side_effect = test_exception
        mock_class_factory.return_value = self.mock_class_maker
        
        # Test execution
        with self.assertRaises(RuntimeError) as context:
            main.main()
        
        # Verify exception details
        self.assertIn("ValueError occurred during conversion", str(context.exception))
        self.assertIn("Test parsing error", str(context.exception))
        self.assertEqual(context.exception.__cause__, test_exception)

    @patch('main.make_class_diagram_to_python_files')
    @patch('sys.argv')
    def test_main_with_maker_returning_false(self, mock_argv, mock_class_factory):
        """
        Test main() function when maker.make() returns False (failure).
        
        Pseudocode:
        1. Mock sys.argv with valid arguments
        2. Mock class factory to return maker that returns False
        3. Call main() function
        4. Verify RuntimeError is raised about conversion failure
        
        Expected behavior:
        - RuntimeError should be raised
        - Error message should indicate conversion failure
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'class_diagram'
        ][x]
        mock_argv.__len__.return_value = 4
        
        # Make the maker return False
        self.mock_class_maker.make.return_value = False
        mock_class_factory.return_value = self.mock_class_maker
        
        # Test execution
        with self.assertRaises(RuntimeError) as context:
            main.main()
        
        # Verify exception message
        self.assertIn("Conversion failed in some way", str(context.exception))

    @patch('sys.argv')
    def test_main_with_invalid_chart_type(self, mock_argv):
        """
        Test main() function with invalid chart type.
        
        Pseudocode:
        1. Mock sys.argv with invalid chart type
        2. Call main() function
        3. Verify error message about invalid type
        4. Verify function exits with code 1
        
        Expected behavior:
        - Error message about invalid type should be printed
        - Function should exit with code 1
        """
        # Setup mocks with invalid type
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'invalid_type'
        ][x]
        mock_argv.__len__.return_value = 4
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify error handling
            mock_print.assert_called_with(
                "Error: Invalid type 'invalid_type'. Choose from 'all', 'class_diagram', or 'flowchart'."
            )
            mock_exit.assert_called_once_with(1)

    @patch('main.make_flowchart_to_directory_tree')
    @patch('sys.argv')
    def test_main_with_flowchart_type_and_custom_output(self, mock_argv, mock_flowchart_factory):
        """
        Test main() function with flowchart type and custom output file.
        
        Pseudocode:
        1. Mock sys.argv with flowchart type and custom output
        2. Mock flowchart factory function
        3. Call main() function
        4. Verify flowchart maker is called with correct args
        5. Verify success message uses custom output path
        
        Expected behavior:
        - Only flowchart factory should be called
        - Success message should reference custom output file
        - Args passed to maker should include custom output
        """
        custom_output = self.test_dir + "/custom_output.py"
        
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'flowchart', 
            '--output', custom_output
        ][x]
        mock_argv.__len__.return_value = 6
        
        mock_flowchart_factory.return_value = self.mock_flowchart_maker
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify correct factory called
            mock_flowchart_factory.assert_called_once()
            self.mock_flowchart_maker.make.assert_called_once()
            
            # Verify args contain custom output
            call_args = self.mock_flowchart_maker.make.call_args[0][0]
            self.assertEqual(str(call_args.output), custom_output)
            
            # Verify success message
            mock_print.assert_called_with(
                f"Successfully converted {self.valid_input_file} to {custom_output}"
            )

    @patch('main.make_entity_relationship_diagram_to_sql_schema')
    @patch('sys.argv')
    def test_main_with_erd_type(self, mock_argv, mock_erd_factory):
        """
        Test main() function with entity_relationship_diagram type.
        
        Pseudocode:
        1. Mock sys.argv with ERD type specification
        2. Mock ERD factory function
        3. Call main() function
        4. Verify only ERD maker is created and called
        5. Verify success path
        
        Expected behavior:
        - Only ERD factory should be called
        - ERD maker.make() should be called once
        - Function should exit successfully
        """
        # Setup mocks
        mock_argv.__getitem__.side_effect = lambda x: [
            'main.py', str(self.valid_input_file), '--type', 'entity_relationship_diagram'
        ][x]
        mock_argv.__len__.return_value = 4
        
        mock_erd_factory.return_value = self.mock_erd_maker
        
        # Test execution
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main.main()
            
            # Verify only ERD factory called
            mock_erd_factory.assert_called_once()
            self.mock_erd_maker.make.assert_called_once()
            
            # Verify success
            mock_exit.assert_called_once_with(0)

    def test_supported_charts_constant(self):
        """
        Test that _SUPPORTED_CHARTS constant contains expected values.
        
        Pseudocode:
        1. Check that _SUPPORTED_CHARTS is a list
        2. Verify it contains all expected chart types
        3. Verify no unexpected types are present
        
        Expected behavior:
        - Should contain 'all', 'class_diagram', 'flowchart', 'entity_relationship_diagram'
        - Should be exactly these 4 values
        """
        expected_charts = ['all', 'class_diagram', 'flowchart', 'entity_relationship_diagram']
        
        self.assertIsInstance(main._SUPPORTED_CHARTS, list)
        self.assertEqual(len(main._SUPPORTED_CHARTS), 4)
        
        for chart_type in expected_charts:
            self.assertIn(chart_type, main._SUPPORTED_CHARTS)


class TestMainModuleAsScript(unittest.TestCase):
    """
    Test the main module when run as a script (__name__ == '__main__').
    
    Tests the exception handling wrapper that catches KeyboardInterrupt
    and other exceptions at the module level.
    """

    @patch('main.main')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_keyboard_interrupt_handling(self, mock_print, mock_exit, mock_main):
        """
        Test that KeyboardInterrupt is properly handled at module level.
        
        Pseudocode:
        1. Mock main() to raise KeyboardInterrupt
        2. Execute the __main__ block code
        3. Verify appropriate message is printed
        4. Verify sys.exit(0) is called
        
        Expected behavior:
        - Should print "Process interrupted by user."
        - Should exit with code 0
        """
        mock_main.side_effect = KeyboardInterrupt()
        
        # Simulate running as script
        with patch('__main__.__name__', '__main__'):
            try:
                if __name__ == '__main__':
                    try:
                        main.main()
                    except KeyboardInterrupt:
                        print("\nProcess interrupted by user.")
                        sys.exit(0)
            except SystemExit:
                pass  # Expected due to sys.exit call
        
        mock_print.assert_called_once_with("\nProcess interrupted by user.")
        mock_exit.assert_called_once_with(0)

    @patch('main.main')
    @patch('sys.exit')
    @patch('builtins.print')
    @patch('traceback.print_exc')
    def test_general_exception_handling(self, mock_traceback, mock_print, mock_exit, mock_main):
        """
        Test that general exceptions are properly handled at module level.
        
        Pseudocode:
        1. Mock main() to raise a general Exception
        2. Execute the __main__ block code
        3. Verify error message is printed
        4. Verify traceback is printed
        5. Verify sys.exit(1) is called
        
        Expected behavior:
        - Should print error message with exception type and message
        - Should print traceback
        - Should exit with code 1
        """
        test_exception = RuntimeError("Test error")
        mock_main.side_effect = test_exception
        
        # Simulate running as script
        with patch('__main__.__name__', '__main__'):
            try:
                if __name__ == '__main__':
                    try:
                        main.main()
                    except KeyboardInterrupt:
                        print("\nProcess interrupted by user.")
                        sys.exit(0)
                    except Exception as e:
                        import traceback
                        print(f"An unexpected {type(e).__name__} occurred: {e}")
                        traceback.print_exc()
                        sys.exit(1)
            except SystemExit:
                pass  # Expected due to sys.exit call
        
        mock_print.assert_called_once_with("An unexpected RuntimeError occurred: Test error")
        mock_traceback.assert_called_once()
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
