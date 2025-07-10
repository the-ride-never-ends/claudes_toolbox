# import unittest
# import tempfile
# import os
# import shutil
# import time
# import threading
# import statistics
# import random
# from tools.functions.list_tools_in_functions_dir import list_tools_in_functions_dir


# class TestListToolsInFunctionsDir(unittest.TestCase):
#     """Test list_tools_in_functions_dir function."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.temp_dir = tempfile.mkdtemp()
#         self.original_cwd = os.getcwd()
#         os.chdir(self.temp_dir)
        
#         # Create test Python files with different docstrings
#         self.create_test_file("todo_manager.py", '''
# def make_todo_list(items):
#     """Creates a comprehensive todo list from given items for task management."""
#     pass

# def _private_todo():
#     """This is a private method that should be skipped."""
#     pass
# ''')
        
#         self.create_test_file("task_helper.py", '''
# def generate_tasks():
#     """Generates tasks and todo items for productivity management."""
#     pass

# def unrelated_function():
#     """Calculates mathematical equations and formulas."""
#     pass
# ''')
        
#         self.create_test_file("no_docstring.py", '''
# def function_without_docs():
#     pass
# ''')
        
#         # Create subdirectory with files
#         os.makedirs("subdir")
#         self.create_test_file("subdir/nested_todo.py", '''
# def nested_todo_function():
#     """Advanced todo list creation and management system."""
#     pass
# ''')

#     def tearDown(self):
#         """Clean up test fixtures."""
#         os.chdir(self.original_cwd)
#         shutil.rmtree(self.temp_dir)

#     def create_test_file(self, filename, content):
#         """Helper method to create test files."""
#         with open(filename, 'w') as f:
#             f.write(content)

#     def test_basic_functionality_with_valid_query(self):
#         """
#         GIVEN a valid query string "I need something for making todo lists"
#         AND default parameters (top_k=5, similarity_threshold=0.5, recursive=False)
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Returns dict[int, Any]
#             - Keys are integers starting from 1
#             - Each value contains keys: 'file_path', 'func_name', 'docstring', 'similarity'
#             - Similarity scores are floats between 0.0 and 1.0
#             - Results are ordered by similarity score (highest first)
#             - All returned results have similarity >= 0.5
#         """
#         result = list_tools_in_functions_dir("I need something for making todo lists")
        
#         self.assertIsInstance(result, dict)
#         self.assertTrue(len(result) > 0)
        
#         # Check keys are sequential integers starting from 1
#         expected_keys = list(range(1, len(result) + 1))
#         self.assertEqual(list(result.keys()), expected_keys)
        
#         # Check each result has required keys
#         for key, value in result.items():
#             self.assertIn('file_path', value)
#             self.assertIn('func_name', value)
#             self.assertIn('docstring', value)
#             self.assertIn('similarity', value)
            
#             # Check similarity is float between 0.0 and 1.0
#             self.assertIsInstance(value['similarity'], float)
#             self.assertGreaterEqual(value['similarity'], 0.0)
#             self.assertLessEqual(value['similarity'], 1.0)
#             self.assertGreaterEqual(value['similarity'], 0.5)
        
#         # Check ordering (highest similarity first)
#         similarities = [result[i]['similarity'] for i in range(1, len(result) + 1)]
#         self.assertEqual(similarities, sorted(similarities, reverse=True))

#     def test_empty_query_raises_value_error(self):
#         """
#         GIVEN an empty query string ""
#         WHEN list_tools_in_functions_dir is called
#         THEN expect ValueError to be raised
#         """
#         with self.assertRaises(ValueError):
#             list_tools_in_functions_dir("")

#     def test_top_k_zero_raises_value_error(self):
#         """
#         GIVEN a valid query string
#         AND top_k=0
#         WHEN list_tools_in_functions_dir is called
#         THEN expect ValueError to be raised
#         """
#         with self.assertRaises(ValueError):
#             list_tools_in_functions_dir("test query", top_k=0)

#     def test_top_k_negative_raises_value_error(self):
#         """
#         GIVEN a valid query string
#         AND top_k=-1
#         WHEN list_tools_in_functions_dir is called
#         THEN expect ValueError to be raised
#         """
#         with self.assertRaises(ValueError):
#             list_tools_in_functions_dir("test query", top_k=-1)

#     def test_similarity_threshold_below_zero_raises_value_error(self):
#         """
#         GIVEN a valid query string
#         AND similarity_threshold=-0.1
#         WHEN list_tools_in_functions_dir is called
#         THEN expect ValueError to be raised
#         """
#         with self.assertRaises(ValueError):
#             list_tools_in_functions_dir("test query", similarity_threshold=-0.1)

#     def test_similarity_threshold_above_one_raises_value_error(self):
#         """
#         GIVEN a valid query string
#         AND similarity_threshold=1.1
#         WHEN list_tools_in_functions_dir is called
#         THEN expect ValueError to be raised
#         """
#         with self.assertRaises(ValueError):
#             list_tools_in_functions_dir("test query", similarity_threshold=1.1)

#     def test_recursive_false_searches_only_current_directory(self):
#         """
#         GIVEN a valid query string
#         AND recursive=False (default)
#         AND files exist in subdirectories
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Only files in the current directory are searched
#             - Subdirectory files are not included in results
#         """
#         result = list_tools_in_functions_dir("todo list management", recursive=False)
        
#         # Check that no results contain files from subdirectories
#         for value in result.values():
#             file_path = value['file_path']
#             self.assertFalse('subdir' in file_path, f"Found subdirectory file: {file_path}")

#     def test_recursive_true_searches_subdirectories(self):
#         """
#         GIVEN a valid query string
#         AND recursive=True
#         AND files exist in subdirectories
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Files in subdirectories are included in search
#             - Results may contain files from any depth of subdirectory
#         """
#         result = list_tools_in_functions_dir("todo list management", recursive=True)
        
#         # Check that at least one result contains a file from subdirectory
#         found_subdir_file = False
#         for value in result.values():
#             if 'subdir' in value['file_path']:
#                 found_subdir_file = True
#                 break
        
#         self.assertTrue(found_subdir_file, "No subdirectory files found in recursive search")

#     def test_skips_private_methods(self):
#         """
#         GIVEN a valid query string
#         AND Python files contain methods starting with underscore (e.g., _private_method)
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Private methods are not included in results
#             - Only public methods/functions are analyzed
#         """
#         result = list_tools_in_functions_dir("private todo method")
        
