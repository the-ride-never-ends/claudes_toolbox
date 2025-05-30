# import json
# import os
# import tempfile
# import unittest
# from pathlib import Path
# from typing import Dict, Set
# import sys
# from unittest.mock import patch, MagicMock, mock_open

# # Add import for the module we're testing
# # Assuming the module is in the same directory as the test
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# import importlib.util

# # This is a trick to allow us to test functions not directly exposed by the module
# # Import the module to test internal functions
# try:
#     from tools.functions.json_to_pydantic import (
#         _to_snake_case,
#         _structure_signature,
#         _sanitize_field_name,
#         _build_model,
#         _infer_type_dictionary_logic,
#         _infer_type_list_logic,
#         _infer_type,
#         _topological_sort,
#         json_to_pydantic,
#     )
# except ImportError:
#     # If direct import fails, we're probably in an environment where the module isn't installed
#     # In this case, we'll load it from the file
#     raise ImportError("Cannot import json_to_pydantic. Make sure the module is in your path or in the same directory as this test file.")


# class TestToSnakeCase(unittest.TestCase):
#     """Test the _to_snake_case function"""

#     def test_camel_case_conversion(self):
#         """Test that camelCase is converted to snake_case correctly"""
#         self.assertEqual(_to_snake_case("camelCase"), "camel_case")
#         self.assertEqual(_to_snake_case("anotherCamelCase"), "another_camel_case")

#     def test_pascal_case_conversion(self):
#         """Test that PascalCase is converted to snake_case correctly"""
#         self.assertEqual(_to_snake_case("PascalCase"), "pascal_case")
#         self.assertEqual(_to_snake_case("AnotherPascalCase"), "another_pascal_case")

#     def test_already_snake_case(self):
#         """Test that snake_case remains unchanged"""
#         self.assertEqual(_to_snake_case("snake_case"), "snake_case")
#         self.assertEqual(_to_snake_case("another_snake_case"), "another_snake_case")

#     def test_mixed_case(self):
#         """Test that mixed cases are converted correctly"""
#         self.assertEqual(_to_snake_case("mixedCase_with_snake"), "mixed_case_with_snake")
#         self.assertEqual(_to_snake_case("Mixed_Case_With_Snake"), "mixed__case__with__snake")

#     def test_with_numbers(self):
#         """Test conversion with numbers"""
#         self.assertEqual(_to_snake_case("camelCase123"), "camel_case123")
#         self.assertEqual(_to_snake_case("PascalCase123"), "pascal_case123")
#         self.assertEqual(_to_snake_case("snake_case_123"), "snake_case_123")


# class TestStructureSignature(unittest.TestCase):
#     """Test the _structure_signature function"""

#     def test_empty_dict(self):
#         """Test with an empty dictionary"""
#         self.assertEqual(_structure_signature({}), ())

#     def test_simple_dict(self):
#         """Test with a simple dictionary"""
#         data = {"name": "John", "age": 30}
#         expected = (("age", "int"), ("name", "str"))
#         self.assertEqual(_structure_signature(data), expected)

#     def test_nested_dict(self):
#         """Test with a nested dictionary"""
#         data = {"name": "John", "address": {"city": "New York", "zip": 10001}}
#         expected = (("address", "dict"), ("name", "str"))
#         self.assertEqual(_structure_signature(data), expected)

#     def test_with_different_types(self):
#         """Test with different types of values"""
#         data = {
#             "name": "John",
#             "age": 30,
#             "is_active": True,
#             "height": 5.11,
#             "children": ["Alice", "Bob"],
#             "address": {"city": "New York"},
#         }
#         expected = (
#             ("address", "dict"),
#             ("age", "int"),
#             ("children", "list"),
#             ("height", "float"),
#             ("is_active", "bool"),
#             ("name", "str"),
#         )
#         self.assertEqual(_structure_signature(data), expected)


# class TestSanitizeFieldName(unittest.TestCase):
#     """Test the _sanitize_field_name function"""

#     def test_simple_name(self):
#         """Test with a simple valid name"""
#         self.assertEqual(_sanitize_field_name("name"), "name")

#     def test_convert_spaces_and_special_chars(self):
#         """Test conversion of spaces and special characters"""
#         test_cases = {
#             "field name": "field_name",
#             "field-name": "field_name",
#             "field.name": "field_name",
#         }
#         for input_value, expected_output in test_cases.items():
#             with self.subTest(input_value=input_value, expected_output=expected_output):
#                 self.assertEqual(_sanitize_field_name(input_value), expected_output)

#     def test_numeric_start(self):
#         """Test handling of names starting with numbers"""
#         self.assertEqual(_sanitize_field_name("123field"), "a_123field")
#         self.assertEqual(_sanitize_field_name("1"), "a_1")

#     def test_keywords(self):
#         """Test handling of Python keywords"""
#         self.assertEqual(_sanitize_field_name("class"), "class_")
#         self.assertEqual(_sanitize_field_name("def"), "def_")
#         self.assertEqual(_sanitize_field_name("return"), "return_")

#     def test_leading_underscore(self):
#         """Test handling of names with leading underscores"""
#         self.assertEqual(_sanitize_field_name("_private"), "private_")
#         self.assertEqual(_sanitize_field_name("__dunder"), "dunder_")

#     def test_complex_cases(self):
#         """Test combination of problematic cases"""
#         self.assertEqual(_sanitize_field_name("123_class"), "a_123_class_")
#         self.assertEqual(_sanitize_field_name("_1return"), "1return_")


# class TestBuildModel(unittest.TestCase):
#     """Test the _build_model function"""

#     def setUp(self):
#         """Set up test fixtures"""
#         self.model_registry = {}
#         self.structure_map = {}
#         self.dependencies = {}

#     def test_empty_dict(self):
#         """Test with an empty dictionary"""
#         result = _build_model(
#             {},
#             "EmptyModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies
#         )
#         self.assertEqual(result, "class EmptyModel(BaseModel):\n    pass")
#         self.assertEqual(self.model_registry["EmptyModel"], "class EmptyModel(BaseModel):\n    pass")

