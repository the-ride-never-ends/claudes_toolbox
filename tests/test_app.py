# import unittest
# from unittest.mock import patch, MagicMock, call
# import sys
# import os
# from pathlib import Path

# # Add parent directory to path to import app modules
# sys.path.insert(0, str(Path(__file__).parent.parent))

# # Import modules to test
# from server import (
#     PATHS_DICT,
#     get_cli_tools_from_files,
#     get_function_tools_from_files,
#     test_generator, 
#     documentation_generator, 
#     lint_a_python_codebase,
#     run_tests_and_save_their_results, 
#     codebase_search
# )

# class TestMCPServerApp(unittest.TestCase):
#     """Test cases for the MCP server application."""

#     # TODO Rewrite these tests for get_cli_tools_from_files and get_function_tools_from_files
#     # @patch('subprocess.run')
#     # @patch('app.logger')
#     # def test_run_cli_tool_success(self, mock_logger, mock_subprocess_run):
#     #     """Test _run_cli_tool function with successful command execution."""
#     #     # Setup mock
#     #     mock_process = MagicMock()
#     #     mock_process.returncode = 0
#     #     mock_process.stdout = "Command output"
#     #     mock_subprocess_run.return_value = mock_process

#     #     # Call function
#     #     result = _run_cli_tool(["test", "command"], "Test Function")

#     #     # Verify
#     #     mock_subprocess_run.assert_called_once_with(
#     #         ["bash", "-c", "source venv/bin/activate && test command"],
#     #         capture_output=True,
#     #         text=True
#     #     )
        
#     #     self.assertEqual(result, "Command output")
#     #     mock_logger.info.assert_called()

#     # @patch('subprocess.run')
#     # @patch('app.logger')
#     # def test_run_cli_tool_failure(self, mock_logger, mock_subprocess_run):
#     #     """Test _run_cli_tool function with failed command execution."""
#     #     # Setup mock
#     #     mock_process = MagicMock()
#     #     mock_process.returncode = 1
#     #     mock_process.stderr = "Command failed"
#     #     mock_subprocess_run.return_value = mock_process

#     #     # Call function and verify exception
#     #     with self.assertRaises(Exception) as context:
#     #         _run_cli_tool(["test", "command"], "Test Function")
        
#     #     self.assertIn("Test generator failed", str(context.exception))
#     #     mock_logger.info.assert_called_once()

#     @patch('server.PATHS_DICT')
#     def setUp(self, mock_paths_dict):
#         """Set up test environment with mocked paths."""
#         self.mock_paths_dict = mock_paths_dict
#         self.mock_paths_dict.__getitem__.side_effect = lambda key: {
#             "this_file": Path("/mock/path/claudes_toolbox/server.py"),
#             "this_dir": Path("/mock/path/claudes_toolbox"),
#             "project_dir": Path("/mock/path"),
#             "venv_dir": Path("/mock/path/claudes_toolbox/.venv"),
#             "server_dir": Path("/mock/path/claudes_toolbox"),
#             "tools_dir": Path("/mock/path/claudes_toolbox/tools"),
#         }[key]
#         self.mock_paths_dict.get.side_effect = self.mock_paths_dict.__getitem__.side_effect

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_test_generator(self, mock_run_cli_tool, paths_dict):
#         """Test test_generator function with default parameters."""
#         # Call function
#         test_generator(
#             name="Test Name",
#             description="Test Description",
#             test_parameter_json="test.json"
#         )

#         # Verify
#         expected_cmd = [
#             "python", "-m", "test_generator",
#             "--name", "Test Name",
#             "--description", "Test Description",
#             "--test_parameter_json", "test.json",
#             "--output_dir", "tests",
#             "--harness", "unittest"
#         ]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Test Generator"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_test_generator_all_params(self, mock_run_cli_tool, paths_dict):
#         """Test test_generator function with all parameters specified."""
#         # Call function
#         test_generator(
#             name="Test Name",
#             description="Test Description",
#             test_parameter_json="custom.json",
#             output_dir="custom_tests",
#             harness="pytest"
#         )

#         # Verify
#         expected_cmd = [
#             "python", "-m", "test_generator",
#             "--name", "Test Name",
#             "--description", "Test Description",
#             "--test_parameter_json", "custom.json",
#             "--output_dir", "custom_tests",
#             "--harness", "pytest"
#         ]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Test Generator"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_documentation_generator_defaults(self, mock_run_cli_tool, paths_dict):
#         """Test documentation_generator function with default parameters."""
#         # Call function
#         documentation_generator(input_path="src")

