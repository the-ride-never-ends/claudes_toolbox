# update_readme_when_settings_are_changed.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/readme/update_readme_when_settings_are_changed.py`

## Table of Contents

### Functions

- [`_format_config_json`](#_format_config_json)
- [`_update`](#_update)
- [`file_operation_error`](#file_operation_error)
- [`_load_file`](#_load_file)
- [`_create_backup`](#_create_backup)
- [`_restore_backup`](#_restore_backup)
- [`_remove_backup`](#_remove_backup)
- [`backup_markdown_file`](#backup_markdown_file)
- [`_write_file`](#_write_file)
- [`update_readme_when_settings_are_changed`](#update_readme_when_settings_are_changed)

## Functions

## `_format_config_json`

```python
def _format_config_json(pattern, new_section)
```

Format the config jsons in the new section.

## `_update`

```python
def _update(pattern, file_content, readme_content, formatting='')
```

Update the README content with the new settings.

## `file_operation_error`

```python
def file_operation_error(func=None)
```

Decorator factory to handle file operation errors.

## `_load_file`

```python
def _load_file(file_path)
```

Load the content of a file.

## `_create_backup`

```python
def _create_backup(file_path)
```

Create a backup of the file.

## `_restore_backup`

```python
def _restore_backup(file_path)
```

Restore the backup of the file.

## `_remove_backup`

```python
def _remove_backup(file_path)
```

## `backup_markdown_file`

```python
def backup_markdown_file(func)
```

Decorator to create a backup of a markdown file before writing.

## `_write_file`

```python
def _write_file(file_path, content)
```

Write the content to a file.

## `update_readme_when_settings_are_changed`

```python
def update_readme_when_settings_are_changed()
```

Update the README file with new settings if they have changed.