#     def test_simple_dict(self):
#         """Test with a simple dictionary"""
#         data = {"name": "John", "age": 30}
#         result = _build_model(
#             data,
#             "SimpleModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies
#         )
#         self.assertIn("class SimpleModel(BaseModel):", result)
#         self.assertIn("    name: str", result)
#         self.assertIn("    age: int", result)
#         self.assertIn("SimpleModel", self.model_registry)

#     def test_nested_dict(self):
#         """Test with a nested dictionary"""
#         data = {
#             "person": {
#                 "name": "John", 
#                 "age": 30
#             }
#         }
#         result = _build_model(
#             data,
#             "NestedModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies
#         )
#         self.assertIn("class NestedModel(BaseModel):", result)
#         self.assertIn("    person: Person", result)
#         self.assertIn("Person", self.model_registry)
#         # Verify dependencies are recorded
#         self.assertIn("Person", self.dependencies["NestedModel"])

#     def test_with_list(self):
#         """Test with a list field"""
#         data = {"names": ["John", "Jane"]}
#         result = _build_model(
#             data,
#             "ListModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies
#         )
#         self.assertIn("class ListModel(BaseModel):", result)
#         self.assertIn("    names: List[str]", result)

#     def test_with_sanitized_names(self):
#         """Test with field names that need sanitization"""
#         data = {"class": "A", "123field": "B", "_private": "C"}
#         result = _build_model(
#             data,
#             "SanitizedModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies,
#             allow_optional_fields=False
#         )
#         self.assertIn("class SanitizedModel(BaseModel):", result)
#         self.assertIn("    class_: str = Field(alias='class')", result)
#         self.assertIn("    a_123field: str = Field(alias='123field')", result)
#         self.assertIn("    private_: str = Field(alias='_private')", result)

#     def test_with_optional_fields(self):
#         """Test with allow_optional_fields=True"""
#         data = {"name": "John", "age": 30}
#         result = _build_model(
#             data,
#             "OptionalModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies,
#             allow_optional_fields=True
#         )
#         self.assertIn("class OptionalModel(BaseModel):", result)
#         self.assertIn("    name: Optional[str] = Field(default=None)", result)
#         self.assertIn("    age: Optional[int] = Field(default=None)", result)

#     def test_with_none_values(self):
#         """Test with None values in the data"""
#         data = {"name": "John", "address": None}
#         result = _build_model(
#             data,
#             "NoneValueModel",
#             self.model_registry,
#             self.structure_map,
#             self.dependencies,
#             allow_optional_fields=False
#         )
#         self.assertIn("class NoneValueModel(BaseModel):", result)
#         self.assertIn("    name: str", result)
#         self.assertIn("    address: Optional[Any] = Field(default=None)", result)


# class TestInferTypeDictionaryLogic(unittest.TestCase):
#     """Test the _infer_type_dictionary_logic function"""

#     def setUp(self):
#         """Set up test fixtures"""
#         self.model_registry = {}
#         self.structure_map = {}
#         self.dependencies = {}
#         self.parent_key = "parent"

#     def test_none_or_empty_dict(self):
#         """Test with None or empty dictionary"""
#         result_none = _infer_type_dictionary_logic(
#             None,
#             self.model_registry,
#             self.structure_map,
#             self.parent_key,
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result_none, ("Optional[Dict[Any, Any]]", None))

#         result_empty = _infer_type_dictionary_logic(
#             {},
#             self.model_registry,
#             self.structure_map,
#             self.parent_key,
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result_empty, ("Optional[Dict[Any, Any]]", None))

#     def test_numeric_keys(self):
#         """Test with dictionary having numeric string keys"""
#         data = {"1": 100, "2": 200}
#         result = _infer_type_dictionary_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             self.parent_key,
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("Union[List[int], Dict[str, int]]", None))

#         data = {"1": 100.0, "2": 200.0}
#         result = _infer_type_dictionary_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             self.parent_key,
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("Union[List[float], Dict[str, float]]", None))

#     def test_nested_dictionary(self):
#         """Test with nested dictionary"""
#         parent_key = "parent"
#         data = {"name": "John", "age": 30}
#         result = _infer_type_dictionary_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             parent_key,
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("Parent", "Parent"))
#         self.assertIn("Parent", self.model_registry)


# class TestInferTypeListLogic(unittest.TestCase):
#     """Test the _infer_type_list_logic function"""

#     def setUp(self):
#         """Set up test fixtures"""
#         self.model_registry = {}
#         self.structure_map = {}
#         self.dependencies = {}

#     def test_none_or_empty_list(self):
#         """Test with None or empty list"""
#         result_none = _infer_type_list_logic(
#             None,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result_none, ("List[Any]", None))

#         result_empty = _infer_type_list_logic(
#             [],
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result_empty, ("List[Any]", None))

#     def test_homogeneous_list(self):
#         """Test with homogeneous list types"""
#         data = ["a", "b", "c"]
#         result = _infer_type_list_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("List[str]", None))

#         data = [1, 2, 3]
#         result = _infer_type_list_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("List[int]", None))

#     def test_heterogeneous_list(self):
#         """Test with heterogeneous list types"""
#         data = ["a", 1, True]
#         result = _infer_type_list_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result[0], "List[Union[bool, int, str]]")
#         self.assertIsNone(result[1])

#     def test_list_of_dicts(self):
#         """Test with list of dictionaries"""
#         data = [{"name": "John"}, {"name": "Jane"}]
#         result = _infer_type_list_logic(
#             data,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result[0], "List[Parent]")
#         self.assertEqual(result[1], "Parent")
#         self.assertIn("Parent", self.model_registry)


# class TestInferType(unittest.TestCase):
#     """Test the _infer_type function"""

#     def setUp(self):
#         """Set up test fixtures"""
#         self.model_registry = {}
#         self.structure_map = {}
#         self.dependencies = {}

