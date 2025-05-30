# configs.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/configs.py`

## Module Description

Server configuration settings.

## Table of Contents

### Classes

- [`Configs`](#configs)

## Classes

## `Configs`

```python
class Configs(object)
```

Configuration settings for the MCP server.

**Methods:**

- [`LLM_API_KEY`](#llm_api_key) (property)
- [`OPERATING_SYSTEM`](#operating_system) (property)
- [`PROJECT_NAME`](#project_name) (property)
- [`REQUIREMENTS_FILE_PATHS`](#requirements_file_paths)
- [`ROOT_DIR`](#root_dir) (property)
- [`VERSION`](#version) (property)

**Special Methods:**

- [`__getitem__`](#__getitem__)
- [`__setitem__`](#__setitem__)

### `LLM_API_KEY`

```python
def LLM_API_KEY(self)
```

The API key for the LLM service.

### `OPERATING_SYSTEM`

```python
def OPERATING_SYSTEM(self)
```

The operating system of the server.

### `PROJECT_NAME`

```python
def PROJECT_NAME(self)
```

The name of the project.

### `REQUIREMENTS_FILE_PATHS`

```python
def REQUIREMENTS_FILE_PATHS(self)
```

List of paths for requirements.txt files.

### `ROOT_DIR`

```python
def ROOT_DIR(self)
```

The root directory of the project.

### `VERSION`

```python
def VERSION(self)
```

The current version of the program.

### `__getitem__`

```python
def __getitem__(self, key)
```

Get the value of a configuration setting by its key.

### `__setitem__`

```python
def __setitem__(self, key, value)
```

Set the value of a configuration setting by its key.
