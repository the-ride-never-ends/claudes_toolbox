# test_update_readme_when_settings_are_changed.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tests/utils_/readme/test_update_readme_when_settings_are_changed.py`

## Table of Contents

### Classes

- [`TestFormatConfigJson`](#testformatconfigjson)
- [`TestUpdate`](#testupdate)
- [`TestFileOperationErrorDecorator`](#testfileoperationerrordecorator)
- [`TestLoadFile`](#testloadfile)
- [`TestBackupOperations`](#testbackupoperations)
- [`TestBackupMarkdownFileDecorator`](#testbackupmarkdownfiledecorator)
- [`TestWriteFile`](#testwritefile)
- [`TestUpdateReadmeWhenSettingsAreChanged`](#testupdatereadmewhensettingsarechanged)

## Classes

## `TestFormatConfigJson`

```python
class TestFormatConfigJson(unittest.TestCase)
```

Test _format_config_json function.

**Methods:**

- [`test_format_config_json_with_matching_pattern`](#test_format_config_json_with_matching_pattern)
- [`test_format_config_json_without_matching_pattern`](#test_format_config_json_without_matching_pattern)

### `test_format_config_json_with_matching_pattern`

```python
def test_format_config_json_with_matching_pattern(self)
```

### `test_format_config_json_without_matching_pattern`

```python
def test_format_config_json_without_matching_pattern(self)
```

## `TestUpdate`

```python
class TestUpdate(unittest.TestCase)
```

Test _update function.

**Methods:**

- [`test_update_with_identical_content`](#test_update_with_identical_content)
- [`test_update_with_matching_pattern`](#test_update_with_matching_pattern)
- [`test_update_with_matching_pattern_and_formatting`](#test_update_with_matching_pattern_and_formatting)
- [`test_update_with_no_matching_pattern`](#test_update_with_no_matching_pattern)

### `test_update_with_identical_content`

```python
def test_update_with_identical_content(self)
```

### `test_update_with_matching_pattern`

```python
def test_update_with_matching_pattern(self)
```

### `test_update_with_matching_pattern_and_formatting`

```python
def test_update_with_matching_pattern_and_formatting(self)
```

### `test_update_with_no_matching_pattern`

```python
def test_update_with_no_matching_pattern(self)
```

## `TestFileOperationErrorDecorator`

```python
class TestFileOperationErrorDecorator(unittest.TestCase)
```

Test file_operation_error decorator.

**Methods:**

- [`setUp`](#setup)
- [`test_function_error_with_default_return`](#test_function_error_with_default_return)
- [`test_function_error_with_no_return`](#test_function_error_with_no_return)
- [`test_function_error_with_raise`](#test_function_error_with_raise)
- [`test_function_success`](#test_function_success)

### `setUp`

```python
def setUp(self)
```

### `test_function_error_with_default_return`

```python
def test_function_error_with_default_return(self)
```

### `test_function_error_with_no_return`

```python
def test_function_error_with_no_return(self)
```

### `test_function_error_with_raise`

```python
def test_function_error_with_raise(self)
```

### `test_function_success`

```python
def test_function_success(self)
```

## `TestLoadFile`

```python
class TestLoadFile(unittest.TestCase)
```

Test _load_file function.

**Methods:**

- [`setUp`](#setup)
- [`test_load_file_not_found`](#test_load_file_not_found)
- [`test_load_file_success`](#test_load_file_success)

### `setUp`

```python
def setUp(self)
```

### `test_load_file_not_found`

```python
def test_load_file_not_found(self, mock_file)
```

### `test_load_file_success`

```python
def test_load_file_success(self, mock_file)
```

## `TestBackupOperations`

```python
class TestBackupOperations(unittest.TestCase)
```

Test backup-related functions (_create_backup, _restore_backup, _remove_backup).

**Methods:**

- [`setUp`](#setup)
- [`test_create_backup`](#test_create_backup)
- [`test_create_backup_error`](#test_create_backup_error)
- [`test_remove_backup`](#test_remove_backup)
- [`test_restore_backup`](#test_restore_backup)

### `setUp`

```python
def setUp(self)
```

### `test_create_backup`

```python
def test_create_backup(self, mock_copy)
```

### `test_create_backup_error`

```python
def test_create_backup_error(self, mock_copy)
```

### `test_remove_backup`

```python
def test_remove_backup(self, mock_unlink)
```

### `test_restore_backup`

```python
def test_restore_backup(self, mock_move)
```

## `TestBackupMarkdownFileDecorator`

```python
class TestBackupMarkdownFileDecorator(unittest.TestCase)
```

Test backup_markdown_file decorator.

**Methods:**

- [`setUp`](#setup)
- [`tearDown`](#teardown)
- [`test_backup_markdown_file_error`](#test_backup_markdown_file_error)
- [`test_backup_markdown_file_success`](#test_backup_markdown_file_success)

### `setUp`

```python
def setUp(self)
```

### `tearDown`

```python
def tearDown(self)
```

### `test_backup_markdown_file_error`

```python
def test_backup_markdown_file_error(self)
```

### `test_backup_markdown_file_success`

```python
def test_backup_markdown_file_success(self)
```

## `TestWriteFile`

```python
class TestWriteFile(unittest.TestCase)
```

Test _write_file function.

**Methods:**

- [`setUp`](#setup)
- [`tearDown`](#teardown)
- [`test_write_file_error`](#test_write_file_error)
- [`test_write_file_success`](#test_write_file_success)

### `setUp`

```python
def setUp(self)
```

### `tearDown`

```python
def tearDown(self)
```

### `test_write_file_error`

```python
def test_write_file_error(self, mock_file)
```

### `test_write_file_success`

```python
def test_write_file_success(self, mock_file)
```

## `TestUpdateReadmeWhenSettingsAreChanged`

```python
class TestUpdateReadmeWhenSettingsAreChanged(unittest.TestCase)
```

Test update_readme_when_settings_are_changed function.

**Methods:**

- [`setUp`](#setup)
- [`tearDown`](#teardown)
- [`test_update_readme_disabled_in_config`](#test_update_readme_disabled_in_config)
- [`test_update_readme_no_readme_file`](#test_update_readme_no_readme_file)
- [`test_update_readme_success`](#test_update_readme_success)
- [`test_update_readme_with_empty_files`](#test_update_readme_with_empty_files)
- [`test_update_readme_with_missing_files`](#test_update_readme_with_missing_files)

### `setUp`

```python
def setUp(self)
```

### `tearDown`

```python
def tearDown(self)
```

### `test_update_readme_disabled_in_config`

```python
def test_update_readme_disabled_in_config(self)
```

### `test_update_readme_no_readme_file`

```python
def test_update_readme_no_readme_file(self)
```

### `test_update_readme_success`

```python
def test_update_readme_success(self)
```

### `test_update_readme_with_empty_files`

```python
def test_update_readme_with_empty_files(self)
```

### `test_update_readme_with_missing_files`

```python
def test_update_readme_with_missing_files(self)
```