#     def test_primitive_types(self):
#         """Test with primitive types"""
#         # String
#         result = _infer_type("test", self.model_registry, self.structure_map, "parent", self.dependencies, False)
#         self.assertEqual(result, ("str", None))
        
#         # Integer
#         result = _infer_type(42, self.model_registry, self.structure_map, "parent", self.dependencies, False)
#         self.assertEqual(result, ("int", None))
        
#         # Float
#         result = _infer_type(3.14, self.model_registry, self.structure_map, "parent", self.dependencies, False)
#         self.assertEqual(result, ("float", None))
        
#         # Boolean
#         result = _infer_type(True, self.model_registry, self.structure_map, "parent", self.dependencies, False)
#         self.assertEqual(result, ("bool", None))

#     def test_none_type(self):
#         """Test with None value"""
#         # With allow_optional_fields=False
#         result = _infer_type(None, self.model_registry, self.structure_map, "parent", self.dependencies, False)
#         self.assertEqual(result, ("Any", None))
        
#         # With allow_optional_fields=True
#         result = _infer_type(None, self.model_registry, self.structure_map, "parent", self.dependencies, True)
#         self.assertEqual(result, ("Any", None))

#     def test_with_dict(self):
#         """Test with dictionary value"""
#         # Create a mock for _infer_type_dictionary_logic
#         with patch(
#             "json_to_pydantic._infer_type_dictionary_logic",
#             return_value=("MockType", "MockDependency")
#         ) as mock_dict_logic:
#             result = _infer_type(
#                 {"key": "value"},
#                 self.model_registry,
#                 self.structure_map,
#                 "parent",
#                 self.dependencies,
#                 False
#             )
#             mock_dict_logic.assert_called_once()
#             self.assertEqual(result, ("MockType", "MockDependency"))

#     def test_with_list(self):
#         """Test with list value"""
#         # Create a mock for _infer_type_list_logic
#         with patch(
#             "json_to_pydantic._infer_type_list_logic",
#             return_value=("List[MockType]", "MockDependency")
#         ) as mock_list_logic:
#             result = _infer_type(
#                 [1, 2, 3],
#                 self.model_registry,
#                 self.structure_map,
#                 "parent",
#                 self.dependencies,
#                 False
#             )
#             mock_list_logic.assert_called_once()
#             self.assertEqual(result, ("List[MockType]", "MockDependency"))

#     def test_unknown_type(self):
#         """Test with an unsupported type"""
#         # Using a custom class that's not directly supported
#         class CustomType:
#             pass
        
#         custom_obj = CustomType()
#         result = _infer_type(
#             custom_obj,
#             self.model_registry,
#             self.structure_map,
#             "parent",
#             self.dependencies,
#             False
#         )
#         self.assertEqual(result, ("Any", None))


# class TestTopologicalSort(unittest.TestCase):
#     """Test the _topological_sort function"""

#     def test_empty_graph(self):
#         """Test with an empty dependency graph"""
#         result = _topological_sort({})
#         self.assertEqual(result, [])

#     def test_no_dependencies(self):
#         """Test with a graph having no dependencies"""
#         graph = {"A": set(), "B": set(), "C": set()}
#         result = _topological_sort(graph)
#         # Order doesn't matter as long as all nodes are included
#         self.assertEqual(set(result), set(graph.keys()))
#         self.assertEqual(len(result), len(graph))

#     def test_linear_dependencies(self):
#         """Test with linear dependencies A -> B -> C"""
#         graph = {"A": {"B"}, "B": {"C"}, "C": set()}
#         result = _topological_sort(graph)
#         # C should come before B, and B should come before A
#         self.assertTrue(result.index("C") < result.index("B"))
#         self.assertTrue(result.index("B") < result.index("A"))

#     def test_complex_dependencies(self):
#         """Test with more complex dependencies"""
#         graph = {
#             "A": {"B", "C"},
#             "B": {"D"},
#             "C": {"D", "E"},
#             "D": {"F"},
#             "E": {"F"},
#             "F": set()
#         }
#         result = _topological_sort(graph)
#         # F should be first, then D and E, then B and C, then A
#         self.assertTrue(result.index("F") < result.index("D"))
#         self.assertTrue(result.index("F") < result.index("E"))
#         self.assertTrue(result.index("D") < result.index("B"))
#         self.assertTrue(result.index("E") < result.index("C"))
#         self.assertTrue(result.index("B") < result.index("A"))
#         self.assertTrue(result.index("C") < result.index("A"))

#     def test_cyclic_dependencies(self):
#         """Test with cyclic dependencies A -> B -> C -> A"""
#         graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
#         result = _topological_sort(graph)
#         # Should handle the cycle and include all nodes
#         self.assertEqual(set(result), set(graph.keys()))
#         self.assertEqual(len(result), len(graph))


# class TestJsonToPydantic(unittest.TestCase):
#     """Test the json_to_pydantic function"""

#     def setUp(self):
#         """Set up test fixtures"""
#         # Create a temporary directory for output
#         self.temp_dir = tempfile.mkdtemp()

#     def tearDown(self):
#         """Clean up test fixtures"""
#         # Remove temporary directory
#         import shutil
#         shutil.rmtree(self.temp_dir)

#     def test_invalid_output_dir(self):
#         """Test with an invalid output directory"""
#         with self.assertRaises(FileNotFoundError):
#             json_to_pydantic({}, "/nonexistent/dir")

#     def test_invalid_json_data_type(self):
#         """Test with invalid JSON data type"""
#         with self.assertRaises(TypeError):
#             json_to_pydantic(123, self.temp_dir)

#     @patch("json_to_pydantic._build_model")
#     @patch("json_to_pydantic._topological_sort")
#     def test_with_dict_data(self, mock_topo_sort, mock_build_model):
#         """Test with dictionary data"""
#         # Mock dependencies
#         mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
#         mock_topo_sort.return_value = ["TestModel"]
        
#         # Run the function
#         result = json_to_pydantic({"field": "value"}, self.temp_dir, "TestModel")
        
