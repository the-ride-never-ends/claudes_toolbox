# json_to_pydantic_mk1.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tests/to_be_tested/json_to_pydantic_mk1.py`

## Table of Contents

### Functions

- [`_to_snake_case`](#_to_snake_case)
- [`_structure_signature`](#_structure_signature)
- [`_sanitize_field_name`](#_sanitize_field_name)
- [`_build_model`](#_build_model)
- [`_infer_type`](#_infer_type)
- [`json_to_pydantic`](#json_to_pydantic)

## Functions

## `_to_snake_case`

```python
def _to_snake_case(name)
```

Convert camelCase or PascalCase to snake_case

## `_structure_signature`

```python
def _structure_signature(data)
```

Create a hashable structure signature for deduplication

## `_sanitize_field_name`

```python
def _sanitize_field_name(name)
```

Sanitize field names to be valid Python identifiers

## `_build_model`

```python
def _build_model(data, class_name, model_registry, structure_map, allow_optional_fields=False)
```

Builds a Pydantic model definition dynamically based on the provided data structure.

**Parameters:**

- `data (dict[str, Any])` (`Any`): The input dictionary representing the structure of the data.

- `class_name (str)` (`Any`): The name of the Pydantic model class to be generated.

- `model_registry (dict)` (`Any`): A registry to store generated model definitions by class name.

- `structure_map (dict)` (`Any`): A mapping of structure signatures to class names to avoid duplication.

- `allow_optional_fields (bool, optional)` (`Any`): Whether to allow fields with `None` values to be marked as optional. Defaults to False.

**Returns:**

- `str`: The generated Pydantic model definition as a string.

## `_infer_type`

```python
def _infer_type(value, model_registry, structure_map, parent_key, allow_optional_fields)
```

Infers the Pydantic-compatible type of a given value and updates the model registry
and structure map if necessary.

**Parameters:**

- `value (Any)` (`Any`): The value whose type needs to be inferred. Can be a dict, list, or primitive type.

- `model_registry (dict)` (`Any`): A dictionary to store dynamically generated Pydantic models.

- `structure_map (dict)` (`Any`): A mapping of parent keys to their corresponding data structures.

- `parent_key (str)` (`Any`): The key associated with the current value, used for naming generated models.

- `allow_optional_fields (bool)` (`Any`): Whether to allow fields to be optional in the generated models.

**Returns:**

- `str`: A string representing the inferred type, compatible with Pydantic type annotations.

## `json_to_pydantic`

```python
def json_to_pydantic(json_data, output_dir, model_name='GeneratedModel', allow_optional_fields=False)
```

Turn JSON data into a Pydantic model or series of models.
Any nested structures will be converted into their own models and placed as fields their parent models.
NOTE: Only POSIX-style paths are supported at this time.

**Parameters:**

- `json_data (str | dict)` (`Any`): JSON data as a JSON string, JSON dictionary, or path to a JSON file.

- `output_dir (str)` (`Any`): Directory to save the generated model file.

- `model_name (str)` (`Any`): Name of the generated model class. Defaults to "GeneratedModel".

- `allow_optional_fields (bool)` (`Any`): If True, allows models fields to be optional. Defaults to False.

**Returns:**

- `str`: A success message that contains the path to the output file.

**Raises:**

- `FileNotFoundError`: If the output directory does not exist.
TypeError: If the input JSON is not a string, dictionary, or path to a JSON file.
ValueError:
- If the input JSON is invalid.
- If there is any error during model generation.
- If importing the generated model fails.
- If generated model fails to validate against the input JSON.
IOError: If there is an error writing to the output file.
