import os
import unittest
from unittest.mock import patch, mock_open


from tools.cli.todo_finder.main import (
    find_todos_in_file,
    walk_directory,
    append_to_todo_file,
    main
)


class TestFindTodosInFile(unittest.TestCase):
    """Test the find_todos_in_file function."""

    def test_find_python_todo_comments(self):
        """Test finding TODO comments in Python-style comments."""
        file_content = """# This is a regular comment
# TODO: Fix this bug
def some_function():
    # TODO implement this function
    pass
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.py')
            
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], (2, 'Fix this bug'))
        self.assertEqual(todos[1], (4, 'implement this function'))

    def test_find_javascript_todo_comments(self):
        """Test finding TODO comments in JavaScript-style comments."""
        file_content = """// Regular comment
// TODO: Add error handling
/* TODO: Refactor this function */
function test() {
    // TODO implement validation
}
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.js')
            
        self.assertEqual(len(todos), 3)
        self.assertEqual(todos[0], (2, 'Add error handling'))
        self.assertEqual(todos[1], (3, 'Refactor this function'))
        self.assertEqual(todos[2], (5, 'implement validation'))

    def test_find_html_todo_comments(self):
        """Test finding TODO comments in HTML-style comments."""
        file_content = """<html>
<!-- TODO: Add meta tags -->
<body>
    <!-- TODO Update styling -->
</body>
</html>
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.html')
            
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], (2, 'Add meta tags'))
        self.assertEqual(todos[1], (4, 'Update styling'))

    def test_case_insensitive_todo(self):
        """Test that TODO detection is case insensitive."""
        file_content = """# todo: lowercase
# TODO: uppercase
# Todo: mixed case
# tOdO: weird case
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.py')
            
        self.assertEqual(len(todos), 4)
        self.assertEqual(todos[0], (1, 'lowercase'))
        self.assertEqual(todos[1], (2, 'uppercase'))
        self.assertEqual(todos[2], (3, 'mixed case'))
        self.assertEqual(todos[3], (4, 'weird case'))

    def test_todo_with_colon_variations(self):
        """Test TODO comments with and without colons."""
        file_content = """# TODO: with colon
# TODO without colon
# TODO   : with spaces
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.py')
            
        self.assertEqual(len(todos), 3)
        self.assertEqual(todos[0], (1, 'with colon'))
        self.assertEqual(todos[1], (2, 'without colon'))
        self.assertEqual(todos[2], (3, 'with spaces'))

    def test_no_todos_found(self):
        """Test when no TODO comments are found."""
        file_content = """# Regular comment
def function():
    # Normal comment
    pass
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.py')
            
        self.assertEqual(len(todos), 0)

    def test_file_read_error(self):
        """Test handling of file read errors."""
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with patch('builtins.print') as mock_print:
                todos = find_todos_in_file('nonexistent.py')
                
        self.assertEqual(len(todos), 0)
        mock_print.assert_called_once()
        self.assertIn("Error reading", mock_print.call_args[0][0])

    def test_empty_file(self):
        """Test with an empty file."""
        with patch('builtins.open', mock_open(read_data="")):
            todos = find_todos_in_file('empty.py')
            
        self.assertEqual(len(todos), 0)

    def test_unicode_content(self):
        """Test with unicode content in TODO comments."""
        file_content = """# TODO: Add støtte for unicode
# TODO: Handle émojis 🚀
"""
        with patch('builtins.open', mock_open(read_data=file_content)):
            todos = find_todos_in_file('test.py')
            
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0], (1, 'Add støtte for unicode'))
        self.assertEqual(todos[1], (2, 'Handle émojis 🚀'))