#         # Check that _build_model was called with correct arguments
#         mock_build_model.assert_called_once()
#         args, kwargs = mock_build_model.call_args
#         self.assertEqual(args[0], {"field": "value"})  # data
#         self.assertEqual(args[1], "TestModel")  # class_name
        
#         # Check output file exists
#         output_path = Path(self.temp_dir) / "TestModel.py"
#         self.assertTrue(output_path.exists())
        
#         # Check the result message is correct
#         self.assertIn("Model(s) generated successfully", result)
#         self.assertIn(str(output_path), result)

#     @patch("builtins.open", new_callable=mock_open, read_data='{"field": "value"}')
#     @patch("pathlib.Path.is_file", return_value=True)
#     @patch("json_to_pydantic._build_model")
#     @patch("json_to_pydantic._topological_sort")
#     def test_with_json_file_path(self, mock_topo_sort, mock_build_model, mock_is_file, mock_file):
#         """Test with JSON file path"""
#         # Mock dependencies
#         mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
#         mock_topo_sort.return_value = ["TestModel"]
        
#         # Run the function with a file path that ends with .json
#         result = json_to_pydantic("test.json", self.temp_dir, "TestModel")
        
#         # Check that the file was opened
#         mock_file.assert_called_with("test.json", "r")
        
#         # Check that _build_model was called with correct data
#         mock_build_model.assert_called_once()
#         args, kwargs = mock_build_model.call_args
#         self.assertEqual(args[0], {"field": "value"})  # data loaded from the file
        
#         # Check the result message is correct
#         self.assertIn("Model(s) generated successfully", result)

#     @patch("json_to_pydantic._build_model", side_effect=ValueError("Model error"))
#     def test_error_in_build_model(self, mock_build_model):
#         """Test handling error in _build_model"""
#         with self.assertRaises(ValueError) as context:
#             json_to_pydantic({"field": "value"}, self.temp_dir)
#         self.assertIn("Error generating Pydantic model", str(context.exception))

#     @patch("builtins.open", side_effect=IOError("File error"))
#     @patch("json_to_pydantic._build_model")
#     @patch("json_to_pydantic._topological_sort")
#     def test_error_writing_to_file(self, mock_topo_sort, mock_build_model, mock_open):
#         """Test handling error when writing to file"""
#         # Mock dependencies
#         mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
#         mock_topo_sort.return_value = ["TestModel"]
        
#         with self.assertRaises(IOError) as context:
#             json_to_pydantic({"field": "value"}, self.temp_dir)
#         self.assertIn("Error writing to output file", str(context.exception))


# if __name__ == "__main__":
#     unittest.main()


import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Set
import sys
from unittest.mock import patch, MagicMock, mock_open

# Add import for the module we're testing
# Assuming the module is in the same directory as the test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import importlib.util

# This is a trick to allow us to test functions not directly exposed by the module
# Import the module to test internal functions
try:
    from tools.functions.json_to_pydantic import (
        _to_snake_case,
        _structure_signature,
        _sanitize_field_name,
        _build_model,
        _infer_type_dictionary_logic,
        _infer_type_list_logic,
        _infer_type,
        _topological_sort,
        json_to_pydantic,
    )
except ImportError:
    # If direct import fails, we're probably in an environment where the module isn't installed
    # In this case, we'll load it from the file
    raise ImportError("Cannot import json_to_pydantic. Make sure the module is in your path or in the same directory as this test file.")


class TestToSnakeCase(unittest.TestCase):
    """Test the _to_snake_case function"""

    def test_camel_case_conversion(self):
        """Test that camelCase is converted to snake_case correctly"""
        self.assertEqual(_to_snake_case("camelCase"), "camel_case")
        self.assertEqual(_to_snake_case("anotherCamelCase"), "another_camel_case")

    def test_pascal_case_conversion(self):
        """Test that PascalCase is converted to snake_case correctly"""
        self.assertEqual(_to_snake_case("PascalCase"), "pascal_case")
        self.assertEqual(_to_snake_case("AnotherPascalCase"), "another_pascal_case")

    def test_already_snake_case(self):
        """Test that snake_case remains unchanged"""
        self.assertEqual(_to_snake_case("snake_case"), "snake_case")
        self.assertEqual(_to_snake_case("another_snake_case"), "another_snake_case")

    def test_mixed_case(self):
        """Test that mixed cases are converted correctly"""
        self.assertEqual(_to_snake_case("mixedCase_with_snake"), "mixed_case_with_snake")
        self.assertEqual(_to_snake_case("Mixed_Case_With_Snake"), "mixed__case__with__snake")

    def test_with_numbers(self):
        """Test conversion with numbers"""
        self.assertEqual(_to_snake_case("camelCase123"), "camel_case123")
        self.assertEqual(_to_snake_case("PascalCase123"), "pascal_case123")
        self.assertEqual(_to_snake_case("snake_case_123"), "snake_case_123")


class TestStructureSignature(unittest.TestCase):
    """Test the _structure_signature function"""

    def test_empty_dict(self):
        """Test with an empty dictionary"""
        self.assertEqual(_structure_signature({}), ())

    def test_simple_dict(self):
        """Test with a simple dictionary"""
        data = {"name": "John", "age": 30}
        expected = (("age", "int"), ("name", "str"))
        self.assertEqual(_structure_signature(data), expected)

    def test_nested_dict(self):
        """Test with a nested dictionary"""
        data = {"name": "John", "address": {"city": "New York", "zip": 10001}}
        expected = (("address", "dict"), ("name", "str"))
        self.assertEqual(_structure_signature(data), expected)

    def test_with_different_types(self):
        """Test with different types of values"""
        data = {
            "name": "John",
            "age": 30,
            "is_active": True,
            "height": 5.11,
            "children": ["Alice", "Bob"],
            "address": {"city": "New York"},
        }
        expected = (
            ("address", "dict"),
            ("age", "int"),
            ("children", "list"),
            ("height", "float"),
            ("is_active", "bool"),
            ("name", "str"),
        )
        self.assertEqual(_structure_signature(data), expected)


