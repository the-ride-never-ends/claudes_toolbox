# test_json_to_pydantic.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/tests/functions/test_json_to_pydantic.py`

## Table of Contents

### Classes

- [`TestToSnakeCase`](#testtosnakecase)
- [`TestStructureSignature`](#teststructuresignature)
- [`TestSanitizeFieldName`](#testsanitizefieldname)
- [`TestBuildModel`](#testbuildmodel)
- [`TestInferTypeDictionaryLogic`](#testinfertypedictionarylogic)
- [`TestInferTypeListLogic`](#testinfertypelistlogic)
- [`TestInferType`](#testinfertype)
- [`TestTopologicalSort`](#testtopologicalsort)
- [`TestJsonToPydantic`](#testjsontopydantic)
- [`TestJsonToPydanticIntegration`](#testjsontopydanticintegration)

## Classes

## `TestToSnakeCase`

```python
class TestToSnakeCase(unittest.TestCase)
```

Test the _to_snake_case function

**Methods:**

- [`test_already_snake_case`](#test_already_snake_case)
- [`test_camel_case_conversion`](#test_camel_case_conversion)
- [`test_mixed_case`](#test_mixed_case)
- [`test_pascal_case_conversion`](#test_pascal_case_conversion)
- [`test_with_numbers`](#test_with_numbers)

### `test_already_snake_case`

```python
def test_already_snake_case(self)
```

Test that snake_case remains unchanged

### `test_camel_case_conversion`

```python
def test_camel_case_conversion(self)
```

Test that camelCase is converted to snake_case correctly

### `test_mixed_case`

```python
def test_mixed_case(self)
```

Test that mixed cases are converted correctly

### `test_pascal_case_conversion`

```python
def test_pascal_case_conversion(self)
```

Test that PascalCase is converted to snake_case correctly

### `test_with_numbers`

```python
def test_with_numbers(self)
```

Test conversion with numbers

## `TestStructureSignature`

```python
class TestStructureSignature(unittest.TestCase)
```

Test the _structure_signature function

**Methods:**

- [`test_empty_dict`](#test_empty_dict)
- [`test_nested_dict`](#test_nested_dict)
- [`test_simple_dict`](#test_simple_dict)
- [`test_with_different_types`](#test_with_different_types)

### `test_empty_dict`

```python
def test_empty_dict(self)
```

Test with an empty dictionary

### `test_nested_dict`

```python
def test_nested_dict(self)
```

Test with a nested dictionary

### `test_simple_dict`

```python
def test_simple_dict(self)
```

Test with a simple dictionary

### `test_with_different_types`

```python
def test_with_different_types(self)
```

Test with different types of values

## `TestSanitizeFieldName`

```python
class TestSanitizeFieldName(unittest.TestCase)
```

Test the _sanitize_field_name function

**Methods:**

- [`test_complex_cases`](#test_complex_cases)
- [`test_convert_spaces_and_special_chars`](#test_convert_spaces_and_special_chars)
- [`test_keywords`](#test_keywords)
- [`test_leading_underscore`](#test_leading_underscore)
- [`test_numeric_start`](#test_numeric_start)
- [`test_simple_name`](#test_simple_name)

### `test_complex_cases`

```python
def test_complex_cases(self)
```

Test combination of problematic cases

### `test_convert_spaces_and_special_chars`

```python
def test_convert_spaces_and_special_chars(self)
```

Test conversion of spaces and special characters

### `test_keywords`

```python
def test_keywords(self)
```

Test handling of Python keywords

### `test_leading_underscore`

```python
def test_leading_underscore(self)
```

Test handling of names with leading underscores

### `test_numeric_start`

```python
def test_numeric_start(self)
```

Test handling of names starting with numbers

### `test_simple_name`

```python
def test_simple_name(self)
```

Test with a simple valid name

## `TestBuildModel`

```python
class TestBuildModel(unittest.TestCase)
```

Test the _build_model function

**Methods:**

- [`setUp`](#setup)
- [`test_empty_dict`](#test_empty_dict)
- [`test_nested_dict`](#test_nested_dict)
- [`test_simple_dict`](#test_simple_dict)
- [`test_with_list`](#test_with_list)
- [`test_with_none_values`](#test_with_none_values)
- [`test_with_optional_fields`](#test_with_optional_fields)
- [`test_with_sanitized_names`](#test_with_sanitized_names)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `test_empty_dict`

```python
def test_empty_dict(self)
```

Test with an empty dictionary

### `test_nested_dict`

```python
def test_nested_dict(self)
```

Test with a nested dictionary

### `test_simple_dict`

```python
def test_simple_dict(self)
```

Test with a simple dictionary

### `test_with_list`

```python
def test_with_list(self)
```

Test with a list field

### `test_with_none_values`

```python
def test_with_none_values(self)
```

Test with None values in the data

### `test_with_optional_fields`

```python
def test_with_optional_fields(self)
```

Test with allow_optional_fields=True

### `test_with_sanitized_names`

```python
def test_with_sanitized_names(self)
```

Test with field names that need sanitization

## `TestInferTypeDictionaryLogic`

```python
class TestInferTypeDictionaryLogic(unittest.TestCase)
```

Test the _infer_type_dictionary_logic function

**Methods:**

- [`setUp`](#setup)
- [`test_nested_dictionary`](#test_nested_dictionary)
- [`test_none_or_empty_dict`](#test_none_or_empty_dict)
- [`test_numeric_keys`](#test_numeric_keys)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `test_nested_dictionary`

```python
def test_nested_dictionary(self)
```

Test with nested dictionary

### `test_none_or_empty_dict`

```python
def test_none_or_empty_dict(self)
```

Test with None or empty dictionary

### `test_numeric_keys`

```python
def test_numeric_keys(self)
```

Test with dictionary having numeric string keys

## `TestInferTypeListLogic`

```python
class TestInferTypeListLogic(unittest.TestCase)
```

Test the _infer_type_list_logic function

**Methods:**

- [`setUp`](#setup)
- [`test_heterogeneous_list`](#test_heterogeneous_list)
- [`test_homogeneous_list`](#test_homogeneous_list)
- [`test_list_of_dicts`](#test_list_of_dicts)
- [`test_none_or_empty_list`](#test_none_or_empty_list)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `test_heterogeneous_list`

```python
def test_heterogeneous_list(self)
```

Test with heterogeneous list types

### `test_homogeneous_list`

```python
def test_homogeneous_list(self)
```

Test with homogeneous list types

### `test_list_of_dicts`

```python
def test_list_of_dicts(self)
```

Test with list of dictionaries

### `test_none_or_empty_list`

```python
def test_none_or_empty_list(self)
```

Test with None or empty list

## `TestInferType`

```python
class TestInferType(unittest.TestCase)
```

Test the _infer_type function

**Methods:**

- [`setUp`](#setup)
- [`test_none_type`](#test_none_type)
- [`test_primitive_types`](#test_primitive_types)
- [`test_unknown_type`](#test_unknown_type)
- [`test_with_dict`](#test_with_dict)
- [`test_with_list`](#test_with_list)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `test_none_type`

```python
def test_none_type(self)
```

Test with None value

### `test_primitive_types`

```python
def test_primitive_types(self)
```

Test with primitive types

### `test_unknown_type`

```python
def test_unknown_type(self)
```

Test with an unsupported type

### `test_with_dict`

```python
def test_with_dict(self)
```

Test with dictionary value

### `test_with_list`

```python
def test_with_list(self)
```

Test with list value

## `TestTopologicalSort`

```python
class TestTopologicalSort(unittest.TestCase)
```

Test the _topological_sort function

**Methods:**

- [`test_complex_dependencies`](#test_complex_dependencies)
- [`test_cyclic_dependencies`](#test_cyclic_dependencies)
- [`test_empty_graph`](#test_empty_graph)
- [`test_linear_dependencies`](#test_linear_dependencies)
- [`test_no_dependencies`](#test_no_dependencies)

### `test_complex_dependencies`

```python
def test_complex_dependencies(self)
```

Test with more complex dependencies

### `test_cyclic_dependencies`

```python
def test_cyclic_dependencies(self)
```

Test with cyclic dependencies A -> B -> C -> A

### `test_empty_graph`

```python
def test_empty_graph(self)
```

Test with an empty dependency graph

### `test_linear_dependencies`

```python
def test_linear_dependencies(self)
```

Test with linear dependencies A -> B -> C

### `test_no_dependencies`

```python
def test_no_dependencies(self)
```

Test with a graph having no dependencies

## `TestJsonToPydantic`

```python
class TestJsonToPydantic(unittest.TestCase)
```

Test the json_to_pydantic function

**Methods:**

- [`setUp`](#setup)
- [`tearDown`](#teardown)
- [`test_error_in_build_model`](#test_error_in_build_model)
- [`test_error_writing_to_file`](#test_error_writing_to_file)
- [`test_invalid_json_data_type`](#test_invalid_json_data_type)
- [`test_invalid_output_dir`](#test_invalid_output_dir)
- [`test_with_dict_data`](#test_with_dict_data)
- [`test_with_json_file_path`](#test_with_json_file_path)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `tearDown`

```python
def tearDown(self)
```

Clean up test fixtures

### `test_error_in_build_model`

```python
def test_error_in_build_model(self, mock_build_model)
```

Test handling error in _build_model

### `test_error_writing_to_file`

```python
def test_error_writing_to_file(self, mock_topo_sort, mock_build_model, mock_open)
```

Test handling error when writing to file

### `test_invalid_json_data_type`

```python
def test_invalid_json_data_type(self)
```

Test with invalid JSON data type

### `test_invalid_output_dir`

```python
def test_invalid_output_dir(self)
```

Test with an invalid output directory

### `test_with_dict_data`

```python
def test_with_dict_data(self, mock_topo_sort, mock_build_model)
```

Test with dictionary data

### `test_with_json_file_path`

```python
def test_with_json_file_path(self, mock_topo_sort, mock_build_model, mock_is_file)
```

Test with JSON file path

## `TestJsonToPydanticIntegration`

```python
class TestJsonToPydanticIntegration(unittest.TestCase)
```

Integration tests using the real sample.json file

**Methods:**

- [`setUp`](#setup)
- [`tearDown`](#teardown)
- [`test_field_name_sanitization`](#test_field_name_sanitization)
- [`test_generated_model_structure`](#test_generated_model_structure)
- [`test_imports_are_strings_not_complex_objects`](#test_imports_are_strings_not_complex_objects)
- [`test_list_fields_are_properly_typed`](#test_list_fields_are_properly_typed)
- [`test_model_can_be_imported_and_used`](#test_model_can_be_imported_and_used)
- [`test_nested_objects_create_separate_models`](#test_nested_objects_create_separate_models)
- [`test_sample_json_basic_functionality`](#test_sample_json_basic_functionality)
- [`test_with_optional_fields_enabled`](#test_with_optional_fields_enabled)

### `setUp`

```python
def setUp(self)
```

Set up test fixtures

### `tearDown`

```python
def tearDown(self)
```

Clean up test fixtures

### `test_field_name_sanitization`

```python
def test_field_name_sanitization(self)
```

Test that field names are properly sanitized

### `test_generated_model_structure`

```python
def test_generated_model_structure(self)
```

Test that the generated model has the correct structure

### `test_imports_are_strings_not_complex_objects`

```python
def test_imports_are_strings_not_complex_objects(self)
```

Test that simple string arrays like 'imports' are handled correctly

### `test_list_fields_are_properly_typed`

```python
def test_list_fields_are_properly_typed(self)
```

Test that list fields in the JSON are properly detected as List types

### `test_model_can_be_imported_and_used`

```python
def test_model_can_be_imported_and_used(self)
```

Test that the generated model can actually be imported and instantiated

### `test_nested_objects_create_separate_models`

```python
def test_nested_objects_create_separate_models(self)
```

Test that nested objects in lists create separate Pydantic models

### `test_sample_json_basic_functionality`

```python
def test_sample_json_basic_functionality(self)
```

Test that the tool can process the sample.json file without errors

### `test_with_optional_fields_enabled`

```python
def test_with_optional_fields_enabled(self)
```

Test behavior when allow_optional_fields=True