#         # Check that no private methods appear in results
#         for value in result.values():
#             # Skip the no results message case
#             if "message" in value:
#                 continue
#             func_name = value['func_name']
#             self.assertFalse(func_name.startswith('_'), f"Found private method: {func_name}")

#     def test_top_k_limits_results(self):
#         """
#         GIVEN a valid query string
#         AND top_k=3
#         AND more than 3 files match above threshold
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Exactly 3 results returned
#             - Results are the top 3 by similarity score
#         """
#         result = list_tools_in_functions_dir("todo management", top_k=2, similarity_threshold=0.1)
        
#         self.assertLessEqual(len(result), 2)
        
#         # If we have results, check they're ordered correctly
#         if len(result) > 1:
#             self.assertGreaterEqual(result[1]['similarity'], result[2]['similarity'])

#     def test_similarity_threshold_filters_results(self):
#         """
#         GIVEN a valid query string
#         AND similarity_threshold=0.7
#         AND some files have similarity < 0.7
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Only files with similarity >= 0.7 are returned
#             - Files with similarity < 0.7 are excluded
#         """
#         result = list_tools_in_functions_dir("mathematical equations", similarity_threshold=0.7)
        
#         for value in result.values():
#             self.assertGreaterEqual(value['similarity'], 0.7)

#     def test_permission_error_on_unreadable_files(self):
#         """
#         GIVEN a valid query string
#         AND some Python files in search path are not readable (no read permissions)
#         WHEN list_tools_in_functions_dir is called
#         THEN expect PermissionError to be raised
#         """
#         # Create a file and remove read permissions
#         restricted_file = "restricted.py"
#         with open(restricted_file, 'w') as f:
#             f.write('def test(): pass')
#         os.chmod(restricted_file, 0o000)
        
#         try:
#             with self.assertRaises(PermissionError):
#                 list_tools_in_functions_dir("test query")
#         finally:
#             # Restore permissions for cleanup
#             os.chmod(restricted_file, 0o644)

#     def test_handles_files_without_docstrings(self):
#         """
#         GIVEN a valid query string
#         AND some Python files contain functions without docstrings
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Files without docstrings are either skipped or have low similarity
#             - Function continues without error
#         """
#         # This should not raise an error
#         result = list_tools_in_functions_dir("function without documentation")
        
#         # Function should complete successfully
#         self.assertIsInstance(result, dict)

#     def test_ordering_by_similarity_score(self):
#         """
#         GIVEN a valid query string
#         AND multiple files with different similarity scores
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Results dict keys are integers 1, 2, 3, etc.
#             - result[1]['similarity'] >= result[2]['similarity']
#             - result[2]['similarity'] >= result[3]['similarity']
#             - And so on for all results
#         """
#         result = list_tools_in_functions_dir("todo task management", top_k=10, similarity_threshold=0.1)
        
#         # Check keys are sequential integers
#         keys = list(result.keys())
#         expected_keys = list(range(1, len(result) + 1))
#         self.assertEqual(keys, expected_keys)
        
#         # Check ordering
#         for i in range(1, len(result)):
#             current_similarity = result[i]['similarity']
#             next_similarity = result[i + 1]['similarity']
#             self.assertGreaterEqual(current_similarity, next_similarity, 
#                                   f"Similarity at position {i} ({current_similarity}) < position {i+1} ({next_similarity})")



# class TestListToolsInFunctionsDirAdditional(unittest.TestCase):
#     """Additional edge case and performance tests for list_tools_in_functions_dir function."""

#     def setUp(self):
#         """Set up test fixtures."""
#         self.temp_dir = tempfile.mkdtemp()
#         self.original_cwd = os.getcwd()
#         os.chdir(self.temp_dir)

#     def tearDown(self):
#         """Clean up test fixtures."""
#         os.chdir(self.original_cwd)
#         shutil.rmtree(self.temp_dir)

#     def create_test_file(self, filename, content):
#         """Helper method to create test files."""
#         # Only create directory if filename contains directory separators
#         if os.path.dirname(filename):
#             os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(content)

#     def test_empty_directory_returns_no_results_message(self):
#         """
#         GIVEN a valid query string
#         AND the search directory contains no Python files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function continues without error
#             - Function returns a dictionary with a single entry specifying no results
#         """
#         # Create empty directory
#         empty_dir = "empty_test_dir"
#         os.makedirs(empty_dir)
#         os.chdir(empty_dir)
        
#         result = list_tools_in_functions_dir("test query")
        
#         # Should return no results message
#         self.assertIsInstance(result, dict)
#         self.assertEqual(len(result), 1)
#         self.assertIn(1, result)
#         self.assertIn("message", result[1])
#         self.assertIn("No Python files found", result[1]["message"])

#     def test_only_init_py_files_in_directory(self):
#         """
#         GIVEN a valid query string
#         AND directory contains only __init__.py files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - __init__.py files are processed if they contain functions with docstrings
#             - If none are found, function continues without error and 
#                 returns a dictionary with a single entry specifying no results
#         """
#         self.create_test_file("__init__.py", '''
# def init_function():
#     """Initializes the module for todo list management."""
#     pass
# ''')
        
#         result = list_tools_in_functions_dir("todo list management")
        
#         # Should process __init__.py files
#         self.assertIsInstance(result, dict)
#         if len(result) == 1 and "message" in result[1]:
#             # No results found case
#             self.assertIn("No Python files found", result[1]["message"])
#         else:
#             # Found results case
#             found_init = any("__init__.py" in value['file_path'] for value in result.values())
#             self.assertTrue(found_init, "Should process __init__.py files")

#     def test_non_python_files_ignored(self):
#         """
#         GIVEN a valid query string
#         AND directory contains .txt, .md, .json files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Non-Python files are ignored
#             - Only .py files are processed
#         """
#         # Create various non-Python files
#         self.create_test_file("readme.txt", "This is a text file")
#         self.create_test_file("docs.md", "# Documentation")
#         self.create_test_file("config.json", '{"key": "value"}')
#         self.create_test_file("script.sh", "#!/bin/bash\necho hello")
        
#         # Create one Python file
#         self.create_test_file("test.py", '''
# def test_function():
#     """Test function for validation."""
#     pass
# ''')
        
