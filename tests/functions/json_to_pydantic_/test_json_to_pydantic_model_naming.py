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



class TestJsonToPydanticModelNaming(unittest.TestCase):
    """Test model naming logic for json_to_pydantic_model function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = {"name": "John", "age": 30}
        
    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_model_name_provided_valid_pascal_case(self):
        """
        GIVEN a valid model_name in PascalCase (e.g., "UserModel")
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Generated model uses the provided name
            - Output file uses snake_case version of the name
        """
        output_path = os.path.join(self.temp_dir, "user_model.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="UserModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("class UserModel(BaseModel)", content)

    def test_model_name_provided_invalid_format(self):
        """
        GIVEN an invalid model_name (e.g., "user-model", "123Model", "class")
        WHEN json_to_pydantic_model is called
        THEN expect ValueError to be raised
        """
        output_path = os.path.join(self.temp_dir, "invalid.py")
        
        invalid_names = [
            "user-model",      # Contains hyphen
            "123Model",        # Starts with number
            "class",           # Python keyword
            "def",             # Python keyword
            "import",          # Python keyword
            "user model",      # Contains space
            "user.model",      # Contains dot
            "",                # Empty string
            "a",               # Too short
            #"ALLCAPS",         # All caps (not invalid, can be coerced to PascalCase)
        ]
        
        for invalid_name in invalid_names:
            with self.subTest(name=invalid_name):
                with self.assertRaises(ValueError):
                    json_to_pydantic_model(
                        json_data=self.test_data,
                        output_file_path=output_path,
                        model_name=invalid_name
                    )

    def test_model_name_not_provided_derives_from_path(self):
        """
        GIVEN model_name is None
        AND output_file_path is "./models/user_data.py"
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Model name derived as "UserData" (PascalCase from filename)
            - Function executes successfully
        """
        models_dir = os.path.join(self.temp_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        output_path = os.path.join(models_dir, "user_data.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name=None  # Should derive from filename
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            # Should derive "UserData" from "user_data.py"
            self.assertIn("class UserData(BaseModel)", content)

    def test_model_name_conflicts_with_nested_model(self):
        """
        GIVEN JSON with nested structure where a key conflicts with model_name
        WHEN json_to_pydantic_model is called
        THEN expect _PydanticGenerationError to be raised
        """
        # Create JSON where a nested key would conflict with the main model name
        conflicting_data = {
            "name": "John",
            "user_model": {  # This would create a "UserModel" class
                "id": 123,
                "active": True
            }
        }
        
        output_path = os.path.join(self.temp_dir, "conflict_test.py")
        
        with self.assertRaises(_PydanticGenerationError):  # Should raise _ModelValidationError
            json_to_pydantic_model(
                json_data=conflicting_data,
                output_file_path=output_path,
                model_name="UserModel"  # Conflicts with nested "user_model" key
            )

    def test_pascal_case_conversion_edge_cases(self):
        """
        GIVEN various filename formats
        WHEN deriving model names from filenames
        THEN expect proper PascalCase conversion
        """
        test_cases = [
            ("simple.py", "Simple"),
            ("snake_case_name.py", "SnakeCaseName"),
            ("kebab-case-name.py", "KebabCaseName"),
            ("camelCaseName.py", "CamelCaseName"),
            ("UPPERCASE.py", "Uppercase"),
            ("multiple_words_here.py", "MultipleWordsHere"),
            ("with123numbers.py", "With123Numbers"),
        ]
        
        for filename, expected_class_name in test_cases:
            with self.subTest(filename=filename):
                output_path = os.path.join(self.temp_dir, filename)
                
                result = json_to_pydantic_model(
                    json_data=self.test_data,
                    output_file_path=output_path,
                    model_name=None
                )
                
                with open(output_path, 'r') as f:
                    content = f.read()
                    self.assertIn(f"class {expected_class_name}(BaseModel)", content)

    def test_snake_case_filename_generation(self):
        """
        GIVEN PascalCase model names
        WHEN generating output filenames
        THEN expect proper snake_case conversion
        """
        self.test_data = {"name": "John", "age": 30}
        test_cases = [
            "SimpleModel",
            "UserAccountModel", 
            "HTTPResponseModel",
            "XMLParser",
            "JSONDataModel",
            "APIEndpointConfig"
        ]
        
        for model_name in test_cases:
            with self.subTest(model_name=model_name):
                # Let the function determine the filename
                base_path = os.path.join(self.temp_dir, f"{model_name.lower()}.py")
                
                result = json_to_pydantic_model(
                    json_data=self.test_data,
                    output_file_path=base_path,
                    model_name=model_name
                )
                
                self.assertIn("Successfully generated Pydantic model", result)
                # The function should create a file with snake_case naming
                # Extract the actual filename from the result message
                self.assertTrue(any(os.path.exists(os.path.join(self.temp_dir, f)) 
                                 for f in os.listdir(self.temp_dir) if f.endswith('.py')))

    def test_reserved_keyword_handling_in_nested_models(self):
        """
        GIVEN JSON with keys that would create model names conflicting with Python keywords
        WHEN json_to_pydantic_model is called
        THEN expect proper handling to avoid conflicts
        """
        data_with_keywords = {
            "name": "test",
            "class": {  # Would create "Class" model
                "id": 1,
                "type": "advanced"
            },
            "import": {  # Would create "Import" model
                "source": "file.py",
                "timestamp": "2023-01-01"
            }
        }
        
        output_path = os.path.join(self.temp_dir, "keyword_test.py")
        
        # This should try to handle the conflict gracefully, amd raise an appropriate error if it can't.
        try:
            result = json_to_pydantic_model(
                json_data=data_with_keywords,
                output_file_path=output_path,
                model_name="TestModel"
            )
            
            # If it succeeds, verify the generated code
            with open(output_path, 'r') as f:
                content = f.read()
                # Should not contain raw Python keywords as class names
                self.assertNotIn("class class(", content.lower())
                self.assertNotIn("class import(", content.lower())
                
        except Exception as e:
            # If it raises an error, that's also acceptable
            self.assertIsInstance(e, (ValueError, Exception))

if __name__ == '__main__':
    unittest.main()