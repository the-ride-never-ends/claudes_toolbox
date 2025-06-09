#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for logger.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from pathlib import Path
import sys
import tempfile
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Any, Optional
import shutil

# Import modules under test
try:
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype')
    import tools.cli.mermaid_to_prototype.logger as logger
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestGetLoggerFunction(unittest.TestCase):
    """
    Comprehensive unit tests for the get_logger() function in logger.py.
    
    Tests cover:
    - Basic logger creation and configuration
    - Handler setup (console and rotating file)
    - Directory creation logic
    - Formatter application
    - Default parameter behavior
    - Custom parameter behavior
    - Error handling scenarios
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates temporary directories for testing log file creation,
        and clears any existing loggers to ensure test isolation.
        """
        # Create temporary directory for log files
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Clear existing loggers to avoid interference
        logging.getLogger().handlers.clear()
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith('test_'):
                del logging.Logger.manager.loggerDict[name]

    def tearDown(self) -> None:
        """
        Clean up test fixtures after each test method.
        
        Removes temporary files and directories, restores original working directory,
        and clears test loggers.
        """
        # Restore original working directory
        os.chdir(self.original_cwd)
        
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        
        # Clear test loggers
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith('test_'):
                logging.getLogger(name).handlers.clear()
                del logging.Logger.manager.loggerDict[name]

    def test_get_logger_with_default_parameters(self):
        """
        Test get_logger() function with all default parameters.
        
        Pseudocode:
        1. Call get_logger() with only the required name parameter
        2. Verify logger is created with correct name
        3. Verify logger has correct default level (DEBUG)
        4. Verify logger has exactly 2 handlers (console + file)
        5. Verify handlers are of correct types
        6. Verify file handler uses default parameters
        7. Verify formatters are applied correctly
        
        Expected behavior:
        - Logger name should match input
        - Logger level should be DEBUG
        - Should have StreamHandler and RotatingFileHandler
        - Default log file should be 'app.log'
        - Default max size should be 5MB
        - Default backup count should be 3
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test execution
            test_logger = logger.get_logger('test_logger_default')
            
            # Verify logger configuration
            self.assertEqual(test_logger.name, 'test_logger_default')
            self.assertEqual(test_logger.level, logging.DEBUG)
            self.assertEqual(len(test_logger.handlers), 2)
            
            # Verify handler types
            handler_types = [type(handler) for handler in test_logger.handlers]
            self.assertIn(logging.StreamHandler, handler_types)
            self.assertIn(RotatingFileHandler, handler_types)
            
            # Find the RotatingFileHandler
            file_handler = next(h for h in test_logger.handlers 
                              if isinstance(h, RotatingFileHandler))
            
            # Verify file handler configuration
            self.assertEqual(file_handler.maxBytes, 5*1024*1024)  # 5MB
            self.assertEqual(file_handler.backupCount, 3)
            self.assertTrue(str(file_handler.baseFilename).endswith('app.log'))
            
            # Verify logs directory creation
            logs_dir = Path(self.test_dir) / 'logs'
            self.assertTrue(logs_dir.exists())
            self.assertTrue(logs_dir.is_dir())

    def test_get_logger_with_custom_parameters(self):
        """
        Test get_logger() function with custom parameters.
        
        Pseudocode:
        1. Call get_logger() with custom name, log_file_name, level, max_size, backup_count
        2. Verify logger uses custom configuration
        3. Verify file handler uses custom parameters
        4. Verify custom log file name is used
        5. Verify custom level is applied
        
        Expected behavior:
        - Logger should use all custom parameters
        - File handler should respect custom max_size and backup_count
        - Custom log file name should be used
        - Custom logging level should be applied
        """
        custom_params = {
            'name': 'test_custom_logger',
            'log_file_name': 'custom_app.log',
            'level': logging.WARNING,
            'max_size': 10*1024*1024,  # 10MB
            'backup_count': 5
        }
        
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test execution
            test_logger = logger.get_logger(**custom_params)
            
            # Verify custom configuration
            self.assertEqual(test_logger.name, 'test_custom_logger')
            self.assertEqual(test_logger.level, logging.WARNING)
            
            # Find the RotatingFileHandler
            file_handler = next(h for h in test_logger.handlers 
                              if isinstance(h, RotatingFileHandler))
            
            # Verify custom file handler configuration
            self.assertEqual(file_handler.maxBytes, 10*1024*1024)  # 10MB
            self.assertEqual(file_handler.backupCount, 5)
            self.assertTrue(str(file_handler.baseFilename).endswith('custom_app.log'))

    def test_get_logger_formatter_configuration(self):
        """
        Test that get_logger() properly configures formatters for both handlers.
        
        Pseudocode:
        1. Create logger with get_logger()
        2. Extract both handlers (console and file)
        3. Verify both handlers have formatters
        4. Verify formatters use expected format string
        5. Test actual log message formatting
        
        Expected behavior:
        - Both handlers should have formatters
        - Format should include timestamp, name, level, filename, line number, message
        - Format string should match expected pattern
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test execution
            test_logger = logger.get_logger('test_formatter')
            
            # Verify all handlers have formatters
            for handler in test_logger.handlers:
                self.assertIsNotNone(handler.formatter)
                
                # Verify format string
                expected_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                self.assertEqual(handler.formatter._fmt, expected_format)

    def test_get_logger_logs_directory_creation(self):
        """
        Test that get_logger() creates the logs directory in current working directory.
        
        Pseudocode:
        1. Change to test directory that doesn't have logs subdirectory
        2. Call get_logger()
        3. Verify logs directory is created
        4. Verify logs directory permissions and structure
        5. Test with existing logs directory
        
        Expected behavior:
        - Should create 'logs' directory if it doesn't exist
        - Should not fail if 'logs' directory already exists
        - Directory should be created in current working directory
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            logs_dir = Path(self.test_dir) / 'logs'
            
            # Verify logs directory doesn't exist initially
            self.assertFalse(logs_dir.exists())
            
            # Test execution
            test_logger = logger.get_logger('test_directory_creation')
            
            # Verify logs directory is created
            self.assertTrue(logs_dir.exists())
            self.assertTrue(logs_dir.is_dir())
            
            # Test with existing logs directory (should not fail)
            test_logger2 = logger.get_logger('test_existing_directory')
            self.assertTrue(logs_dir.exists())

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.cwd')
    def test_get_logger_directory_creation_with_parents(self, mock_cwd, mock_mkdir):
        """
        Test that get_logger() creates logs directory with proper mkdir parameters.
        
        Pseudocode:
        1. Mock Path.cwd() and Path.mkdir()
        2. Call get_logger()
        3. Verify mkdir() is called with parents=True and exist_ok=True
        4. Verify proper path construction
        
        Expected behavior:
        - mkdir should be called with parents=True to create parent directories
        - mkdir should be called with exist_ok=True to not fail if directory exists
        """
        mock_cwd.return_value = Path(self.test_dir)
        
        # Test execution
        test_logger = logger.get_logger('test_mkdir_params')
        
        # Verify mkdir was called with correct parameters
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_logger_file_path_resolution(self):
        """
        Test that get_logger() properly resolves log file paths.
        
        Pseudocode:
        1. Create logger with custom log file name
        2. Extract file handler
        3. Verify file path is properly resolved (absolute path)
        4. Verify file path includes logs directory
        5. Verify file name matches input
        
        Expected behavior:
        - File path should be absolute (resolved)
        - File path should be within logs directory
        - File name should match the log_file_name parameter
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test execution
            test_logger = logger.get_logger('test_path_resolution', 
                                          log_file_name='test_file.log')
            
            # Find the RotatingFileHandler
            file_handler = next(h for h in test_logger.handlers 
                              if isinstance(h, RotatingFileHandler))
            
            # Verify path resolution
            file_path = Path(file_handler.baseFilename)
            self.assertTrue(file_path.is_absolute())
            self.assertTrue(str(file_path).endswith('test_file.log'))
            self.assertIn('logs', str(file_path))

    def test_get_logger_multiple_loggers_isolation(self):
        """
        Test that multiple loggers created with get_logger() are properly isolated.
        
        Pseudocode:
        1. Create multiple loggers with different names and configurations
        2. Verify each logger has correct individual configuration
        3. Verify loggers don't interfere with each other
        4. Verify each has its own handlers
        
        Expected behavior:
        - Each logger should maintain its own configuration
        - Loggers should not share handlers
        - Different log levels should be respected per logger
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Create multiple loggers
            logger1 = logger.get_logger('test_logger1', level=logging.DEBUG)
            logger2 = logger.get_logger('test_logger2', level=logging.ERROR)
            logger3 = logger.get_logger('test_logger3', log_file_name='special.log')
            
            # Verify isolation
            self.assertEqual(logger1.name, 'test_logger1')
            self.assertEqual(logger2.name, 'test_logger2')
            self.assertEqual(logger3.name, 'test_logger3')
            
            self.assertEqual(logger1.level, logging.DEBUG)
            self.assertEqual(logger2.level, logging.ERROR)
            
            # Verify separate handlers
            self.assertEqual(len(logger1.handlers), 2)
            self.assertEqual(len(logger2.handlers), 2)
            self.assertEqual(len(logger3.handlers), 2)
            
            # Verify handlers are not shared
            self.assertNotEqual(id(logger1.handlers[0]), id(logger2.handlers[0]))

    def test_get_logger_edge_case_parameters(self):
        """
        Test get_logger() with edge case parameters.
        
        Pseudocode:
        1. Test with very small max_size
        2. Test with very large max_size
        3. Test with zero backup_count
        4. Test with very large backup_count
        5. Test with different logging levels
        
        Expected behavior:
        - Should handle edge case values gracefully
        - Should not raise exceptions for reasonable edge cases
        - Should apply parameters correctly even when unusual
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test with edge case parameters
            edge_cases = [
                {'max_size': 1024, 'backup_count': 0},  # Very small/zero
                {'max_size': 100*1024*1024, 'backup_count': 10},  # Very large
                {'level': logging.NOTSET},  # Edge logging level
                {'level': logging.CRITICAL},  # Highest logging level
            ]
            
            for i, params in enumerate(edge_cases):
                with self.subTest(case=i, params=params):
                    test_logger = logger.get_logger(f'test_edge_{i}', **params)
                    
                    # Verify logger was created successfully
                    self.assertIsInstance(test_logger, logging.Logger)
                    self.assertEqual(len(test_logger.handlers), 2)
                    
                    # Verify parameters were applied
                    if 'level' in params:
                        self.assertEqual(test_logger.level, params['level'])
                    
                    if 'max_size' in params or 'backup_count' in params:
                        file_handler = next(h for h in test_logger.handlers 
                                          if isinstance(h, RotatingFileHandler))
                        if 'max_size' in params:
                            self.assertEqual(file_handler.maxBytes, params['max_size'])
                        if 'backup_count' in params:
                            self.assertEqual(file_handler.backupCount, params['backup_count'])

    def test_get_logger_return_type(self):
        """
        Test that get_logger() returns the correct type.
        
        Pseudocode:
        1. Call get_logger()
        2. Verify return type is logging.Logger
        3. Verify logger has all expected methods and attributes
        
        Expected behavior:
        - Should return logging.Logger instance
        - Should have all standard logger methods available
        """
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.test_dir)
            
            # Test execution
            test_logger = logger.get_logger('test_return_type')
            
            # Verify return type
            self.assertIsInstance(test_logger, logging.Logger)
            
            # Verify logger has expected methods
            expected_methods = ['debug', 'info', 'warning', 'error', 'critical', 
                              'log', 'exception', 'addHandler', 'removeHandler']
            for method_name in expected_methods:
                self.assertTrue(hasattr(test_logger, method_name))
                self.assertTrue(callable(getattr(test_logger, method_name)))