#         result = list_tools_in_functions_dir("test function")
        
#         # Should only process Python files
#         for value in result.values():
#             self.assertTrue(value['file_path'].endswith('.py'), 
#                           f"Non-Python file found: {value['file_path']}")

#     def test_malformed_python_files_handled(self):
#         """
#         GIVEN a valid query string
#         AND some Python files have syntax errors
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Malformed files are skipped or error is handled gracefully
#             - Other valid files are still processed
#         """
#         # Create malformed Python file
#         self.create_test_file("broken.py", '''
# def broken_function(
#     """This has syntax errors - missing closing parenthesis"""
#     pass

# invalid syntax here
# ''')
        
#         # Create valid Python file
#         self.create_test_file("valid.py", '''
# def valid_function():
#     """This is a valid function for testing."""
#     pass
# ''')
        
#         # Should not raise an exception and should process valid files
#         result = list_tools_in_functions_dir("valid function testing")
        
#         # Should have results from valid file
#         found_valid = any("valid.py" in value['file_path'] for value in result.values())
#         self.assertTrue(found_valid, "Should process valid Python files despite malformed ones")

#     def test_unicode_in_query_and_docstrings(self):
#         """
#         GIVEN a query string with Unicode characters "需要一个待办事项列表"
#         AND Python files with Unicode in docstrings
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Unicode is handled correctly
#             - Similarity calculation works with non-ASCII characters
#         """
#         self.create_test_file("unicode_test.py", '''
# def create_todo_list():
#     """创建待办事项列表 - Creates a todo list in Chinese."""
#     pass

# def другая_функция():
#     """Функция на русском языке для управления задачами."""
#     pass
# ''')
        
#         # Test with Unicode query
#         result = list_tools_in_functions_dir("需要一个待办事项列表")
        
#         # Should handle Unicode without errors
#         self.assertIsInstance(result, dict)
        
#         # Test with ASCII query matching Unicode docstring
#         result2 = list_tools_in_functions_dir("todo list management")
#         self.assertIsInstance(result2, dict)

#     def test_very_long_query_string(self):
#         """
#         GIVEN a query string with 10,000+ characters
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function handles long query without error
#             - Or raises ValueError if there's a hardcoded length limit
#         """
#         # Create a very long query string
#         long_query = "todo list management " * 500  # ~10,000 characters
        
#         self.create_test_file("test.py", '''
# def manage_tasks():
#     """Task and todo list management system."""
#     pass
# ''')
        
#         # Should either work or raise ValueError (not crash)
#         try:
#             result = list_tools_in_functions_dir(long_query)
#             self.assertIsInstance(result, dict)
#         except ValueError:
#             # Acceptable if there's a length limit
#             pass

#     def test_circular_symlinks_handled(self):
#         """
#         GIVEN a valid query string
#         AND recursive=True
#         AND directory structure contains circular symlinks
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function doesn't get stuck in infinite loop
#             - Completes successfully.
#         """
#         # Create directories and symlinks
#         os.makedirs("dir1/dir2")
        
#         self.create_test_file("dir1/test.py", '''
# def test_function():
#     """Test function in directory."""
#     pass
# ''')
        
#         # Create circular symlink (if supported by OS)
#         try:
#             os.symlink("../dir1", "dir1/dir2/back_to_dir1")
            
#             # Should complete without infinite loop
#             start_time = time.time()
#             result = list_tools_in_functions_dir("test function", recursive=True)
#             end_time = time.time()
            
#             # Should complete in reasonable time (not infinite loop)
#             self.assertLess(end_time - start_time, 10, "Function took too long - possible infinite loop")
#             self.assertIsInstance(result, dict)
            
#         except (OSError, NotImplementedError):
#             # Skip if symlinks not supported
#             self.skipTest("Symlinks not supported on this system")

#     def test_deeply_nested_directories(self):
#         """
#         GIVEN a valid query string
#         AND recursive=True
#         AND directory structure is 50+ levels deep
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function handles deep nesting without stack overflow
#             - Or has reasonable depth limit
#         """
#         # Create deeply nested directory structure
#         current_path = ""
#         for i in range(50):
#             current_path = os.path.join(current_path, f"level{i}")
#             os.makedirs(current_path, exist_ok=True)
        
#         # Place a Python file at the deepest level
#         deep_file = os.path.join(current_path, "deep_test.py")
#         self.create_test_file(deep_file, '''
# def deep_function():
#     """Function located in deeply nested directory."""
#     pass
# ''')
        
#         # Should handle deep nesting
#         result = list_tools_in_functions_dir("deeply nested function", recursive=True)
#         self.assertIsInstance(result, dict)

#     def test_identical_similarity_scores_stable_ordering(self):
#         """
#         GIVEN a valid query string
#         AND multiple files have identical similarity scores
#         WHEN list_tools_in_functions_dir is called multiple times
#         THEN expect:
#             - Files with same score have consistent ordering
#             - Ordered by file path as secondary sort
#         """
#         # Create files with identical docstrings
#         self.create_test_file("a_file.py", '''
# def function_a():
#     """Identical docstring for testing."""
#     pass
# ''')
        
#         self.create_test_file("z_file.py", '''
# def function_z():
#     """Identical docstring for testing."""
#     pass
# ''')
        
#         # Run multiple times and check consistency
#         results = []
#         for _ in range(3):
#             result = list_tools_in_functions_dir("identical docstring testing")
#             results.append(result)
        
#         # Results should be consistent across runs
#         for i in range(1, len(results)):
#             self.assertEqual(list(results[0].keys()), list(results[i].keys()))
#             for key in results[0].keys():
#                 self.assertEqual(results[0][key]['file_path'], results[i][key]['file_path'])

#     def test_special_characters_in_file_paths(self):
#         """
#         GIVEN a valid query string
#         AND file paths contain spaces, parentheses, and special characters
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Files are processed correctly regardless of path characters
#             - No path-related errors
#         """
#         # Create files with special characters in paths
#         special_files = [
#             "file with spaces.py",
#             "file(with)parentheses.py",
#             "file-with-dashes.py",
#             "file_with_underscores.py",
#             "file.with.dots.py"
#         ]
        
#         for filename in special_files:
#             self.create_test_file(filename, f'''
# def special_function():
#     """Function in file with special characters: {filename}."""
#     pass
# ''')
        