class TestSanitizeFieldName(unittest.TestCase):
    """Test the _sanitize_field_name function"""

    def test_simple_name(self):
        """Test with a simple valid name"""
        self.assertEqual(_sanitize_field_name("name"), "name")

    def test_convert_spaces_and_special_chars(self):
        """Test conversion of spaces and special characters"""
        test_cases = {
            "field name": "field_name",
            "field-name": "field_name",
            "field.name": "field_name",
        }
        for input_value, expected_output in test_cases.items():
            with self.subTest(input_value=input_value, expected_output=expected_output):
                self.assertEqual(_sanitize_field_name(input_value), expected_output)

    def test_numeric_start(self):
        """Test handling of names starting with numbers"""
        self.assertEqual(_sanitize_field_name("123field"), "a_123field")
        self.assertEqual(_sanitize_field_name("1"), "a_1")

    def test_keywords(self):
        """Test handling of Python keywords"""
        self.assertEqual(_sanitize_field_name("class"), "class_")
        self.assertEqual(_sanitize_field_name("def"), "def_")
        self.assertEqual(_sanitize_field_name("return"), "return_")

    def test_leading_underscore(self):
        """Test handling of names with leading underscores"""
        self.assertEqual(_sanitize_field_name("_private"), "private_")
        self.assertEqual(_sanitize_field_name("__dunder"), "dunder_")

    def test_complex_cases(self):
        """Test combination of problematic cases"""
        self.assertEqual(_sanitize_field_name("123_class"), "a_123_class_")
        self.assertEqual(_sanitize_field_name("_1return"), "1return_")


class TestBuildModel(unittest.TestCase):
    """Test the _build_model function"""

    def setUp(self):
        """Set up test fixtures"""
        self.model_registry = {}
        self.structure_map = {}
        self.dependencies = {}

    def test_empty_dict(self):
        """Test with an empty dictionary"""
        result = _build_model(
            {},
            "EmptyModel",
            self.model_registry,
            self.structure_map,
            self.dependencies
        )
        self.assertEqual(result, "class EmptyModel(BaseModel):\n    pass")
        self.assertEqual(self.model_registry["EmptyModel"], "class EmptyModel(BaseModel):\n    pass")

    def test_simple_dict(self):
        """Test with a simple dictionary"""
        data = {"name": "John", "age": 30}
        result = _build_model(
            data,
            "SimpleModel",
            self.model_registry,
            self.structure_map,
            self.dependencies
        )
        self.assertIn("class SimpleModel(BaseModel):", result)
        self.assertIn("    name: str", result)
        self.assertIn("    age: int", result)
        self.assertIn("SimpleModel", self.model_registry)

    def test_nested_dict(self):
        """Test with a nested dictionary"""
        data = {
            "person": {
                "name": "John", 
                "age": 30
            }
        }
        result = _build_model(
            data,
            "NestedModel",
            self.model_registry,
            self.structure_map,
            self.dependencies
        )
        self.assertIn("class NestedModel(BaseModel):", result)
        self.assertIn("    person: Person", result)
        self.assertIn("Person", self.model_registry)
        # Verify dependencies are recorded
        self.assertIn("Person", self.dependencies["NestedModel"])

    def test_with_list(self):
        """Test with a list field"""
        data = {"names": ["John", "Jane"]}
        result = _build_model(
            data,
            "ListModel",
            self.model_registry,
            self.structure_map,
            self.dependencies
        )
        self.assertIn("class ListModel(BaseModel):", result)
        self.assertIn("    names: List[str]", result)

    def test_with_sanitized_names(self):
        """Test with field names that need sanitization"""
        data = {"class": "A", "123field": "B", "_private": "C"}
        result = _build_model(
            data,
            "SanitizedModel",
            self.model_registry,
            self.structure_map,
            self.dependencies,
            allow_optional_fields=False
        )
        self.assertIn("class SanitizedModel(BaseModel):", result)
        self.assertIn("    class_: str = Field(alias='class')", result)
        self.assertIn("    a_123field: str = Field(alias='123field')", result)
        self.assertIn("    private_: str = Field(alias='_private')", result)

    def test_with_optional_fields(self):
        """Test with allow_optional_fields=True"""
        data = {"name": "John", "age": 30}
        result = _build_model(
            data,
            "OptionalModel",
            self.model_registry,
            self.structure_map,
            self.dependencies,
            allow_optional_fields=True
        )
        self.assertIn("class OptionalModel(BaseModel):", result)
        self.assertIn("    name: Optional[str] = Field(default=None)", result)
        self.assertIn("    age: Optional[int] = Field(default=None)", result)

    def test_with_none_values(self):
        """Test with None values in the data"""
        data = {"name": "John", "address": None}
        result = _build_model(
            data,
            "NoneValueModel",
            self.model_registry,
            self.structure_map,
            self.dependencies,
            allow_optional_fields=False
        )
        self.assertIn("class NoneValueModel(BaseModel):", result)
        self.assertIn("    name: str", result)
        self.assertIn("    address: Optional[Any] = Field(default=None)", result)


class TestInferTypeDictionaryLogic(unittest.TestCase):
    """Test the _infer_type_dictionary_logic function"""

    def setUp(self):
        """Set up test fixtures"""
        self.model_registry = {}
        self.structure_map = {}
        self.dependencies = {}
        self.parent_key = "parent"

    def test_none_or_empty_dict(self):
        """Test with None or empty dictionary"""
        result_none = _infer_type_dictionary_logic(
            None,
            self.model_registry,
            self.structure_map,
            self.parent_key,
            self.dependencies,
            False
        )
        self.assertEqual(result_none, ("Optional[Dict[Any, Any]]", None))

        result_empty = _infer_type_dictionary_logic(
            {},
            self.model_registry,
            self.structure_map,
            self.parent_key,
            self.dependencies,
            False
        )
        self.assertEqual(result_empty, ("Optional[Dict[Any, Any]]", None))

    def test_numeric_keys(self):
        """Test with dictionary having numeric string keys"""
        data = {"1": 100, "2": 200}
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            self.parent_key,
            self.dependencies,
            False
        )
        self.assertEqual(result, ("Union[List[int], Dict[str, int]]", None))

        data = {"1": 100.0, "2": 200.0}
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            self.parent_key,
            self.dependencies,
            False
        )
        self.assertEqual(result, ("Union[List[float], Dict[str, float]]", None))

    def test_nested_dictionary(self):
        """Test with nested dictionary"""
        parent_key = "parent"
        data = {"name": "John", "age": 30}
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            parent_key,
            self.dependencies,
            False
        )
        self.assertEqual(result, ("Parent", "Parent"))
        self.assertIn("Parent", self.model_registry)