#         # Verify
#         expected_cmd = [
#             "python", "documentation_generator.py",
#             "--input", "src",
#             "--output", "docs",
#             "--docstring-style", "google",
#             "--inheritance"
#         ]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Documentation Generator"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_documentation_generator_all_params(self, mock_run_cli_tool, paths_dict):
#         """Test documentation_generator function with all parameters specified."""
#         # Call function
#         documentation_generator(
#             input_path="src",
#             output_path="custom_docs",
#             docstring_style="numpy",
#             ignore=["venv", "tests"],
#             inheritance=False
#         )

#         # Verify
#         expected_cmd = [
#             "python", "documentation_generator.py",
#             "--input", "src",
#             "--output", "custom_docs",
#             "--docstring-style", "numpy",
#             "--ignore", "venv", "tests"
#         ]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Documentation Generator"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_lint_a_python_codebase_defaults(self, mock_run_cli_tool, paths_dict):
#         """Test lint_a_python_codebase function with default parameters."""
#         # Call function
#         lint_a_python_codebase()

#         # Verify
#         expected_cmd = ["python", "main.py", "."]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Lint Python Codebase"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_lint_a_python_codebase_all_params(self, mock_run_cli_tool, paths_dict):
#         """Test lint_a_python_codebase function with all parameters specified."""
#         # Call function
#         lint_a_python_codebase(
#             path="src",
#             patterns=["*.py", "*.pyx"],
#             exclude=[".venv", "build"],
#             no_blank=True,
#             no_trailing=True,
#             no_newlines=True,
#             dry_run=True,
#             verbose=True
#         )

#         # Verify command contains expected flags
#         mock_run_cli_tool.assert_called_once()
#         cmd_arg = mock_run_cli_tool.call_args[0][0]
        
#         self.assertEqual(cmd_arg[0:3], ["python", "main.py", "src"])
#         self.assertIn("--patterns", cmd_arg)
#         self.assertIn("--exclude", cmd_arg)
#         self.assertIn("--no-blank", cmd_arg)
#         self.assertIn("--no-trailing", cmd_arg)
#         self.assertIn("--no-newlines", cmd_arg)
#         self.assertIn("--dry-run", cmd_arg)
#         self.assertIn("--verbose", cmd_arg)

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_run_tests_and_save_their_results_defaults(self, mock_run_cli_tool, paths_dict):
#         """Test run_tests_and_save_their_results function with default parameters."""
#         # Call function
#         run_tests_and_save_their_results()

#         # Verify
#         expected_cmd = ["./run_tests.sh", "--path", "."]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Run Tests and Save Results"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_run_tests_and_save_their_results_all_params(self, mock_run_cli_tool, paths_dict):
#         """Test run_tests_and_save_their_results function with all parameters specified."""
#         # Call function
#         run_tests_and_save_their_results(
#             path="src",
#             check_all=True,
#             mypy=True,
#             flake8=True,
#             lint_only=True,
#             respect_gitignore=True
#         )

#         # Verify
#         expected_cmd = [
#             "./run_tests.sh",
#             "--path", "src",
#             "--check-all",
#             "--mypy",
#             "--flake8",
#             "--lint-only",
#             "--respect-gitignore"
#         ]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Run Tests and Save Results"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_codebase_search_defaults(self, mock_run_cli_tool, paths_dict):
#         """Test codebase_search function with default parameters."""
#         # Call function
#         codebase_search(pattern="def main")

#         # Verify
#         expected_cmd = ["python", "-m", "codebase_search", "def main", "."]
#         mock_run_cli_tool.assert_called_once_with(
#             expected_cmd, "Codebase Search"
#         )

#     @patch('server.PATHS_DICT')
#     @patch('utils.run_tool')
#     def test_codebase_search_all_params(self, mock_run_cli_tool, paths_dict):
#         """Test codebase_search function with all parameters specified."""
#         # Call function
#         codebase_search(
#             pattern="function",
#             path="src",
#             case_insensitive=True,
#             whole_word=True,
#             regex=True,
#             extensions="py,js",
#             exclude="*.git*,*node_modules*",
#             max_depth=3,
#             context=2,
#             format="json",
#             output="results.json",
#             compact=True,
#             group_by_file=True,
#             summary=True
#         )

#         # Verify command contains expected flags and arguments
#         mock_run_cli_tool.assert_called_once()
#         cmd_arg = mock_run_cli_tool.call_args[0][0]
        
#         # Check required args
#         self.assertEqual(cmd_arg[0:5], ["python", "-m", "codebase_search", "function", "src"])
        
#         # Check all flags are present
#         flags = ["--case-insensitive", "--whole-word", "--regex", 
#                  "--extensions", "py,js", "--exclude", "*.git*,*node_modules*",
#                  "--max-depth", "3", "--context", "2", "--format", "json",
#                  "--output", "results.json", "--compact", "--group-by-file", 
#                  "--summary"]
                 
#         for flag in flags:
#             self.assertIn(flag, cmd_arg)


# if __name__ == '__main__':
#     unittest.main()