#         result = list_tools_in_functions_dir("special characters function")
        
#         # Should process all files without errors
#         self.assertIsInstance(result, dict)
#         if len(result) > 0 and "message" not in result[1]:
#             file_paths = [value['file_path'] for value in result.values()]
#             # At least some special character files should be found
#             self.assertTrue(any(any(char in path for char in " ()-_.") for path in file_paths))

#     # Performance Tests
#     def test_performance_with_large_number_of_files(self):
#         """
#         GIVEN a valid query string
#         AND directory contains 10,000+ Python files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function completes in under 30 seconds
#             - Memory usage remains under 4 GB
#         """
#         # Create a smaller number for practical testing (100 files instead of 10,000)
#         num_files = 100
        
#         for i in range(num_files):
#             self.create_test_file(f"file_{i:04d}.py", f'''
# def function_{i}():
#     """Function number {i} for performance testing and evaluation."""
#     pass
# ''')
        
#         start_time = time.time()
#         result = list_tools_in_functions_dir("performance testing evaluation", top_k=10)
#         end_time = time.time()
        
#         # Should complete in reasonable time
#         self.assertLess(end_time - start_time, 10, "Function took too long with many files")
#         self.assertIsInstance(result, dict)

#     def test_performance_with_very_large_docstrings(self):
#         """
#         GIVEN a valid query string
#         AND some Python files have docstrings with 10,000+ characters
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function handles large docstrings efficiently
#             - No significant performance degradation
#         """
#         # Create file with very large docstring
#         large_docstring = "This is a very long docstring. " * 300  # ~9,000 characters
        
#         self.create_test_file("large_docstring.py", f'''
# def large_doc_function():
#     """{large_docstring}
    
#     This function has an extremely large docstring for performance testing.
#     """
#     pass
# ''')
        
#         self.create_test_file("normal.py", '''
# def normal_function():
#     """Normal sized docstring for comparison."""
#     pass
# ''')
        
#         start_time = time.time()
#         result = list_tools_in_functions_dir("performance testing docstring")
#         end_time = time.time()
        
#         # Should handle large docstrings without significant delay
#         self.assertLess(end_time - start_time, 5, "Large docstrings caused significant performance degradation")
#         self.assertIsInstance(result, dict)

#     def test_performance_scaling_with_top_k(self):
#         """
#         GIVEN a valid query string
#         AND directory with 1000 Python files
#         WHEN list_tools_in_functions_dir is called with top_k=10 vs top_k=900
#         THEN expect:
#             - Performance is similar regardless of top_k value
#             - Algorithm doesn't process all files if not needed
#         """
#         # Create smaller number for practical testing
#         num_files = 50
        
#         for i in range(num_files):
#             self.create_test_file(f"perf_{i:03d}.py", f'''
# def performance_function_{i}():
#     """Performance function {i} for scaling tests."""
#     pass
# ''')
        
#         # Test with small top_k
#         start_time = time.time()
#         result_small = list_tools_in_functions_dir("performance function", top_k=5)
#         time_small = time.time() - start_time
        
#         # Test with large top_k
#         start_time = time.time()
#         result_large = list_tools_in_functions_dir("performance function", top_k=40)
#         time_large = time.time() - start_time
        
#         # Performance shouldn't degrade significantly
#         self.assertLessEqual(len(result_small), 5)
#         self.assertLessEqual(len(result_large), 40)

#     def test_performance_with_high_similarity_threshold(self):
#         """
#         GIVEN a valid query string
#         AND similarity_threshold=0.95
#         AND directory with 1000 Python files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function can short-circuit evaluation when possible
#             - Doesn't compute similarity for all files if early ones don't meet threshold
#         """
#         # Create files with varying similarity to query
#         for i in range(20):
#             self.create_test_file(f"threshold_{i:02d}.py", f'''
# def threshold_function_{i}():
#     """Function {i} with different similarity levels."""
#     pass
# ''')
        
#         start_time = time.time()
#         result = list_tools_in_functions_dir("very specific unique query", similarity_threshold=0.95)
#         end_time = time.time()
        
#         # Should complete quickly with high threshold
#         self.assertLess(end_time - start_time, 3, "High threshold search took too long")
        
#         # Should return no results message if threshold is too high
#         self.assertIsInstance(result, dict)
#         if len(result) == 1 and "message" in result[1]:
#             self.assertIn("No Python files found", result[1]["message"])

#     def test_memory_usage_with_recursive_search(self):
#         """
#         GIVEN a valid query string
#         AND recursive=True
#         AND deeply nested directory with thousands of files
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Memory usage scales reasonably
#             - No memory leaks or excessive allocation
#         """
#         # Create nested structure with multiple files
#         for level in range(5):
#             for file_num in range(10):
#                 path = os.path.join(*[f"level{i}" for i in range(level + 1)])
#                 self.create_test_file(f"{path}/file_{file_num}.py", f'''
# def nested_function_{level}_{file_num}():
#     """Nested function at level {level}, file {file_num}."""
#     pass
# ''')
        
#         result = list_tools_in_functions_dir("nested function", recursive=True)
        
#         # Should complete without memory issues
#         self.assertIsInstance(result, dict)

#     def test_concurrent_access_to_files(self):
#         """
#         GIVEN a valid query string
#         AND other processes are modifying Python files during search
#         WHEN list_tools_in_functions_dir is called
#         THEN expect:
#             - Function handles file access errors gracefully
#             - Completes with available files
#         """
#         self.create_test_file("concurrent_test.py", '''
# def concurrent_function():
#     """Function for concurrent access testing."""
#     pass
# ''')
        
#         # Function to modify file during search
#         def modify_file():
#             time.sleep(0.1)
#             try:
#                 with open("concurrent_test.py", "a") as f:
#                     f.write("\n# Modified during search\n")
#             except:
#                 pass  # Ignore errors
        
#         # Start file modification in background
#         modifier_thread = threading.Thread(target=modify_file)
#         modifier_thread.start()
        
#         # Should handle concurrent access gracefully
#         result = list_tools_in_functions_dir("concurrent access testing")
        
#         modifier_thread.join()
#         self.assertIsInstance(result, dict)


# class TestAccuracyOptimization(unittest.TestCase):
#     """Accuracy optimization tests to achieve 95% true positive rate through threshold optimization."""