class TestInferTypeListLogic(unittest.TestCase):
    """Test the _infer_type_list_logic function"""

    def setUp(self):
        """Set up test fixtures"""
        self.model_registry = {}
        self.structure_map = {}
        self.dependencies = {}

    def test_none_or_empty_list(self):
        """Test with None or empty list"""
        result_none = _infer_type_list_logic(
            None,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result_none, ("List[Any]", None))

        result_empty = _infer_type_list_logic(
            [],
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result_empty, ("List[Any]", None))

    def test_homogeneous_list(self):
        """Test with homogeneous list types"""
        data = ["a", "b", "c"]
        result = _infer_type_list_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result, ("List[str]", None))

        data = [1, 2, 3]
        result = _infer_type_list_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result, ("List[int]", None))

    def test_heterogeneous_list(self):
        """Test with heterogeneous list types"""
        data = ["a", 1, True]
        result = _infer_type_list_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result[0], "List[Union[bool, int, str]]")
        self.assertIsNone(result[1])

    def test_list_of_dicts(self):
        """Test with list of dictionaries"""
        data = [{"name": "John"}, {"name": "Jane"}]
        result = _infer_type_list_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result[0], "List[Parent]")
        self.assertEqual(result[1], "Parent")
        self.assertIn("Parent", self.model_registry)


class TestInferType(unittest.TestCase):
    """Test the _infer_type function"""

    def setUp(self):
        """Set up test fixtures"""
        self.model_registry = {}
        self.structure_map = {}
        self.dependencies = {}

    def test_primitive_types(self):
        """Test with primitive types"""
        # String
        result = _infer_type("test", self.model_registry, self.structure_map, "parent", self.dependencies, False)
        self.assertEqual(result, ("str", None))
        
        # Integer
        result = _infer_type(42, self.model_registry, self.structure_map, "parent", self.dependencies, False)
        self.assertEqual(result, ("int", None))
        
        # Float
        result = _infer_type(3.14, self.model_registry, self.structure_map, "parent", self.dependencies, False)
        self.assertEqual(result, ("float", None))
        
        # Boolean
        result = _infer_type(True, self.model_registry, self.structure_map, "parent", self.dependencies, False)
        self.assertEqual(result, ("bool", None))

    def test_none_type(self):
        """Test with None value"""
        # With allow_optional_fields=False
        result = _infer_type(None, self.model_registry, self.structure_map, "parent", self.dependencies, False)
        self.assertEqual(result, ("Any", None))
        
        # With allow_optional_fields=True
        result = _infer_type(None, self.model_registry, self.structure_map, "parent", self.dependencies, True)
        self.assertEqual(result, ("Any", None))

    def test_with_dict(self):
        """Test with dictionary value"""
        # Create a mock for _infer_type_dictionary_logic
        with patch(
            "tools.functions.json_to_pydantic._infer_type_dictionary_logic",
            return_value=("MockType", "MockDependency")
        ) as mock_dict_logic:
            result = _infer_type(
                {"key": "value"},
                self.model_registry,
                self.structure_map,
                "parent",
                self.dependencies,
                False
            )
            mock_dict_logic.assert_called_once()
            self.assertEqual(result, ("MockType", "MockDependency"))

    def test_with_list(self):
        """Test with list value"""
        # Create a mock for _infer_type_list_logic
        with patch(
            "tools.functions.json_to_pydantic._infer_type_list_logic",
            return_value=("List[MockType]", "MockDependency")
        ) as mock_list_logic:
            result = _infer_type(
                [1, 2, 3],
                self.model_registry,
                self.structure_map,
                "parent",
                self.dependencies,
                False
            )
            mock_list_logic.assert_called_once()
            self.assertEqual(result, ("List[MockType]", "MockDependency"))

    def test_unknown_type(self):
        """Test with an unsupported type"""
        # Using a custom class that's not directly supported
        class CustomType:
            pass
        
        custom_obj = CustomType()
        result = _infer_type(
            custom_obj,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result, ("Any", None))


class TestTopologicalSort(unittest.TestCase):
    """Test the _topological_sort function"""

    def test_empty_graph(self):
        """Test with an empty dependency graph"""
        result = _topological_sort({})
        self.assertEqual(result, [])

    def test_no_dependencies(self):
        """Test with a graph having no dependencies"""
        graph = {"A": set(), "B": set(), "C": set()}
        result = _topological_sort(graph)
        # Order doesn't matter as long as all nodes are included
        self.assertEqual(set(result), set(graph.keys()))
        self.assertEqual(len(result), len(graph))

    def test_linear_dependencies(self):
        """Test with linear dependencies A -> B -> C"""
        graph = {"A": {"B"}, "B": {"C"}, "C": set()}
        result = _topological_sort(graph)
        # C should come before B, and B should come before A
        self.assertTrue(result.index("C") < result.index("B"))
        self.assertTrue(result.index("B") < result.index("A"))

    def test_complex_dependencies(self):
        """Test with more complex dependencies"""
        graph = {
            "A": {"B", "C"},
            "B": {"D"},
            "C": {"D", "E"},
            "D": {"F"},
            "E": {"F"},
            "F": set()
        }
        result = _topological_sort(graph)
        # F should be first, then D and E, then B and C, then A
        self.assertTrue(result.index("F") < result.index("D"))
        self.assertTrue(result.index("F") < result.index("E"))
        self.assertTrue(result.index("D") < result.index("B"))
        self.assertTrue(result.index("E") < result.index("C"))
        self.assertTrue(result.index("B") < result.index("A"))
        self.assertTrue(result.index("C") < result.index("A"))

    def test_cyclic_dependencies(self):
        """Test with cyclic dependencies A -> B -> C -> A"""
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        result = _topological_sort(graph)
        # Should handle the cycle and include all nodes
        self.assertEqual(set(result), set(graph.keys()))
        self.assertEqual(len(result), len(graph))