class TestWalkDirectory(unittest.TestCase):
    """Test the walk_directory function."""

    def test_default_exclude_dirs(self):
        """Test that default directories are excluded."""
        mock_walk_result = [
            ('/test', ['.git', 'src', '__pycache__'], ['file1.py']),
            ('/test/src', [], ['file2.py']),
        ]
        
        with patch('os.walk', return_value=mock_walk_result):
            with patch('tools.cli.todo_finder.todo_finder.find_todos_in_file', return_value=[]):
                todos = walk_directory('/test')
                
        # Should only process src directory, not .git or __pycache__
        self.assertEqual(len(todos), 0)

    def test_custom_exclude_dirs(self):
        """Test with custom exclude directories."""
        mock_walk_result = [
            ('/test', ['build', 'src'], ['file1.py']),
            ('/test/src', [], ['file2.py']),
        ]
        
        with patch('os.walk', return_value=mock_walk_result):
            with patch('tools.cli.todo_finder.todo_finder.find_todos_in_file', return_value=[]):
                todos = walk_directory('/test', exclude_dirs={'build'})
                
        self.assertEqual(len(todos), 0)

    def test_skip_binary_files(self):
        """Test that binary files are skipped."""
        mock_walk_result = [
            ('/test', [], ['script.py', 'binary.pyc', 'lib.so', 'app.exe']),
        ]
        
        with patch('os.walk', return_value=mock_walk_result):
            with patch('tools.cli.todo_finder.todo_finder.find_todos_in_file', return_value=[(1, 'test todo')]) as mock_find:
                todos = walk_directory('/test')
                
        # Should only call find_todos_in_file once for script.py
        mock_find.assert_called_once()
        self.assertEqual(len(todos), 1)

    def test_collect_todos_from_multiple_files(self):
        """Test collecting TODOs from multiple files."""
        mock_walk_result = [
            ('/test', [], ['file1.py', 'file2.py']),
        ]
        
        def mock_find_todos(filepath):
            if 'file1.py' in filepath:
                return [(1, 'First todo'), (5, 'Second todo')]
            elif 'file2.py' in filepath:
                return [(2, 'Third todo')]
            return []
        
        with patch('os.walk', return_value=mock_walk_result):
            with patch('os.path.relpath', side_effect=lambda x, y: os.path.basename(x)):
                with patch('tools.cli.todo_finder.todo_finder.find_todos_in_file', side_effect=mock_find_todos):
                    todos = walk_directory('/test')
                    
        self.assertEqual(len(todos), 3)
        self.assertEqual(todos[0]['file'], 'file1.py')
        self.assertEqual(todos[0]['line'], 1)
        self.assertEqual(todos[0]['text'], 'First todo')
        self.assertEqual(todos[1]['file'], 'file1.py')
        self.assertEqual(todos[1]['line'], 5)
        self.assertEqual(todos[1]['text'], 'Second todo')
        self.assertEqual(todos[2]['file'], 'file2.py')
        self.assertEqual(todos[2]['line'], 2)
        self.assertEqual(todos[2]['text'], 'Third todo')

    def test_empty_directory(self):
        """Test with an empty directory."""
        mock_walk_result = [
            ('/test', [], []),
        ]
        
        with patch('os.walk', return_value=mock_walk_result):
            todos = walk_directory('/test')
            
        self.assertEqual(len(todos), 0)