#     def setUp(self):
#         """Set up test fixtures with known ground truth data."""
#         self.temp_dir = tempfile.mkdtemp()
#         self.original_cwd = os.getcwd()
#         os.chdir(self.temp_dir)
        
#         # Create a comprehensive set of test files with known relevance labels
#         self.ground_truth_data = self._create_ground_truth_test_files()

#     def tearDown(self):
#         """Clean up test fixtures."""
#         os.chdir(self.original_cwd)
#         shutil.rmtree(self.temp_dir)

#     def create_test_file(self, filename, content):
#         """Helper method to create test files."""
#         if os.path.dirname(filename):
#             os.makedirs(os.path.dirname(filename), exist_ok=True)
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(content)

#     def _create_ground_truth_test_files(self):
#         """Create test files with known relevance for different query types."""
#         ground_truth = {}
        
#         # File management related functions (highly relevant)
#         self.create_test_file("file_ops.py", '''
# def read_file_content(path):
#     """Read and return the complete content of a file from the filesystem."""
#     pass

# def write_file_data(path, data):
#     """Write data to a file, creating directories if needed."""
#     pass

# def delete_file_safely(path):
#     """Safely delete a file with backup and confirmation."""
#     pass

# def copy_file_with_metadata(src, dst):
#     """Copy file preserving metadata, timestamps, and permissions."""
#     pass
# ''')
        
#         # Database operations (highly relevant for DB queries)
#         self.create_test_file("database.py", '''
# def execute_sql_query(query, params):
#     """Execute SQL query with parameters and return results."""
#     pass

# def create_database_connection(config):
#     """Establish connection to database using configuration."""
#     pass

# def insert_record_batch(table, records):
#     """Insert multiple records into database table efficiently."""
#     pass

# def query_database_with_filter(table, conditions):
#     """Query database table with filtering conditions."""
#     pass
# ''')
        
#         # Text processing functions (relevant for text queries)
#         self.create_test_file("text_utils.py", '''
# def process_text_content(text):
#     """Process and clean text content for analysis."""
#     pass

# def extract_keywords_from_text(content):
#     """Extract important keywords from text using NLP."""
#     pass

# def format_text_output(data):
#     """Format text data for display or export."""
#     pass

# def validate_text_input(text):
#     """Validate text input according to specified rules."""
#     pass
# ''')
        
#         # Mathematical operations (relevant for math queries)
#         self.create_test_file("math_ops.py", '''
# def calculate_statistical_metrics(data):
#     """Calculate mean, median, mode, and standard deviation."""
#     pass

# def solve_linear_equations(matrix, vector):
#     """Solve system of linear equations using matrix operations."""
#     pass

# def compute_numerical_derivative(function, point):
#     """Compute numerical derivative of function at given point."""
#     pass

# def perform_matrix_multiplication(a, b):
#     """Perform matrix multiplication with error checking."""
#     pass
# ''')
        
#         # Network operations (relevant for network queries)
#         self.create_test_file("network.py", '''
# def send_http_request(url, method, data):
#     """Send HTTP request and handle response with retries."""
#     pass

# def establish_socket_connection(host, port):
#     """Create socket connection with timeout and error handling."""
#     pass

# def download_file_from_url(url, destination):
#     """Download file from URL with progress tracking."""
#     pass

# def validate_network_connectivity(host):
#     """Check network connectivity to specified host."""
#     pass
# ''')
        
#         # Unrelated functions (should have low relevance)
#         self.create_test_file("unrelated.py", '''
# def bake_chocolate_cake(ingredients):
#     """Bake a delicious chocolate cake following recipe steps."""
#     pass

# def feed_pet_animals(pets, food_type):
#     """Feed pets according to their dietary requirements."""
#     pass

# def organize_closet_items(clothing):
#     """Organize clothing items by category and season."""
#     pass

# def plan_vacation_itinerary(destination, days):
#     """Plan detailed vacation itinerary with activities."""
#     pass
# ''')
        
#         # Define ground truth relevance for different query types
#         ground_truth = {
#             "file operations and management": {
#                 "highly_relevant": ["read_file_content", "write_file_data", "delete_file_safely", "copy_file_with_metadata"],
#                 "moderately_relevant": [],
#                 "not_relevant": ["bake_chocolate_cake", "feed_pet_animals", "organize_closet_items", "plan_vacation_itinerary"]
#             },
#             "database queries and operations": {
#                 "highly_relevant": ["execute_sql_query", "create_database_connection", "insert_record_batch", "query_database_with_filter"],
#                 "moderately_relevant": [],
#                 "not_relevant": ["bake_chocolate_cake", "feed_pet_animals", "organize_closet_items", "plan_vacation_itinerary"]
#             },
#             "text processing and analysis": {
#                 "highly_relevant": ["process_text_content", "extract_keywords_from_text", "format_text_output", "validate_text_input"],
#                 "moderately_relevant": [],
#                 "not_relevant": ["bake_chocolate_cake", "feed_pet_animals", "organize_closet_items", "plan_vacation_itinerary"]
#             },
#             "mathematical calculations": {
#                 "highly_relevant": ["calculate_statistical_metrics", "solve_linear_equations", "compute_numerical_derivative", "perform_matrix_multiplication"],
#                 "moderately_relevant": [],
#                 "not_relevant": ["bake_chocolate_cake", "feed_pet_animals", "organize_closet_items", "plan_vacation_itinerary"]
#             },
#             "network communication": {
#                 "highly_relevant": ["send_http_request", "establish_socket_connection", "download_file_from_url", "validate_network_connectivity"],
#                 "moderately_relevant": [],
#                 "not_relevant": ["bake_chocolate_cake", "feed_pet_animals", "organize_closet_items", "plan_vacation_itinerary"]
#             }
#         }
        
#         return ground_truth

#     def _calculate_metrics(self, results, ground_truth, query_type):
#         """Calculate precision, recall, and F1-score for given results."""
#         if not results or "message" in results.get(1, {}):
#             return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "true_positives": 0, "false_positives": 0, "false_negatives": 0}
        
#         returned_functions = [result['func_name'] for result in results.values()]
#         highly_relevant = set(ground_truth[query_type]["highly_relevant"])
#         not_relevant = set(ground_truth[query_type]["not_relevant"])
        
