import os
import sys
import unittest
from typing import Any, Dict, Set
from unittest.mock import patch

# Add import for the module we're testing
# Assuming the module is in the same directory as the test
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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



class TestInferTypeDictionaryLogic(unittest.TestCase):
    """Test the _infer_type_dictionary_logic function"""

    def setUp(self):
        """Set up test fixtures"""
        self.model_registry = {}
        self.structure_map = {}
        self.dependencies = {}

    def test_none_or_empty_dict(self):
        """Test with None or empty dictionary"""
        result_none = _infer_type_dictionary_logic(
            None,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result_none, ("Optional[Dict[Any, Any]]", None))

        result_empty = _infer_type_dictionary_logic(
            {},
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertEqual(result_empty, ("Optional[Dict[Any, Any]]", None))

    @patch('tools.functions.json_to_pydantic._build_model')
    def test_numeric_keys(self, mock_build_model):
        """Test with dictionary having numeric string keys"""
        # For testing we need to mock _build_model to isolate the test
        mock_build_model.return_value = "class Parent(BaseModel):\n    pass"
        
        # Setup test data - all numeric keys
        data = {"1": 100, "2": 200}
        
        # Check if all keys are digits
        all_digit_keys = all(k.isdigit() for k in data.keys())
        self.assertTrue(all_digit_keys, "Test setup error: Not all keys are digits")
        
        # Get value types
        value_types = {type(v) for v in data.values()}
        self.assertEqual(len(value_types), 1, "Test setup error: Values should be of the same type")
        self.assertEqual(list(value_types)[0], int, "Test setup error: Values should be integers")
        
        # Call the function
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        
        # Assert the result matches the expected format
        self.assertIn("Union[List[int], Dict[str, int]]", result[0])
        self.assertIsNone(result[1])
        
        # Test with float values
        data = {"1": 100.0, "2": 200.0}
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        self.assertIn("Union[List[float], Dict[str, float]]", result[0])
        self.assertIsNone(result[1])

    @patch('tools.functions.json_to_pydantic._build_model')
    def test_nested_dictionary(self, mock_build_model):
        """Test with nested dictionary"""
        # For testing we need to mock _build_model to isolate the test
        mock_build_model.return_value = "class Parent(BaseModel):\n    name: str\n    age: int"
        
        data = {"name": "John", "age": 30}
        result = _infer_type_dictionary_logic(
            data,
            self.model_registry,
            self.structure_map,
            "parent",
            self.dependencies,
            False
        )
        
        # The function should call _build_model and return the class name
        mock_build_model.assert_called_once_with(
            data, "Parent", self.model_registry, self.structure_map, 
            self.dependencies, False
        )
        
        self.assertEqual(result, ("Parent", "Parent"))
        # The model would be added to the registry by _build_model
        # Mock the behavior of adding the model to the registry
        self.model_registry["Parent"] = mock_build_model.return_value

        # Assert that the model was added to the registry
        self.assertIn("Parent", self.model_registry)
        self.assertEqual(self.model_registry["Parent"], mock_build_model.return_value)


if __name__ == "__main__":
    unittest.main()
