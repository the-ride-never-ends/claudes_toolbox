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



class TestJsonToPydanticModelInputValidation(unittest.TestCase):
    """Test input validation for json_to_pydantic_model function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = {"name": "John", "age": 30}
        self.test_json_string = '{"name": "John", "age": 30}'
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory and files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_json_data_as_valid_dict(self):
        """
        GIVEN a valid dictionary with string and integer fields
        WHEN json_to_pydantic_model is called with the dict
        THEN expect:
            - Function executes successfully
            - Returns success message with correct output path
            - Generated file exists at specified location
        """
        output_path = os.path.join(self.temp_dir, "test_model.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="TestModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertIn("test_model.py", result)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify file contents
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("class TestModel(BaseModel)", content)
            self.assertIn("name: str", content)
            self.assertIn("age: int", content)

    def test_json_data_as_valid_json_string(self):
        """
        GIVEN a valid JSON string representation
        WHEN json_to_pydantic_model is called with the string
        THEN expect:
            - Function executes successfully
            - Returns success message with correct output path
            - Generated file exists at specified location
        """
        output_path = os.path.join(self.temp_dir, "string_model.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_json_string,
            output_file_path=output_path,
            model_name="StringModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("class StringModel(BaseModel)", content)

    def test_json_data_as_valid_file_path(self):
        """
        GIVEN a valid path to an existing JSON file
        WHEN json_to_pydantic_model is called with the file path
        THEN expect:
            - Function executes successfully
            - Returns success message with correct output path
            - Generated file exists at specified location
        """
        # Create test JSON file
        json_file_path = os.path.join(self.temp_dir, "test_data.json")
        with open(json_file_path, 'w') as f:
            json.dump(self.test_data, f)
        
        output_path = os.path.join(self.temp_dir, "file_model.py")
        
        result = json_to_pydantic_model(
            json_data=json_file_path,
            output_file_path=output_path,
            model_name="FileModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))

    def test_json_data_invalid_type(self):
        """
        GIVEN json_data of an unsupported type (e.g., list, int, None)
        WHEN json_to_pydantic_model is called
        THEN expect TypeError to be raised
        """
        output_path = os.path.join(self.temp_dir, "invalid.py")
        
        # Test with list
        with self.assertRaises(TypeError):
            json_to_pydantic_model([1, 2, 3], output_path)
        
        # Test with int
        with self.assertRaises(TypeError):
            json_to_pydantic_model(123, output_path)
        
        # Test with None
        with self.assertRaises(TypeError):
            json_to_pydantic_model(None, output_path)

    def test_json_data_malformed_json_string(self):
        """
        GIVEN a malformed JSON string (e.g., missing quotes, extra commas)
        WHEN json_to_pydantic_model is called
        THEN expect _InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "malformed.py")
        
        malformed_json_strings = [
            '{"name": "John", "age":}',  # Missing value
            '{"name": "John",, "age": 30}',  # Extra comma
            '{name: "John", "age": 30}',  # Missing quotes on key
            '{"name": "John" "age": 30}',  # Missing comma
        ]

        for malformed_json in malformed_json_strings:
            with self.assertRaises(_InvalidJSONError):  # Should raise _InvalidJSONError
                json_to_pydantic_model(malformed_json, output_path)

    def test_json_data_empty_dict(self):
        """
        GIVEN an empty dictionary {}
        WHEN json_to_pydantic_model is called
        THEN expect _InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "empty.py")
        
        with self.assertRaises(_InvalidJSONError):  # Should raise _InvalidJSONError
            json_to_pydantic_model({}, output_path)

    def test_json_data_empty_json_string(self):
        """
        GIVEN an empty JSON string "{}"
        WHEN json_to_pydantic_model is called
        THEN expect _InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "empty_string.py")
        
        with self.assertRaises(_InvalidJSONError):  # Should raise _InvalidJSONError
            json_to_pydantic_model("{}", output_path)

    def test_json_data_nonexistent_file_path(self):
        """
        GIVEN a path to a non-existent JSON file
        WHEN json_to_pydantic_model is called
        THEN expect _InvalidJSONError to be raised
        """
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        output_path = os.path.join(self.temp_dir, "output.py")

        with self.assertRaises(_InvalidJSONError):  # Should raise _InvalidJSONError
            json_to_pydantic_model(nonexistent_path, output_path)

if __name__ == '__main__':
    unittest.main()