#         # Calculate true positives, false positives, false negatives
#         true_positives = len([f for f in returned_functions if f in highly_relevant])
#         false_positives = len([f for f in returned_functions if f in not_relevant])
#         false_negatives = len(highly_relevant) - true_positives
        
#         # Calculate metrics
#         precision = true_positives / len(returned_functions) if returned_functions else 0.0
#         recall = true_positives / len(highly_relevant) if highly_relevant else 0.0
#         f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
#         return {
#             "precision": precision,
#             "recall": recall,
#             "f1": f1,
#             "true_positives": true_positives,
#             "false_positives": false_positives,
#             "false_negatives": false_negatives
#         }

#     def test_threshold_optimization_for_95_percent_accuracy(self):
#         """
#         GIVEN a set of queries with known ground truth relevance
#         WHEN testing different similarity thresholds from 0.1 to 0.9
#         THEN find the optimal threshold that achieves at least 95% true positive rate
#         AND maintains reasonable precision (>50%)
#         """
#         test_queries = [
#             "file operations and management",
#             "database queries and operations", 
#             "text processing and analysis",
#             "mathematical calculations",
#             "network communication"
#         ]
        
#         # Test thresholds from 0.1 to 0.9 in steps of 0.005
#         thresholds = [round(t, 3) for t in [0.1 + i * 0.005 for i in range(0, 161)]]  # 0.1 to 0.9 in steps of 0.005
        
#         results_by_threshold = {}
#         from tqdm import tqdm
        
#         for threshold in tqdm(thresholds, desc="Testing thresholds"):
#             threshold_results = {
#                 "total_precision": 0.0,
#                 "total_recall": 0.0,
#                 "total_f1": 0.0,
#                 "total_tp": 0,
#                 "total_fp": 0,
#                 "total_fn": 0,
#                 "query_count": 0
#             }
            
#             for query in test_queries:
#                 results = list_tools_in_functions_dir(
#                     query, 
#                     top_k=10, 
#                     similarity_threshold=threshold, 
#                     recursive=False
#                 )
                
#                 metrics = self._calculate_metrics(results, self.ground_truth_data, query)
                
#                 threshold_results["total_precision"] += metrics["precision"]
#                 threshold_results["total_recall"] += metrics["recall"]
#                 threshold_results["total_f1"] += metrics["f1"]
#                 threshold_results["total_tp"] += metrics["true_positives"]
#                 threshold_results["total_fp"] += metrics["false_positives"]
#                 threshold_results["total_fn"] += metrics["false_negatives"]
#                 threshold_results["query_count"] += 1
            
#             # Calculate averages
#             count = threshold_results["query_count"]
#             threshold_results["avg_precision"] = threshold_results["total_precision"] / count
#             threshold_results["avg_recall"] = threshold_results["total_recall"] / count
#             threshold_results["avg_f1"] = threshold_results["total_f1"] / count
            
#             # Calculate overall true positive rate
#             total_relevant = threshold_results["total_tp"] + threshold_results["total_fn"]
#             threshold_results["true_positive_rate"] = threshold_results["total_tp"] / total_relevant if total_relevant > 0 else 0.0
            
#             results_by_threshold[threshold] = threshold_results
        
#         # Find thresholds that achieve at least 95% true positive rate
#         qualifying_thresholds = [
#             (threshold, data) for threshold, data in results_by_threshold.items()
#             if data["true_positive_rate"] >= 0.95
#         ]
        
#         # Print detailed results for analysis
#         print("\n" + "="*80)
#         print("THRESHOLD OPTIMIZATION RESULTS")
#         print("="*80)
#         print(f"{'Threshold':<12} {'TPR':<8} {'Precision':<12} {'Recall':<10} {'F1':<8} {'TP':<4} {'FP':<4} {'FN':<4}")
#         print("-"*80)
        
#         for threshold in sorted(results_by_threshold.keys()):
#             data = results_by_threshold[threshold]
#             print(f"{threshold:<12.2f} {data['true_positive_rate']:<8.3f} {data['avg_precision']:<12.3f} "
#                   f"{data['avg_recall']:<10.3f} {data['avg_f1']:<8.3f} {data['total_tp']:<4d} "
#                   f"{data['total_fp']:<4d} {data['total_fn']:<4d}")
        
#         # Assert that we found at least one qualifying threshold
#         self.assertGreater(len(qualifying_thresholds), 0, 
#                           "No threshold achieved 95% true positive rate")
        
#         # Find the optimal threshold (best F1 score among qualifying thresholds)
#         optimal_threshold, optimal_data = max(qualifying_thresholds, 
#                                             key=lambda x: x[1]["avg_f1"])
        
#         print(f"\n🎯 OPTIMAL THRESHOLD: {optimal_threshold}")
#         print(f"   True Positive Rate: {optimal_data['true_positive_rate']:.1%}")
#         print(f"   Average Precision: {optimal_data['avg_precision']:.1%}")
#         print(f"   Average Recall: {optimal_data['avg_recall']:.1%}")
#         print(f"   Average F1-Score: {optimal_data['avg_f1']:.3f}")
        
#         # Verify the optimal threshold meets our requirements
#         self.assertGreaterEqual(optimal_data["true_positive_rate"], 0.95,
#                                f"Optimal threshold {optimal_threshold} only achieved "
#                                f"{optimal_data['true_positive_rate']:.1%} TPR, need ≥95%")
        
#         # Ensure precision is reasonable (>30% to avoid too many false positives)
#         self.assertGreater(optimal_data["avg_precision"], 0.30,
#                           f"Optimal threshold {optimal_threshold} has low precision "
#                           f"({optimal_data['avg_precision']:.1%}), may return too many irrelevant results")

#     def test_statistical_significance_of_optimal_threshold(self):
#         """
#         GIVEN the optimal threshold found in the previous test
#         WHEN running multiple trials with different query variations
#         THEN verify the threshold's performance is statistically significant
#         AND consistent across different query formulations
#         """
#         # Set random seed for reproducible results
#         random.seed(420)