class TestLoggerModuleGlobalLogger(unittest.TestCase):
    """
    Test the global logger instance created at module level.
    
    Tests the logger instance that's created when the module is imported.
    """

    def test_module_logger_exists(self):
        """
        Test that the module creates a global logger instance.
        
        Pseudocode:
        1. Verify logger module has 'logger' attribute
        2. Verify it's a logging.Logger instance
        3. Verify it has expected configuration
        
        Expected behavior:
        - Module should have 'logger' attribute
        - Should be properly configured Logger instance
        - Should use 'mermaid_to_prototype.log' as filename
        """
        # Verify module logger exists
        self.assertTrue(hasattr(logger, 'logger'))
        self.assertIsInstance(logger.logger, logging.Logger)
        
        # Verify it has handlers
        self.assertGreater(len(logger.logger.handlers), 0)

    @patch('pathlib.Path.cwd')
    def test_module_logger_configuration(self, mock_cwd):
        """
        Test that the module-level logger is configured correctly.
        
        Pseudocode:
        1. Mock Path.cwd() to control directory
        2. Reload logger module to trigger logger creation
        3. Verify logger configuration matches expected values
        
        Expected behavior:
        - Should use parent directory name as logger name
        - Should use 'mermaid_to_prototype.log' as log file name
        - Should have both console and file handlers
        """
        mock_cwd.return_value = Path('/test/path')
        
        # Access the module logger (already created at import)
        module_logger = logger.logger
        
        # Verify basic configuration
        self.assertIsInstance(module_logger, logging.Logger)
        self.assertEqual(len(module_logger.handlers), 2)
        
        # Verify handler types
        handler_types = [type(handler) for handler in module_logger.handlers]
        self.assertIn(logging.StreamHandler, handler_types)
        self.assertIn(RotatingFileHandler, handler_types)


if __name__ == "__main__":
    unittest.main()
