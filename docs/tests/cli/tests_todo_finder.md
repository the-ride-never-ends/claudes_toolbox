# tests_todo_finder.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tests/cli/tests_todo_finder.py`

## Table of Contents

### Classes

- [`TestFindTodosInFile`](#testfindtodosinfile)
- [`TestWalkDirectory`](#testwalkdirectory)
- [`TestAppendToTodoFile`](#testappendtotodofile)
- [`TestMain`](#testmain)

## Classes

## `TestFindTodosInFile`

```python
class TestFindTodosInFile(unittest.TestCase)
```

Test the find_todos_in_file function.

**Methods:**

- [`test_case_insensitive_todo`](#test_case_insensitive_todo)
- [`test_empty_file`](#test_empty_file)
- [`test_file_read_error`](#test_file_read_error)
- [`test_find_html_todo_comments`](#test_find_html_todo_comments)
- [`test_find_javascript_todo_comments`](#test_find_javascript_todo_comments)
- [`test_find_python_todo_comments`](#test_find_python_todo_comments)
- [`test_no_todos_found`](#test_no_todos_found)
- [`test_todo_with_colon_variations`](#test_todo_with_colon_variations)
- [`test_unicode_content`](#test_unicode_content)

### `test_case_insensitive_todo`

```python
def test_case_insensitive_todo(self)
```

Test that TODO detection is case insensitive.

### `test_empty_file`

```python
def test_empty_file(self)
```

Test with an empty file.

### `test_file_read_error`

```python
def test_file_read_error(self)
```

Test handling of file read errors.

### `test_find_html_todo_comments`

```python
def test_find_html_todo_comments(self)
```

Test finding TODO comments in HTML-style comments.

### `test_find_javascript_todo_comments`

```python
def test_find_javascript_todo_comments(self)
```

Test finding TODO comments in JavaScript-style comments.

### `test_find_python_todo_comments`

```python
def test_find_python_todo_comments(self)
```

Test finding TODO comments in Python-style comments.

### `test_no_todos_found`

```python
def test_no_todos_found(self)
```

Test when no TODO comments are found.

### `test_todo_with_colon_variations`

```python
def test_todo_with_colon_variations(self)
```

Test TODO comments with and without colons.

### `test_unicode_content`

```python
def test_unicode_content(self)
```

Test with unicode content in TODO comments.

## `TestWalkDirectory`

```python
class TestWalkDirectory(unittest.TestCase)
```

Test the walk_directory function.

**Methods:**

- [`test_collect_todos_from_multiple_files`](#test_collect_todos_from_multiple_files)
- [`test_custom_exclude_dirs`](#test_custom_exclude_dirs)
- [`test_default_exclude_dirs`](#test_default_exclude_dirs)
- [`test_empty_directory`](#test_empty_directory)
- [`test_skip_binary_files`](#test_skip_binary_files)

### `test_collect_todos_from_multiple_files`

```python
def test_collect_todos_from_multiple_files(self)
```

Test collecting TODOs from multiple files.

### `test_custom_exclude_dirs`

```python
def test_custom_exclude_dirs(self)
```

Test with custom exclude directories.

### `test_default_exclude_dirs`

```python
def test_default_exclude_dirs(self)
```

Test that default directories are excluded.

### `test_empty_directory`

```python
def test_empty_directory(self)
```

Test with an empty directory.

### `test_skip_binary_files`

```python
def test_skip_binary_files(self)
```

Test that binary files are skipped.

## `TestAppendToTodoFile`

```python
class TestAppendToTodoFile(unittest.TestCase)
```

Test the append_to_todo_file function.

**Methods:**

- [`test_append_no_todos`](#test_append_no_todos)
- [`test_append_to_existing_file`](#test_append_to_existing_file)
- [`test_append_to_new_file`](#test_append_to_new_file)
- [`test_file_read_error`](#test_file_read_error)
- [`test_file_write_error`](#test_file_write_error)
- [`test_timestamp_included`](#test_timestamp_included)

### `test_append_no_todos`

```python
def test_append_no_todos(self)
```

Test appending when no TODOs are found.

### `test_append_to_existing_file`

```python
def test_append_to_existing_file(self)
```

Test appending TODOs to an existing file.

### `test_append_to_new_file`

```python
def test_append_to_new_file(self)
```

Test appending TODOs to a new file.

### `test_file_read_error`

```python
def test_file_read_error(self)
```

Test handling of file read errors.

### `test_file_write_error`

```python
def test_file_write_error(self)
```

Test handling of file write errors.

### `test_timestamp_included`

```python
def test_timestamp_included(self)
```

Test that timestamp is included in the output.

## `TestMain`

```python
class TestMain(unittest.TestCase)
```

Test the main function.

**Methods:**

- [`test_main_append_failure`](#test_main_append_failure)
- [`test_main_default_output_file`](#test_main_default_output_file)
- [`test_main_with_exclude_directories`](#test_main_with_exclude_directories)
- [`test_main_with_invalid_directory`](#test_main_with_invalid_directory)
- [`test_main_with_valid_directory`](#test_main_with_valid_directory)

### `test_main_append_failure`

```python
def test_main_append_failure(self)
```

Test main function when appending fails.

### `test_main_default_output_file`

```python
def test_main_default_output_file(self)
```

Test main function uses default output file.

### `test_main_with_exclude_directories`

```python
def test_main_with_exclude_directories(self)
```

Test main function with exclude directories.

### `test_main_with_invalid_directory`

```python
def test_main_with_invalid_directory(self)
```

Test main function with invalid directory.

### `test_main_with_valid_directory`

```python
def test_main_with_valid_directory(self)
```

Test main function with valid directory.