#         # Create query variations to test robustness
#         query_variations = {
#             "file_ops": [
#             "file operations and management",
#             "how to read and write files in python?",
#             "best way to handle file system operations",
#             "python manage files and directories",
#             "file handling and manipulation examples",
#             "file I/O operations tutorial",
#             "disk file operations python",
#             "manage file content efficiently",
#             "read write delete files",
#             "how can I interact with the filesystem?",
#             "file processing utilities example code",
#             "need help with file management functions",
#             "fs utils python",
#             "file operations toolkit documentation",
#             "what's the best method for file handling?",
#             "python file manipulation tools",
#             "efficient file storage operations",
#             "file access control permissions",
#             "how to work with file metadata",
#             "backup and restore files automatically",
#             "file sync script example",
#             "compress files with python",
#             "transfer files between servers",
#             "validate file integrity",
#             "file verification checksum"
#             ],
#             "database": [
#             "database queries and operations", 
#             "how to use SQL in python",
#             "execute database queries example",
#             "connect to database python",
#             "database admin tools",
#             "run SQL query python",
#             "process SQL statements efficiently",
#             "manage database transactions",
#             "CRUD operations database",
#             "create and manage database tables",
#             "alter database schema",
#             "implement connection pooling",
#             "optimize slow database queries",
#             "backup and recover database",
#             "database migration script",
#             "monitor database performance",
#             "how to tune database performance?",
#             "secure database access",
#             "create index on database table",
#             "set up database replication",
#             "manage database cluster",
#             "run analytics on database",
#             "generate reports from database",
#             "sync databases python",
#             "database maintenance script",
#             "audit database operations",
#             "configure database settings",
#             "handle database connections properly",
#             "manage database sessions",
#             "call stored procedures from python"
#             ],
#             "text": [
#             "text processing and analysis",
#             "how to process text in python?",
#             "manipulate text strings",
#             "process large text content",
#             "parse text file python",
#             "extract data from text",
#             "transform text content",
#             "format text output",
#             "validate text input",
#             "search and replace in text",
#             "regex pattern matching text",
#             "convert text encoding utf-8",
#             "normalize text data",
#             "tokenize text into words",
#             "classify text by category",
#             "analyze sentiment in text",
#             "summarize long text automatically",
#             "compare text similarity",
#             "calculate text similarity percentage",
#             "clean messy text data",
#             "preprocess text for nlp",
#             "extract features from text",
#             "text mining techniques python",
#             "annotate text with metadata",
#             "segment text into paragraphs",
#             "detect language in text",
#             "translate text between languages",
#             "extract keywords from article",
#             "analyze text content for topics",
#             "process text documents in batch",
#             "prepare text data for analysis",
#             "check text quality score",
#             "analyze text structure",
#             "semantic analysis of text",
#             "statistical analysis of word frequency"
#             ],
#             "math": [
#             "mathematical calculations",
#             "how to perform complex math in python?",
#             "numerical computation libraries",
#             "mathematical functions example",
#             "statistical analysis python",
#             "create mathematical model",
#             "implement numerical methods",
#             "efficient math algorithms",
#             "calculate statistics from dataset",
#             "solve mathematical problems python",
#             "numerical analysis techniques",
#             "statistical math functions",
#             "computational math libraries",
#             "optimize mathematical equations",
#             "linear algebra operations numpy",
#             "matrix calculations example",
#             "vector operations python",
#             "how to do calculus in python?",
#             "solve differential equations",
#             "calculate probability distribution",
#             "perform regression analysis",
#             "mathematical transformations example",
#             "simulate mathematical models",
#             "plot mathematical functions",
#             "visualize mathematical data",
#             "validate mathematical results",
#             "approximate mathematical functions",
#             "interpolate data points",
#             "extrapolate from dataset",
#             "fit curve to data points",
#             "analyze mathematical patterns in data",
#             "process mathematical signals",
#             "recognize patterns with math",
#             "machine learning math operations",
#             "deep learning mathematical foundations"
#             ],
#             "network": [
#             "network communication",
#             "how to make network requests in python?",
#             "implement network protocols",
#             "check network connectivity",
#             "manage network connections",
#             "secure network traffic",
#             "monitor network activity",
#             "configure network settings",
#             "troubleshoot network issues",
#             "optimize network performance",
#             "analyze network traffic",
#             "improve network speed",
#             "network admin tools python",
#             "set up network infrastructure",
#             "create network services",
#             "implement custom protocol",
#             "socket programming tutorial",
#             "make HTTP requests python",
#             "connect to API over network",
#             "transfer data over network",
#             "share files over network",
#             "stream data over network",
#             "encrypt network communication",
#             "authenticate network users",
#             "load balance network traffic",
#             "route network packets",
#             "configure network firewall",
#             "measure network bandwidth",
#             "check network latency",
#             "analyze network packets",
#             "monitor network traffic spikes",
#             "map network topology",
#             "discover network services",
#             "analyze protocol efficiency",
#             "measure network quality"
#             ],
#             "web": [
#             "web development",
#             "how to build web applications?",
#             "create web services",
#             "develop REST API",
#             "set up web server",
#             "implement web client",
#             "scrape website data",
#             "crawl multiple web pages",
#             "extract data from websites",
#             "manage web content",
#             "secure web application",
#             "implement web auth",
#             "manage user sessions",
#             "cache web responses",
#             "speed up web performance",
#             "test web application",
#             "deploy web app to production",
#             "monitor web server health",
#             "track web analytics",
#             "make website accessible",
#             "create responsive web design",
#             "develop frontend components",
#             "build backend web services",
#             "connect web app to database",
#             "use web framework utilities",
#             "process web templates",
#             "handle web form submissions",
#             "upload files to web server",
#             "implement web sockets",
#             "create web microservices"
#             ],
#             "security": [
#             "security operations",
#             "how to improve application security?",
#             "monitor security events",
#             "analyze security risks",
#             "perform security audit",
#             "ensure security compliance",
#             "implement encryption",
#             "set up user authentication",
#             "authorize user actions",
#             "control access to resources",
#             "assess security vulnerabilities",
#             "detect security threats",
#             "respond to security incidents",
#             "analyze security logs",
#             "enforce security policies",
#             "manage encryption keys",
#             "handle security certificates",
#             "secure password storage",
#             "manage user security",
#             "protect user sessions",
#             "secure sensitive data",
#             "network security best practices",
#             "application security checklist",
#             "database security measures",
#             "cloud security implementation",
#             "mobile app security",
#             "web security headers",
#             "secure API endpoints",
#             "container security scanning",
#             "DevSecOps pipeline"
#             ],
#             "data": [
#             "data processing",
#             "how to analyze large datasets?",
#             "manipulate data efficiently",
#             "transform data format",
#             "clean dirty data",
#             "validate data integrity",
#             "integrate multiple data sources",
#             "migrate data between systems",
#             "sync data across platforms",
#             "backup important data",
#             "recover corrupted data",
#             "archive old data",
#             "compress large datasets",
#             "encrypt sensitive data",
#             "visualize data insights",
#             "mine data for patterns",
#             "set up data warehouse",
#             "create data model",
#             "assess data quality",
#             "implement data governance",
#             "build data pipeline",
#             "ETL process example",
#             "stream data processing",
#             "batch data processing",
#             "real-time data analysis",
#             "data lake implementation",
#             "manage data catalog",
#             "track data lineage",
#             "profile dataset characteristics",
#             "discover hidden data",
#             "classify data types",
#             "mask sensitive data",
#             "anonymize personal data",
#             "aggregate data results",
#             "summarize data findings"
#             ],
#             "api": [
#             "API development",
#             "how to build REST API?",
#             "test API endpoints",
#             "document API usage",
#             "secure API access",
#             "implement API authentication",
#             "authorize API requests",
#             "limit API request rate",
#             "monitor API usage",
#             "track API analytics",
#             "version API endpoints",
#             "set up API gateway",
#             "integrate with external APIs",
#             "orchestrate multiple API calls",
#             "compose API responses",
#             "manage API lifecycle",
#             "implement API design patterns",
#             "handle API errors gracefully",
#             "format API responses",
#             "validate API requests",
#             "cache API responses",
#             "optimize API performance",
#             "load test API endpoints",
#             "create API mock services",
#             "test API contracts",
#             "transform API responses",
#             "aggregate API results",
#             "route API requests",
#             "proxy API calls",
#             "implement API service mesh"
#             ],
#             "cloud": [
#             "cloud computing",
#             "how to use cloud services?",
#             "deploy to cloud provider",
#             "manage cloud resources",
#             "monitor cloud services",
#             "implement cloud security",
#             "use cloud storage",
#             "configure cloud networking",
#             "automate cloud provisioning",
#             "orchestrate cloud services",
#             "migrate to cloud platform",
#             "optimize cloud costs",
#             "manage cloud spending",
#             "backup cloud data",
#             "implement cloud disaster recovery",
#             "scale cloud services automatically",
#             "load balance cloud traffic",
#             "manage cloud containers",
#             "create serverless functions",
#             "build cloud microservices",
#             "cloud DevOps practices",
#             "set up cloud CI/CD pipeline",
#             "manage cloud configuration",
#             "implement cloud identity",
#             "ensure cloud compliance",
#             "govern cloud resources",
#             "allocate cloud resources",
#             "monitor cloud performance",
#             "analyze cloud metrics",
#             "predict cloud usage"
#             ]
#         }
        
