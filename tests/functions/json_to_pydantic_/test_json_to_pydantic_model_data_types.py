import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest


from tools.functions.json_to_pydantic_model import (
    json_to_pydantic_model, _InvalidJSONError, _ModelValidationError, _PydanticGenerationError
)

from pydantic import ValidationError, BaseModel



class TestJsonToPydanticModelDataTypes(unittest.TestCase):
    """Test handling of various JSON data types."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_string_fields(self):
        """
        GIVEN JSON with string fields
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as str
        """
        string_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "description": "A test user",
            "empty_string": "",
            "unicode_string": "Hello 世界 🌍"
        }
        
        output_path = os.path.join(self.temp_dir, "string_fields.py")
        
        result = json_to_pydantic_model(
            json_data=string_data,
            output_file_path=output_path,
            model_name="StringFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class StringFieldsModel(BaseModel)", content)
            self.assertIn("name: str", content)
            self.assertIn("email: str", content)
            self.assertIn("description: str", content)
            self.assertIn("empty_string: str", content)
            self.assertIn("unicode_string: str", content)

    def test_integer_fields(self):
        """
        GIVEN JSON with integer fields
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as int
        """
        integer_data = {
            "id": 123,
            "age": 30,
            "count": 0,
            "negative_number": -45,
            "large_number": 9223372036854775807
        }
        
        output_path = os.path.join(self.temp_dir, "integer_fields.py")
        
        result = json_to_pydantic_model(
            json_data=integer_data,
            output_file_path=output_path,
            model_name="IntegerFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class IntegerFieldsModel(BaseModel)", content)
            self.assertIn("id: int", content)
            self.assertIn("age: int", content)
            self.assertIn("count: int", content)
            self.assertIn("negative_number: int", content)
            self.assertIn("large_number: int", content)

    def test_float_fields(self):
        """
        GIVEN JSON with float fields
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as float
        """
        float_data = {
            "price": 19.99,
            "temperature": -2.5,
            "percentage": 0.75,
            "scientific": 1.23e-4,
            "pi": 3.141592653589793
        }
        
        output_path = os.path.join(self.temp_dir, "float_fields.py")
        
        result = json_to_pydantic_model(
            json_data=float_data,
            output_file_path=output_path,
            model_name="FloatFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class FloatFieldsModel(BaseModel)", content)
            self.assertIn("price: float", content)
            self.assertIn("temperature: float", content)
            self.assertIn("percentage: float", content)
            self.assertIn("scientific: float", content)
            self.assertIn("pi: float", content)

    def test_boolean_fields(self):
        """
        GIVEN JSON with boolean fields
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as bool
        """
        boolean_data = {
            "is_active": True,
            "is_verified": False,
            "has_premium": True,
            "accepts_marketing": False
        }
        
        output_path = os.path.join(self.temp_dir, "boolean_fields.py")
        
        result = json_to_pydantic_model(
            json_data=boolean_data,
            output_file_path=output_path,
            model_name="BooleanFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class BooleanFieldsModel(BaseModel)", content)
            self.assertIn("is_active: bool", content)
            self.assertIn("is_verified: bool", content)
            self.assertIn("has_premium: bool", content)
            self.assertIn("accepts_marketing: bool", content)

    def test_null_fields(self):
        """
        GIVEN JSON with null values
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as Optional[Any]
        """
        null_data = {
            "name": "John",
            "middle_name": None,
            "optional_field": None,
            "another_null": None
        }
        
        output_path = os.path.join(self.temp_dir, "null_fields.py")
        
        result = json_to_pydantic_model(
            json_data=null_data,
            output_file_path=output_path,
            model_name="NullFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class NullFieldsModel(BaseModel)", content)
            self.assertIn("name: str", content)
            
            # Null fields should be Optional or Any
            self.assertTrue("Optional" in content or "Any" in content)
            self.assertIn("from typing import", content)

    def test_mixed_type_lists(self):
        """
        GIVEN JSON with lists containing mixed types
        WHEN json_to_pydantic_model is called
        THEN expect fields typed as List[Any] or Union types
        """
        mixed_list_data = {
            "homogeneous_strings": ["apple", "banana", "cherry"],
            "homogeneous_numbers": [1, 2, 3, 4, 5],
            "mixed_types": [1, "hello", True, 3.14, None],
            "nested_mixed": [
                {"type": "string", "value": "text"},
                {"type": "number", "value": 42},
                {"type": "boolean", "value": True}
            ]
        }
        
        output_path = os.path.join(self.temp_dir, "mixed_lists.py")
        
        result = json_to_pydantic_model(
            json_data=mixed_list_data,
            output_file_path=output_path,
            model_name="MixedListsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class MixedListsModel(BaseModel)", content)
            self.assertIn("List", content)
            self.assertIn("from typing import", content)
            
            # Homogeneous lists should have specific types
            self.assertIn("homogeneous_strings: List[str]", content)
            self.assertIn("homogeneous_numbers: List[int]", content)
            
            # Mixed types should use Any or Union
            self.assertTrue("Any" in content or "Union" in content)

    def test_complex_mixed_data_types(self):
        """
        GIVEN JSON with all data types mixed together
        WHEN json_to_pydantic_model is called
        THEN expect proper typing for each field
        """
        complex_data = {
            "user_id": 12345,
            "username": "johndoe",
            "balance": 1234.56,
            "is_premium": True,
            "last_login": None,
            "tags": ["user", "premium", "verified"],
            "metadata": {
                "created_at": "2023-01-01T00:00:00Z",
                "login_count": 42,
                "success_rate": 0.95,
                "is_admin": False,
                "notes": None
            },
            "permissions": [
                {"resource": "users", "actions": ["read", "write"]},
                {"resource": "posts", "actions": ["read"]}
            ]
        }
        
        output_path = os.path.join(self.temp_dir, "complex_types.py")
        
        result = json_to_pydantic_model(
            json_data=complex_data,
            output_file_path=output_path,
            model_name="ComplexTypesModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            import pprint
            pprint.pprint(f"test_complex_mixed_data_types\n\n{content}")
            
            # Should have main model and nested models
            self.assertIn("class Metadata(BaseModel)", content)
            self.assertIn("class Permissions(BaseModel)", content)
            self.assertIn("class ComplexTypesModel(BaseModel)", content)
            
            # Check basic type annotations
            self.assertIn("user_id: int", content)
            self.assertIn("username: str", content)
            self.assertIn("balance: float", content)
            self.assertIn("is_premium: bool", content)
            self.assertIn("tags: List[str]", content)
            self.assertIn("permissions: List[Permissions]", content)
            self.assertIn("metadata: Metadata", content)
            
            # Should handle null fields appropriately
            self.assertTrue("Optional" in content or "Any" in content)

    def test_edge_case_numeric_types(self):
        """
        GIVEN JSON with edge case numeric values
        WHEN json_to_pydantic_model is called
        THEN expect appropriate type handling
        """
        numeric_edge_cases = {
            "zero_int": 0,
            "zero_float": 0.0,
            "very_large_int": 18446744073709551615,
            "very_small_float": 1e-300,
            "very_large_float": 1e300,
            "negative_zero": -0.0,
            "infinity_like": 1e400,  # May be converted to string by JSON
        }
        
        output_path = os.path.join(self.temp_dir, "numeric_edge_cases.py")
        
        result = json_to_pydantic_model(
            json_data=numeric_edge_cases,
            output_file_path=output_path,
            model_name="NumericEdgeCasesModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class NumericEdgeCasesModel(BaseModel)", content)
            # Should handle various numeric types appropriately
            self.assertTrue("int" in content or "float" in content)

    def test_empty_containers(self):
        """
        GIVEN JSON with empty lists and objects
        WHEN json_to_pydantic_model is called
        THEN expect appropriate handling with Optional or default values
        """
        empty_containers = {
            "name": "test",
            "empty_list": [],
            "empty_object": {},
            "nested": {
                "also_empty_list": [],
                "value": "something"
            }
        }
        
        output_path = os.path.join(self.temp_dir, "empty_containers.py")
        
        result = json_to_pydantic_model(
            json_data=empty_containers,
            output_file_path=output_path,
            model_name="EmptyContainersModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            self.assertIn("class EmptyContainersModel(BaseModel)", content)
            # Should handle empty containers appropriately
            self.assertTrue("List" in content or "Optional" in content or "Field" in content)


if __name__ == '__main__':
    unittest.main()