class TestAppendToTodoFile(unittest.TestCase):
    """Test the append_to_todo_file function."""

    def test_append_to_new_file(self):
        """Test appending TODOs to a new file."""
        todos = [
            {'file': 'test.py', 'line': 1, 'text': 'Fix this'},
            {'file': 'main.py', 'line': 5, 'text': 'Add validation'},
        ]
        
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('builtins.print'):
                    result = append_to_todo_file(todos, 'TODO.md')
                    
        self.assertTrue(result)
        mock_file.assert_called_with('TODO.md', 'a', encoding='utf-8')
        
        # Check that content was written
        handle = mock_file()
        written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn('## New Tasks', written_content)
        self.assertIn('**test.py**', written_content)
        self.assertIn('Fix this', written_content)
        self.assertIn('**main.py**', written_content)
        self.assertIn('Add validation', written_content)

    def test_append_to_existing_file(self):
        """Test appending TODOs to an existing file."""
        existing_content = "# Existing TODO file\n\n## Old tasks\n- Old task"
        todos = [{'file': 'test.py', 'line': 1, 'text': 'New task'}]
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=existing_content)) as mock_file:
                with patch('builtins.print'):
                    result = append_to_todo_file(todos, 'TODO.md')
                    
        self.assertTrue(result)
        
        # Check that file was opened for both reading and appending
        calls = mock_file.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], ('TODO.md', 'r'))
        self.assertEqual(calls[1][0], ('TODO.md', 'a'))

    def test_append_no_todos(self):
        """Test appending when no TODOs are found."""
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('builtins.print'):
                    result = append_to_todo_file([], 'TODO.md')
                    
        self.assertTrue(result)
        
        handle = mock_file()
        written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn('No TODO comments found', written_content)

    def test_file_write_error(self):
        """Test handling of file write errors."""
        todos = [{'file': 'test.py', 'line': 1, 'text': 'Fix this'}]
        
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', side_effect=IOError("Permission denied")):
                with patch('tools.cli.todo_finder.todo_finder.logger.debug') as mock_debug:
                    result = append_to_todo_file(todos, 'TODO.md')
                    
        self.assertFalse(result)
        mock_debug.assert_called()
        error_call = [call for call in mock_debug.call_args_list if "Error writing" in str(call)]
        self.assertTrue(len(error_call) > 0)

    def test_file_read_error(self):
        """Test handling of file read errors."""
        todos = [{'file': 'test.py', 'line': 1, 'text': 'Fix this'}]
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=[IOError("Permission denied"), mock_open().return_value]):
                with patch('tools.cli.todo_finder.todo_finder.logger.debug') as mock_debug:
                    result = append_to_todo_file(todos, 'TODO.md')
                    
        self.assertTrue(result)
        mock_debug.assert_called()
        read_error_call = [call for call in mock_debug.call_args_list if "Error reading" in str(call)]
        self.assertTrue(len(read_error_call) > 0)

    def test_timestamp_included(self):
        """Test that timestamp is included in the output."""
        todos = [{'file': 'test.py', 'line': 1, 'text': 'Fix this'}]
        
        with patch('os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('builtins.print'):
                    with patch('tools.cli.todo_finder.todo_finder.datetime') as mock_datetime:
                        mock_datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"
                        result = append_to_todo_file(todos, 'TODO.md')
                        
        self.assertTrue(result)
        handle = mock_file()
        written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
        self.assertIn('2023-01-01 12:00:00', written_content)


class TestMain(unittest.TestCase):
    """Test the main function."""

    def test_main_with_valid_directory(self):
        """Test main function with valid directory."""
        test_args = ['todo_finder.py', '.', '-o', 'test.md']
        
        with patch('sys.argv', test_args):
            with patch('os.path.isdir', return_value=True):
                with patch('tools.cli.todo_finder.todo_finder.walk_directory', return_value=[]):
                    with patch('tools.cli.todo_finder.todo_finder.append_to_todo_file', return_value=True):
                        with patch('builtins.print'):
                            result = main()
                            
        self.assertEqual(result, 0)

    def test_main_with_invalid_directory(self):
        """Test main function with invalid directory."""
        test_args = ['todo_finder.py', '/nonexistent']
        
        with patch('sys.argv', test_args):
            with patch('os.path.isdir', return_value=False):
                with patch('builtins.print') as mock_print:
                    result = main()
                    
        self.assertEqual(result, 1)
        error_call = [call for call in mock_print.call_args_list if "Error:" in str(call)]
        self.assertTrue(len(error_call) > 0)

    def test_main_with_exclude_directories(self):
        """Test main function with exclude directories."""
        test_args = ['todo_finder.py', '.', '-e', 'build', 'dist']
        
        with patch('sys.argv', test_args):
            with patch('os.path.isdir', return_value=True):
                with patch('tools.cli.todo_finder.todo_finder.walk_directory') as mock_walk:
                    mock_walk.return_value = []
                    with patch('tools.cli.todo_finder.todo_finder.append_to_todo_file', return_value=True):
                        with patch('builtins.print'):
                            result = main()
                            
        self.assertEqual(result, 0)
        # Check that walk_directory was called with the correct exclude dirs
        exclude_dirs = mock_walk.call_args[0][1]
        self.assertIn('build', exclude_dirs)
        self.assertIn('dist', exclude_dirs)
        self.assertIn('.git', exclude_dirs)  # Default excludes should still be there

    def test_main_append_failure(self):
        """Test main function when appending fails."""
        test_args = ['todo_finder.py', '.']
        
        with patch('sys.argv', test_args):
            with patch('os.path.isdir', return_value=True):
                with patch('tools.cli.todo_finder.todo_finder.walk_directory', return_value=[]):
                    with patch('tools.cli.todo_finder.todo_finder.append_to_todo_file', return_value=False):
                        with patch('builtins.print'):
                            result = main()
                            
        self.assertEqual(result, 1)

    def test_main_default_output_file(self):
        """Test main function uses default output file."""
        test_args = ['todo_finder.py', '.']
        
        with patch('sys.argv', test_args):
            with patch('os.path.isdir', return_value=True):
                with patch('tools.cli.todo_finder.todo_finder.walk_directory', return_value=[]):
                    with patch('tools.cli.todo_finder.todo_finder.append_to_todo_file') as mock_append:
                        mock_append.return_value = True
                        with patch('builtins.print'):
                            result = main()
                            
        self.assertEqual(result, 0)
        # Check that default TODO.md was used
        mock_append.assert_called_once()
        self.assertEqual(mock_append.call_args[0][1], 'TODO.md')


if __name__ == "__main__":
    unittest.main()