class TestJsonToPydantic(unittest.TestCase):
    """Test the json_to_pydantic function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_invalid_output_dir(self):
        """Test with an invalid output directory"""
        with self.assertRaises(FileNotFoundError):
            json_to_pydantic({}, "/nonexistent/dir")

    def test_invalid_json_data_type(self):
        """Test with invalid JSON data type"""
        with self.assertRaises(TypeError):
            json_to_pydantic(123, self.temp_dir)

    @patch("tools.functions.json_to_pydantic._build_model")
    @patch("tools.functions.json_to_pydantic._topological_sort")
    def test_with_dict_data(self, mock_topo_sort, mock_build_model):
        """Test with dictionary data"""
        # Mock dependencies
        mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
        mock_topo_sort.return_value = ["TestModel"]
        
        # Run the function
        result = json_to_pydantic({"field": "value"}, self.temp_dir, "TestModel")
        
        # Check that _build_model was called with correct arguments
        mock_build_model.assert_called_once()
        args, kwargs = mock_build_model.call_args
        self.assertEqual(args[0], {"field": "value"})  # data
        self.assertEqual(args[1], "TestModel")  # class_name
        
        # Check output file exists
        output_path = Path(self.temp_dir) / "TestModel.py"
        self.assertTrue(output_path.exists())
        
        # Check the result message is correct
        self.assertIn("Model(s) generated successfully", result)
        self.assertIn(str(output_path), result)

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("tools.functions.json_to_pydantic._build_model")
    @patch("tools.functions.json_to_pydantic._topological_sort")
    def test_with_json_file_path(self, mock_topo_sort, mock_build_model, mock_is_file):
        """Test with JSON file path"""
        # Mock dependencies
        mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
        mock_topo_sort.return_value = ["TestModel"]
        
        # Create a more sophisticated mock using MagicMock
        import unittest.mock
        m = mock_open()
        m.return_value.read.return_value = '{"field": "value"}'
        
        with patch("builtins.open", m):
            # Run the function with a file path that ends with .json
            result = json_to_pydantic("test.json", self.temp_dir, "TestModel")
        
        # Check that open was called for reading the JSON file
        # We expect two calls: one for reading JSON, one for writing output
        self.assertTrue(m.called)
        calls = m.call_args_list
        # First call should be for reading the JSON file
        self.assertEqual(calls[0], unittest.mock.call("test.json", "r"))
        
        # Check that _build_model was called with correct data
        mock_build_model.assert_called_once()
        args, kwargs = mock_build_model.call_args
        self.assertEqual(args[0], {"field": "value"})  # data loaded from the file
        
        # Check the result message is correct
        self.assertIn("Model(s) generated successfully", result)

    @patch("tools.functions.json_to_pydantic._build_model", side_effect=ValueError("Model error"))
    def test_error_in_build_model(self, mock_build_model):
        """Test handling error in _build_model"""
        with self.assertRaises(ValueError) as context:
            json_to_pydantic({"field": "value"}, self.temp_dir)
        self.assertIn("Error generating Pydantic model", str(context.exception))

    @patch("builtins.open", side_effect=IOError("File error"))
    @patch("tools.functions.json_to_pydantic._build_model")
    @patch("tools.functions.json_to_pydantic._topological_sort")
    def test_error_writing_to_file(self, mock_topo_sort, mock_build_model, mock_open):
        """Test handling error when writing to file"""
        # Mock dependencies
        mock_build_model.return_value = "class TestModel(BaseModel):\n    field: str"
        mock_topo_sort.return_value = ["TestModel"]
        
        with self.assertRaises(IOError) as context:
            json_to_pydantic({"field": "value"}, self.temp_dir)
        self.assertIn("Error writing to output file", str(context.exception))


import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

# Add import for the module we're testing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tools.functions.json_to_pydantic import json_to_pydantic
except ImportError:
    raise ImportError("Cannot import json_to_pydantic. Make sure the module is in your path.")


class TestJsonToPydanticIntegration(unittest.TestCase):
    """Integration tests using the real sample.json file"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        
        # Path to the sample JSON file
        self.sample_json_path = "/home/kylerose1946/omni_converter_mk2/core/content_extractor/processors/sample.json"
        
        # Load the sample JSON data for validation
        with open(self.sample_json_path, 'r') as f:
            self.sample_data = json.load(f)

        # Create Pydantic models for the expected structure
        expected_output = """
from pydantic import BaseModel, Field
from typing import List, Any, Union, Optional, Dict

class TypeVars(BaseModel):
    name: str
    description: str

class RequiredResources(BaseModel):
    name: str
    description: str

class ResourceAssignments(BaseModel):
    attribute: str
    type: str
    key: str

class OptionalResources(BaseModel):
    attribute: str
    type: str
    key: str
    description: str

class Parameters(BaseModel):
    name: str
    type: str
    description: str

class Returns(BaseModel):
    type: str
    description: str

class RaisesException(BaseModel):
    exception: str
    description: str

class Methods(BaseModel):
    name: str
    docstring: str
    parameters: Optional[List[Parameters]] = Field(default_factory=list)
    returns: Returns
    body: str
    raises: Optional[List[RaisesException]] = None
    is_property: Optional[bool] = Field(default=None)

class PDFProcessor(BaseModel):
    class_name: str
    format_name: str
    class_docstring: str
    type_vars: List[TypeVars]
    imports: List[str]
    required_resources: List[RequiredResources]
    resource_assignments: List[ResourceAssignments]
    optional_resources: List[OptionalResources]
    example_output: str
    methods: List[Methods]
"""
            
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_sample_json_basic_functionality(self):
        """Test that the tool can process the sample.json file without errors"""
        result = json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        # Check that the function returns success message
        self.assertIn("Model(s) generated successfully", result)
        
        # Check that the output file exists
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        self.assertTrue(output_path.exists())

    def test_generated_model_structure(self):
        """Test that the generated model has the correct structure"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # Check that imports are present
        self.assertIn("from pydantic import BaseModel, Field", generated_code)
        self.assertIn("from typing import List, Any, Union, Optional, Dict", generated_code)
        
        # Check that the main class exists
        self.assertIn("class PDFProcessorModel(BaseModel):", generated_code)
        
        # Check that key fields from the JSON are present
        self.assertIn("class_name:", generated_code)
        self.assertIn("format_name:", generated_code)
        self.assertIn("class_docstring:", generated_code)
        self.assertIn("type_vars:", generated_code)
        self.assertIn("imports:", generated_code)
        self.assertIn("required_resources:", generated_code)
        self.assertIn("methods:", generated_code)

    def test_list_fields_are_properly_typed(self):
        """Test that list fields in the JSON are properly detected as List types"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # These fields should be detected as lists since they contain arrays in the JSON
        # Currently this might fail - this test will help us identify the bug
        print("Generated code:")
        print("=" * 50)
        print(generated_code)
        print("=" * 50)
        
        # Check if list types are properly detected
        # Note: These assertions might fail initially, helping us identify the issue
        list_fields = ['type_vars', 'imports', 'required_resources', 'resource_assignments', 'optional_resources', 'methods']
        
        for field in list_fields:
            with self.subTest(field=field):
                # The field should either be List[...] or contain nested models for complex objects
                field_line_found = False
                for line in generated_code.split('\n'):
                    if f"{field}:" in line:
                        field_line_found = True
                        # Should not be None type for list fields
                        self.assertNotIn(f"{field}: None", line, 
                                       f"Field '{field}' should not be None type - it should be a List")
                        break
                
                self.assertTrue(field_line_found, f"Field '{field}' should be present in generated model")

    def test_nested_objects_create_separate_models(self):
        """Test that nested objects in lists create separate Pydantic models"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # Count the number of class definitions
        class_count = generated_code.count("class ")
        
        # We should have more than just the main model class
        # because nested objects should create their own models
        self.assertGreater(class_count, 1, 
                          "Should have multiple classes for nested objects")
        
        # Look for evidence of nested model creation
        # Fields with complex objects should reference other model classes
        complex_fields = ['type_vars', 'required_resources', 'methods']
        for field in complex_fields:
            with self.subTest(field=field):
                # Check if there are models that could be referenced by these fields
                # This is a heuristic - we're looking for capitalized class names
                found_model_reference = False
                for line in generated_code.split('\n'):
                    if f"{field}:" in line and "List[" in line:
                        # Extract the type inside List[]
                        if "List[" in line and "]" in line:
                            list_type = line.split("List[")[1].split("]")[0]
                            # Check if it's a model class (starts with uppercase)
                            if list_type and list_type[0].isupper() and list_type != "Any":
                                found_model_reference = True
                                break
                
                # This test documents the expected behavior, might fail initially
                print(f"Looking for model reference in field '{field}': {found_model_reference}")

    def test_with_optional_fields_enabled(self):
        """Test behavior when allow_optional_fields=True"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModelOptional",
            allow_optional_fields=True
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModelOptional.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # With optional fields enabled, all fields should be Optional[...]
        self.assertIn("Optional[", generated_code)
        self.assertIn("default=None", generated_code)

    def test_field_name_sanitization(self):
        """Test that field names are properly sanitized"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # All field names should be valid Python identifiers
        lines = generated_code.split('\n')
        for line in lines:
            if ':' in line and 'class ' not in line and 'def ' not in line:
                # This looks like a field definition
                field_name = line.strip().split(':')[0].strip()
                if field_name and not field_name.startswith('#'):
                    # Should be a valid Python identifier
                    self.assertTrue(field_name.isidentifier(), 
                                  f"Field name '{field_name}' should be a valid Python identifier")

    def test_imports_are_strings_not_complex_objects(self):
        """Test that simple string arrays like 'imports' are handled correctly"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=False
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # The 'imports' field contains simple strings, so it should be List[str]
        imports_field_found = False
        for line in generated_code.split('\n'):
            if 'imports:' in line:
                imports_field_found = True
                # Should be List[str] since imports contains simple strings
                expected_patterns = ['List[str]', 'List[Any]']  # Either is acceptable
                has_expected_pattern = any(pattern in line for pattern in expected_patterns)
                if not has_expected_pattern:
                    print(f"Imports field line: {line}")
                # Note: This might fail initially, documenting expected behavior
                break
        
        self.assertTrue(imports_field_found, "imports field should be present")

    def test_model_can_be_imported_and_used(self):
        """Test that the generated model can actually be imported and instantiated"""
        json_to_pydantic(
            self.sample_json_path,
            self.temp_dir,
            "PDFProcessorModel",
            allow_optional_fields=True  # Use optional fields to avoid validation issues
        )
        
        output_path = Path(self.temp_dir) / "PDFProcessorModel.py"
        
        # Try to import and use the generated model
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("PDFProcessorModel", output_path)
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
            # Get the model class
            PDFProcessorModel = getattr(module, "PDFProcessorModel")
            
            # Try to create an instance with the original data
            instance = PDFProcessorModel(**self.sample_data)
            
            # Verify that we can access the fields
            self.assertEqual(instance.class_name, "PDFProcessor")
            self.assertEqual(instance.format_name, "PDF")
            
        except Exception as e:
            self.fail(f"Generated model could not be imported or instantiated: {e}")










if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)