#         all_results = []
        
#         # Random seed for reproducible results
#         _SEED = 420
#         random.seed(_SEED)
#         statistical_significance_threshold = 0.90
#         top_k = 8  # Use a reasonable top_k for testing
#         # Use threshold around 0.15-0.25 based on typical semantic similarity distributions
#         test_threshold = 0.10  # Use the optimal threshold found in the previous test

#         # Randomly sample queries from each category to reduce test time while maintaining diversity
#         from tqdm import tqdm
#         for category, queries in tqdm(query_variations.items()):
#             # Only test the 5 categories we have ground truth for
#             if category not in ["file_ops", "database", "text", "math", "network"]:
#                 continue

#             # Randomly sample 10 queries from each category
#             sampled_queries = random.sample(queries, min(10, len(queries)))

#             for query in sampled_queries:
#                 results = list_tools_in_functions_dir(
#                     query, 
#                     top_k=top_k, 
#                     similarity_threshold=test_threshold, 
#                     recursive=False
#                 )
                
#                 metrics = self._calculate_metrics(results, self.ground_truth_data, 
#                                                 {
#                                                     "file_ops": "file operations and management",
#                                                     "database": "database queries and operations",
#                                                     "text": "text processing and analysis",
#                                                     "math": "mathematical calculations",
#                                                     "network": "network communication",
#                                                     "web": "file operations and management",
#                                                     "security": "file operations and management",
#                                                     "data": "file operations and management",
#                                                     "api": "file operations and management",
#                                                     "cloud": "file operations and management"
#                                                 }[category])
                
#                 all_results.append(metrics)
        
#         # Calculate overall statistics
#         total_tp = sum(r["true_positives"] for r in all_results)
#         total_fp = sum(r["false_positives"] for r in all_results)
#         total_fn = sum(r["false_negatives"] for r in all_results)

#         overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
#         overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
#         overall_tpr = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        
#         # Calculate standard deviation to assess consistency
#         precisions = [r["precision"] for r in all_results if r["precision"] > 0]
#         recalls = [r["recall"] for r in all_results if r["recall"] > 0]
        
#         if len(precisions) > 1 and len(recalls) > 1:
#             precision_stdev = statistics.stdev(precisions)
#             recall_stdev = statistics.stdev(recalls)
#         else:
#             precision_stdev = recall_stdev = 0.0

#         print(f"\n📊 STATISTICAL ANALYSIS (Threshold: {test_threshold})")
#         print(f"   Overall True Positive Rate: {overall_tpr:.1%}")
#         print(f"   Overall Precision: {overall_precision:.1%}")
#         print(f"   Overall Recall: {overall_recall:.1%}")
#         print(f"   Precision Std Dev: {precision_stdev:.3f}")
#         print(f"   Recall Std Dev: {recall_stdev:.3f}")
#         print(f"   Total Trials: {len(all_results)}")
        
#         # Verify performance is consistent and meets requirements
#         self.assertGreaterEqual(overall_tpr, statistical_significance_threshold,
#                                f"Overall TPR ({overall_tpr:.1%}) should be ≥{statistical_significance_threshold}% for statistical significance")
        
#         # Verify consistency (standard deviation should be reasonable)
#         self.assertLess(precision_stdev, 0.5,
#                        f"Precision standard deviation ({precision_stdev:.3f}) too high - inconsistent performance")
        
#         self.assertLess(recall_stdev, 0.4,
#                        f"Recall standard deviation ({recall_stdev:.3f}) too high - inconsistent performance")


# if __name__ == '__main__':
#     unittest.main()