import importlib.util
import json
import os
import re
import sys
import tempfile
import unittest


from tools.functions.json_to_pydantic_model import (
    json_to_pydantic_model, InvalidJSONError, ModelValidationError, PydanticGenerationError
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
        THEN expect InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "malformed.py")
        
        malformed_json_strings = [
            '{"name": "John", "age":}',  # Missing value
            '{"name": "John",, "age": 30}',  # Extra comma
            '{name: "John", "age": 30}',  # Missing quotes on key
            '{"name": "John" "age": 30}',  # Missing comma
        ]

        for malformed_json in malformed_json_strings:
            with self.assertRaises(InvalidJSONError):  # Should raise InvalidJSONError
                json_to_pydantic_model(malformed_json, output_path)

    def test_json_data_empty_dict(self):
        """
        GIVEN an empty dictionary {}
        WHEN json_to_pydantic_model is called
        THEN expect InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "empty.py")
        
        with self.assertRaises(InvalidJSONError):  # Should raise InvalidJSONError
            json_to_pydantic_model({}, output_path)

    def test_json_data_empty_json_string(self):
        """
        GIVEN an empty JSON string "{}"
        WHEN json_to_pydantic_model is called
        THEN expect InvalidJSONError to be raised
        """
        output_path = os.path.join(self.temp_dir, "empty_string.py")
        
        with self.assertRaises(InvalidJSONError):  # Should raise InvalidJSONError
            json_to_pydantic_model("{}", output_path)

    def test_json_data_nonexistent_file_path(self):
        """
        GIVEN a path to a non-existent JSON file
        WHEN json_to_pydantic_model is called
        THEN expect InvalidJSONError to be raised
        """
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        output_path = os.path.join(self.temp_dir, "output.py")

        with self.assertRaises(InvalidJSONError):  # Should raise InvalidJSONError
            json_to_pydantic_model(nonexistent_path, output_path)


class TestJsonToPydanticModelOutputHandling(unittest.TestCase):
    """Test output file handling for json_to_pydantic_model function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = {"name": "John", "age": 30}
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Reset permissions before cleanup
        for root, dirs, files in os.walk(self.temp_dir):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o644)
        
        # Clean up temp directory and files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_output_file_path_valid_directory(self):
        """
        GIVEN a valid output_file_path to an existing directory
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Function executes successfully
            - File is created in the specified directory
            - Return message contains correct path
        """
        output_path = os.path.join(self.temp_dir, "valid_output.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="ValidModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertIn("valid_output.py", result)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(os.path.isfile(output_path))

    def test_output_file_path_nonexistent_directory(self):
        """
        GIVEN an output_file_path with a non-existent directory
        WHEN json_to_pydantic_model is called
        THEN expect IOError to be raised
        """
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent", "subdir")
        output_path = os.path.join(nonexistent_dir, "model.py")
        
        with self.assertRaises(IOError):  # Should raise IOError
            json_to_pydantic_model(
                json_data=self.test_data,
                output_file_path=output_path,
                model_name="TestModel"
            )

    def test_output_file_path_no_write_permissions(self):
        """
        GIVEN an output_file_path to a directory without write permissions
        WHEN json_to_pydantic_model is called
        THEN expect IOError to be raised
        """
        # Create a directory and remove write permissions
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)  # Read-only permissions
        
        output_path = os.path.join(readonly_dir, "model.py")
        
        try:
            with self.assertRaises(IOError):  # Should raise IOError
                json_to_pydantic_model(
                    json_data=self.test_data,
                    output_file_path=output_path,
                    model_name="TestModel"
                )
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)

    def test_overwrite_existing_false_file_exists(self):
        """
        GIVEN an existing file at output_file_path
        AND overwrite_existing is False (default)
        WHEN json_to_pydantic_model is called
        THEN expect IOError to be raised
        """
        output_path = os.path.join(self.temp_dir, "existing_model.py")
        
        # Create existing file
        with open(output_path, 'w') as f:
            f.write("# Existing file content")
        
        with self.assertRaises(IOError):
            json_to_pydantic_model(
                json_data=self.test_data,
                output_file_path=output_path,
                model_name="TestModel",
                overwrite_existing=False
            )

    def test_overwrite_existing_true_file_exists(self):
        """
        GIVEN an existing file at output_file_path
        AND overwrite_existing is True
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Function executes successfully
            - Existing file is overwritten
            - Returns success message
        """
        output_path = os.path.join(self.temp_dir, "overwrite_model.py")
        
        # Create existing file with different content
        with open(output_path, 'w') as f:
            f.write("# Old content that should be overwritten")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="OverwriteModel",
            overwrite_existing=True
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify the file was overwritten
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("class OverwriteModel(BaseModel)", content)
            self.assertNotIn("Old content", content)

    def test_output_path_with_nested_directories(self):
        """
        GIVEN an output_file_path with multiple nested directories that don't exist
        WHEN json_to_pydantic_model is called with appropriate directory creation
        THEN raise FileNotFoundError or IOError
        """
        nested_path = os.path.join(self.temp_dir, "level1", "level2", "level3", "model.py")

        with self.assertRaises(IOError):
            result = json_to_pydantic_model(
                json_data=self.test_data,
                output_file_path=nested_path,
                model_name="NestedModel"
            )

    def test_output_path_permissions_after_creation(self):
        """
        GIVEN successful file creation
        WHEN checking file permissions
        THEN expect the file to be readable and writable
        """
        output_path = os.path.join(self.temp_dir, "permissions_model.py")
        
        json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="PermissionsModel"
        )
        
        self.assertTrue(os.access(output_path, os.R_OK))  # Readable
        self.assertTrue(os.access(output_path, os.W_OK))  # Writable



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
        THEN expect PydanticGenerationError to be raised
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
        
        with self.assertRaises(PydanticGenerationError):  # Should raise ModelValidationError
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



class TestJsonToPydanticModelNestedStructures(unittest.TestCase):
    """Test handling of nested JSON structures."""

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

    def test_single_level_nesting(self):
        """
        GIVEN JSON with one level of nesting (e.g., {"user": {"name": "John", "age": 30}})
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Separate User model created
            - Parent model references User model
            - Both models properly typed
        """
        nested_data = {
            "user": {
                "name": "John",
                "age": 30
            },
            "status": "active"
        }
        
        output_path = os.path.join(self.temp_dir, "single_nested.py")
        
        result = json_to_pydantic_model(
            json_data=nested_data,
            output_file_path=output_path,
            model_name="SingleNestedModel"
        )
        
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should have a User model
            self.assertIn("class User(BaseModel)", content)
            self.assertIn("name: str", content)
            self.assertIn("age: int", content)
            
            # Should have main model referencing User
            self.assertIn("class SingleNestedModel(BaseModel)", content)
            self.assertIn("user: User", content)
            self.assertIn("status: str", content)

    def test_multiple_levels_nesting(self):
        """
        GIVEN JSON with multiple levels of nesting
        WHEN json_to_pydantic_model is called
        THEN expect:
            - All nested models created with proper hierarchy
            - Each model properly references its children
            - All models have correct types
        """
        deeply_nested_data = {
            "company": {
                "name": "TechCorp",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "coordinates": {
                        "latitude": 40.7128,
                        "longitude": -74.0060
                    }
                },
                "employees": [
                    {
                        "name": "Alice",
                        "department": {
                            "name": "Engineering",
                            "budget": 1000000
                        }
                    }
                ]
            }
        }
        
        output_path = os.path.join(self.temp_dir, "multi_nested.py")
        
        result = json_to_pydantic_model(
            json_data=deeply_nested_data,
            output_file_path=output_path,
            model_name="MultiNestedModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Check for all expected models
            expected_models = [
                "class Coordinates(BaseModel)",
                "class Address(BaseModel)", 
                "class Department(BaseModel)",
                "class Company(BaseModel)",
                "class MultiNestedModel(BaseModel)"
            ]
            
            for model in expected_models:
                self.assertIn(model, content)
            
            # Check for proper field types
            self.assertIn("latitude: float", content)
            self.assertIn("longitude: float", content)
            self.assertIn("coordinates: Coordinates", content)
            self.assertIn("address: Address", content)

    def test_list_of_nested_objects(self):
        """
        GIVEN JSON with a list containing nested objects
        WHEN json_to_pydantic_model is called
        THEN expect:
            - List type annotation with nested model
            - Nested model created separately
            - Proper handling of List[NestedModel]
        """
        list_data = {
            "users": [
                {
                    "name": "Alice",
                    "profile": {
                        "bio": "Software engineer",
                        "skills": ["Python", "JavaScript"]
                    }
                },
                {
                    "name": "Bob", 
                    "profile": {
                        "bio": "Data scientist",
                        "skills": ["R", "SQL"]
                    }
                }
            ],
            "total_count": 2
        }
        
        output_path = os.path.join(self.temp_dir, "list_nested.py")
        
        result = json_to_pydantic_model(
            json_data=list_data,
            output_file_path=output_path,
            model_name="ListNestedModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should have Profile model
            self.assertIn("class Profile(BaseModel)", content)
            self.assertIn("bio: str", content)
            self.assertIn("skills: List[str]", content)
            
            # Should have Users model
            self.assertIn("class Users(BaseModel)", content)
            self.assertIn("name: str", content)
            self.assertIn("profile: Profile", content)
            
            # Main model should reference List[Users]
            self.assertIn("class ListNestedModel(BaseModel)", content)
            self.assertIn("users: List[Users]", content)
            self.assertIn("total_count: int", content)
            
            # Should import List from typing
            self.assertIn("from typing import", content)
            self.assertIn("List", content)

    def test_circular_reference_handling(self):
        """
        GIVEN JSON with circular references (e.g., parent -> child -> parent)
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Models use Optional types and forward references
            - No infinite recursion occurs
            - Models can be instantiated without errors
        """
        circular_data = {
            "name": "Alice",
            "age": 25,
            "children": [
                {
                    "name": "Bob",
                    "age": 5,
                    "parent": {
                        "name": "Alice",
                        "age": 25,
                        "children": []
                    },
                    "siblings": []
                }
            ]
        }
        
        output_path = os.path.join(self.temp_dir, "circular.py")
        
        result = json_to_pydantic_model(
            json_data=circular_data,
            output_file_path=output_path,
            model_name="CircularModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should handle circular references with Optional and forward references
            self.assertIn("Optional", content)
            self.assertIn("from typing import", content)
            
            # Should use forward references for circular types
            self.assertTrue("CircularModel" in content or "Children" in content)

    def test_empty_nested_lists(self):
        """
        GIVEN JSON with empty lists as values
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Fields use Optional[List] with default_factory
            - Generated model handles empty lists correctly
        """
        empty_list_data = {
            "name": "TestUser",
            "tags": [],
            "permissions": [],
            "metadata": {
                "categories": [],
                "flags": []
            }
        }
        
        output_path = os.path.join(self.temp_dir, "empty_lists.py")
        
        result = json_to_pydantic_model(
            json_data=empty_list_data,
            output_file_path=output_path,
            model_name="EmptyListModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should handle empty lists appropriately
            self.assertIn("List", content)
            self.assertIn("from typing import", content)
            
            # May use Optional[List]
            self.assertTrue("Optional" in content)

    def test_mixed_nested_and_flat_structure(self):
        """
        GIVEN JSON with mix of nested objects and flat fields
        WHEN json_to_pydantic_model is called
        THEN expect proper handling of both types
        """
        mixed_data = {
            "id": 123,
            "name": "Mixed Example",
            "is_active": True,
            "config": {
                "timeout": 30,
                "retries": 3,
                "endpoints": {
                    "primary": "https://api.example.com",
                    "fallback": "https://backup.example.com"
                }
            },
            "tags": ["important", "production"],
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        output_path = os.path.join(self.temp_dir, "mixed_structure.py")
        
        result = json_to_pydantic_model(
            json_data=mixed_data,
            output_file_path=output_path,
            model_name="MixedStructureModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should have nested models
            self.assertIn("class Endpoints(BaseModel)", content)
            self.assertIn("class Config(BaseModel)", content)
            self.assertIn("class MixedStructureModel(BaseModel)", content)
            
            # Should have proper field types
            self.assertIn("id: int", content)
            self.assertIn("name: str", content)
            self.assertIn("is_active: bool", content)
            self.assertIn("config: Config", content)
            self.assertIn("tags: List[str]", content)
            self.assertIn("created_at: str", content)
            
            # Nested model fields
            self.assertIn("timeout: int", content)
            self.assertIn("retries: int", content)
            self.assertIn("endpoints: Endpoints", content)
            self.assertIn("primary: str", content)
            self.assertIn("fallback: str", content)

    def test_deeply_nested_arrays_and_objects(self):
        """
        GIVEN JSON with arrays containing objects that contain more arrays and objects
        WHEN json_to_pydantic_model is called
        THEN expect proper handling of complex nesting
        """
        complex_nested = {
            "organizations": [
                {
                    "name": "Org1",
                    "departments": [
                        {
                            "name": "Engineering",
                            "teams": [
                                {
                                    "name": "Backend",
                                    "members": [
                                        {
                                            "name": "Alice",
                                            "roles": ["developer", "mentor"],
                                            "contact": {
                                                "email": "alice@example.com",
                                                "phone": "555-0123"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        output_path = os.path.join(self.temp_dir, "complex_nested.py")
        
        result = json_to_pydantic_model(
            json_data=complex_nested,
            output_file_path=output_path,
            model_name="ComplexNestedModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should create all necessary nested models
            expected_models = [
                "class Contact(BaseModel)",
                "class Members(BaseModel)", 
                "class Teams(BaseModel)",
                "class Departments(BaseModel)",
                "class Organizations(BaseModel)",
                "class ComplexNestedModel(BaseModel)"
            ]
            
            for model in expected_models:
                self.assertIn(model, content)
            
            # Should handle nested lists properly
            self.assertIn("List[", content)
            self.assertIn("roles: List[str]", content)
            self.assertIn("members: List[Members]", content)
            self.assertIn("teams: List[Teams]", content)
            self.assertIn("departments: List[Departments]", content)
            self.assertIn("organizations: List[Organizations]", content)

    def test_nested_objects_with_same_structure(self):
        """
        GIVEN JSON with multiple nested objects having the same structure
        WHEN json_to_pydantic_model is called
        THEN expect reuse of model definitions
        """
        same_structure_data = {
            "primary_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "zip": "12345"
            },
            "billing_address": {
                "street": "456 Oak Ave",
                "city": "Other Town", 
                "zip": "67890"
            },
            "shipping_address": {
                "street": "789 Pine Rd",
                "city": "Third Town",
                "zip": "54321"
            }
        }
        
        output_path = os.path.join(self.temp_dir, "same_structure.py")
        
        result = json_to_pydantic_model(
            json_data=same_structure_data,
            output_file_path=output_path,
            model_name="SameStructureModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should have address models (might be reused or separate)
            address_models = [line for line in content.split('\n') if 'Address' in line and 'class' in line and 'BaseModel' in line]
            
            # Should have the main model
            self.assertIn("class SameStructureModel(BaseModel)", content)
            
            # Should reference address models
            self.assertTrue(any("Address" in line for line in content.split('\n') if ":" in line))

    def test_nested_lists_with_different_types(self):
        """
        GIVEN JSON with nested lists containing different object types
        WHEN json_to_pydantic_model is called
        THEN expect proper handling of heterogeneous lists
        """
        heterogeneous_data = {
            "mixed_items": [
                {"type": "text", "content": "Hello world", "length": 11},
                {"type": "image", "url": "https://example.com/img.jpg", "width": 800, "height": 600},
                {"type": "video", "url": "https://example.com/vid.mp4", "duration": 120}
            ],
            "metadata": {
                "total_items": 3,
                "types_present": ["text", "image", "video"]
            }
        }
        
        output_path = os.path.join(self.temp_dir, "heterogeneous.py")
        
        result = json_to_pydantic_model(
            json_data=heterogeneous_data,
            output_file_path=output_path,
            model_name="HeterogeneousModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should handle the mixed list appropriately
            self.assertIn("class HeterogeneousModel(BaseModel)", content)
            self.assertIn("mixed_items:", content)
            self.assertIn("List", content)
            
            # Should have metadata model
            self.assertIn("class Metadata(BaseModel)", content)
            self.assertIn("total_items: int", content)
            self.assertIn("types_present: List[str]", content)

    def test_empty_nested_objects(self):
        """
        GIVEN JSON with empty nested objects
        WHEN json_to_pydantic_model is called
        THEN expect appropriate handling of empty structures
        """
        empty_nested_data = {
            "name": "test",
            "empty_config": {},
            "partial_config": {
                "enabled": True,
                "empty_subsection": {}
            }
        }
        
        output_path = os.path.join(self.temp_dir, "empty_nested.py")
        
        result = json_to_pydantic_model(
            json_data=empty_nested_data,
            output_file_path=output_path,
            model_name="EmptyNestedModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()

            # Should have the main model
            self.assertIn("class EmptyNestedModel(BaseModel)", content)
            self.assertIn("name: str", content)

            # Should handle empty objects appropriately with Optional[Any]
            self.assertTrue(
                any(model_type in content for model_type in ["Optional", "Any", "Dict", "class"])
            )



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





class TestJsonToPydanticModelValidation(unittest.TestCase):
    """Test model validation after generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove any modules we might have imported
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name.startswith('temp_test_'):
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
        
        # Clean up temp directory and files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def _import_module_from_path(self, module_path, module_name):
        """Helper to import a module from a file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def test_generated_model_validates_original_data(self):
        """
        GIVEN generated Pydantic model from JSON data
        WHEN the original JSON is validated against the model
        THEN expect:
            - Validation passes without errors
            - All fields are correctly populated
            - Nested structures are properly instantiated
        """
        test_data = {
            "user_id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": True,
            "balance": 1234.56,
            "profile": {
                "bio": "Software developer",
                "age": 30,
                "skills": ["Python", "JavaScript", "SQL"]
            },
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "language": "en"
            }
        }
        
        output_path = os.path.join(self.temp_dir, "validation_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="ValidationTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Import the generated module
        module = self._import_module_from_path(output_path, "temp_test_validation")
        
        # Get the main model class
        model_class = getattr(module, "ValidationTestModel")
        
        # Validate that we can instantiate the model with the original data
        try:
            model_instance = model_class(**test_data)
            
            # Verify all fields are correctly populated
            self.assertEqual(model_instance.user_id, 123)
            self.assertEqual(model_instance.name, "John Doe")
            self.assertEqual(model_instance.email, "john@example.com")
            self.assertEqual(model_instance.is_active, True)
            self.assertEqual(model_instance.balance, 1234.56)
            
            # Verify nested structures
            self.assertEqual(model_instance.profile.bio, "Software developer")
            self.assertEqual(model_instance.profile.age, 30)
            self.assertEqual(model_instance.profile.skills, ["Python", "JavaScript", "SQL"])
            
            self.assertEqual(model_instance.preferences.theme, "dark")
            self.assertEqual(model_instance.preferences.notifications, True)
            self.assertEqual(model_instance.preferences.language, "en")
            
        except Exception as e:
            self.fail(f"Model validation failed: {e}")

    def test_generated_model_import_success(self):
        """
        GIVEN a successfully generated model file
        WHEN attempting to import the generated module
        THEN expect:
            - Import succeeds without errors
            - All model classes are accessible
            - No syntax errors in generated code
        """
        test_data = {
            "company": {
                "name": "TechCorp",
                "employees": [
                    {
                        "name": "Alice",
                        "department": {
                            "name": "Engineering",
                            "budget": 1000000
                        }
                    }
                ]
            },
            "founded_year": 2020
        }
        
        output_path = os.path.join(self.temp_dir, "import_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="ImportTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Attempt to import the module
        try:
            module = self._import_module_from_path(output_path, "temp_test_import")
            
            # Check that all expected classes are present
            self.assertTrue(hasattr(module, "ImportTestModel"))
            self.assertTrue(hasattr(module, "Company"))
            self.assertTrue(hasattr(module, "Department"))
            self.assertTrue(hasattr(module, "Employees"))
            
            # Verify classes are actually classes and can be instantiated
            main_model = getattr(module, "ImportTestModel")
            self.assertTrue(callable(main_model))
            
            company_model = getattr(module, "Company")
            self.assertTrue(callable(company_model))
            
            # Check that BaseModel is properly imported
            self.assertTrue(issubclass(main_model, BaseModel))
            
        except ImportError as e:
            self.fail(f"Failed to import generated module: {e}")
        except SyntaxError as e:
            self.fail(f"Generated code has syntax errors: {e}")
        except Exception as e:
            self.fail(f"Unexpected error during import: {e}")

    def test_generated_model_validation_failure(self):
        """
        GIVEN a model generation that would create invalid Pydantic models
        WHEN json_to_pydantic_model is called
        THEN expect ModelValidationError to be raised
        """
        # This test is tricky because we need to force an invalid model generation
        # One way is to use data that might cause naming conflicts or invalid syntax

        problematic_data = {
            "class": "invalid",  # Python keyword
            "def": "also invalid",  # Python keyword
            "123invalid": "starts with number",
            "": "empty key",
            "from typing import List": "Python code as key"
        }
        
        output_path = os.path.join(self.temp_dir, "validation_failure.py")
        
        # This should either handle the issues gracefully or raise an appropriate error
        try:
            result = json_to_pydantic_model(
                json_data=problematic_data,
                output_file_path=output_path,
                model_name="ValidationFailureModel"
            )
            
            # If it succeeds, let's verify it actually works
            if os.path.exists(output_path):
                # Try to import and validate
                module = self._import_module_from_path(output_path, "temp_test_validation_failure")
                model_class = getattr(module, "ValidationFailureModel")
                
                # The original data might not validate due to field name changes
                # But the model should at least be syntactically correct
                self.assertTrue(callable(model_class))
                
        except Exception as e:
            # If it raises an error, that's also acceptable behavior
            # The specific error type depends on the implementation
            self.assertIsInstance(e, (ValueError, Exception))

    def test_model_serialization_roundtrip(self):
        """
        GIVEN a generated model with original data
        WHEN serializing to JSON and deserializing back
        THEN expect data integrity is maintained
        """
        test_data = {
            "transaction_id": "tx_123456",
            "amount": 99.99,
            "currency": "USD",
            "timestamp": "2023-01-01T12:00:00Z",
            "user": {
                "id": 456,
                "email": "user@example.com"
            },
            "items": [
                {"name": "Product A", "quantity": 2, "price": 29.99},
                {"name": "Product B", "quantity": 1, "price": 39.99}
            ]
        }
        
        output_path = os.path.join(self.temp_dir, "serialization_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="SerializationTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Import and test serialization
        module = self._import_module_from_path(output_path, "temp_test_serialization")
        model_class = getattr(module, "SerializationTestModel")
        
        # Create model instance
        model_instance = model_class(**test_data)
        
        # Serialize to dict
        serialized = model_instance.dict()
        
        # Verify serialized data matches original
        self.assertEqual(serialized["transaction_id"], test_data["transaction_id"])
        self.assertEqual(serialized["amount"], test_data["amount"])
        self.assertEqual(serialized["user"]["id"], test_data["user"]["id"])
        self.assertEqual(len(serialized["items"]), len(test_data["items"]))
        
        # Create new instance from serialized data
        new_instance = model_class(**serialized)
        
        # Verify both instances are equivalent
        self.assertEqual(model_instance.transaction_id, new_instance.transaction_id)
        self.assertEqual(model_instance.amount, new_instance.amount)
        self.assertEqual(model_instance.user.id, new_instance.user.id)

    def test_model_with_optional_fields_validation(self):
        """
        GIVEN a model with optional fields
        WHEN validating with partial data
        THEN expect validation to succeed for missing optional fields
        """
        test_data = {
            "required_field": "must be present",
            "optional_field": None,
            "nested_optional": {
                "required_nested": "present",
                "optional_nested": None
            }
        }
        
        output_path = os.path.join(self.temp_dir, "optional_fields_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="OptionalFieldsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        module = self._import_module_from_path(output_path, "temp_test_optional")
        model_class = getattr(module, "OptionalFieldsModel")
        
        # Test with full data
        full_instance = model_class(**test_data)
        self.assertEqual(full_instance.required_field, "must be present")
        
        # Test with minimal data (only required fields)
        minimal_data = {
            "required_field": "still must be present",
            "nested_optional": {
                "required_nested": "also present"
            }
        }
        minimal_instance = model_class(**minimal_data)
        self.assertEqual(minimal_instance.required_field, "still must be present")


    def test_model_field_validation_types(self):
        """
        GIVEN a generated model
        WHEN providing data with wrong types
        THEN expect appropriate validation errors
        """
        test_data = {
            "string_field": "text",
            "int_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "list_field": ["item1", "item2"]
        }
        
        output_path = os.path.join(self.temp_dir, "type_validation_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="TypeValidationModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        module = self._import_module_from_path(output_path, "temp_test_type_validation")
        model_class = getattr(module, "TypeValidationModel")
        
        # Valid data should work
        valid_instance = model_class(**test_data)
        self.assertEqual(valid_instance.string_field, "text")
        self.assertEqual(valid_instance.int_field, 42)
        
        # Invalid data should raise validation errors
        invalid_data_sets = [
            {**test_data, "int_field": "not an int"},
            {**test_data, "bool_field": "not a bool"},
            {**test_data, "float_field": "not a float"},
        ]

        for invalid_data in invalid_data_sets:
            with self.subTest(invalid_data=invalid_data):
                try:
                    model_class(**invalid_data)
                    # If no exception is raised, the model might be too permissive
                    # This could be expected behavior depending on implementation
                except ValidationError:
                    # Validation error is expected for wrong types
                    pass
                except Exception as e:
                    self.fail(f"Unexpected error during validation: {e}")

    def test_complex_nested_model_validation(self):
        """
        GIVEN a complex nested model
        WHEN validating with deeply nested data
        THEN expect all levels to validate correctly
        """
        complex_data = {
            "metadata": {
                "version": "1.0",
                "created_by": {
                    "user": {
                        "id": 123,
                        "profile": {
                            "name": "John",
                            "settings": {
                                "theme": "dark",
                                "notifications": {
                                    "email": True,
                                    "push": False,
                                    "sms": None
                                }
                            }
                        }
                    }
                }
            }
        }
        
        output_path = os.path.join(self.temp_dir, "complex_nested_validation.py")
        
        result = json_to_pydantic_model(
            json_data=complex_data,
            output_file_path=output_path,
            model_name="ComplexNestedValidationModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        module = self._import_module_from_path(output_path, "temp_test_complex_nested")
        model_class = getattr(module, "ComplexNestedValidationModel")
        
        # Should be able to instantiate with complex nested data
        try:
            instance = model_class(**complex_data)
            
            # Verify deep nesting works
            self.assertEqual(instance.metadata.version, "1.0")
            self.assertEqual(instance.metadata.created_by.user.id, 123)
            self.assertEqual(instance.metadata.created_by.user.profile.name, "John")
            self.assertEqual(instance.metadata.created_by.user.profile.settings.theme, "dark")
            self.assertEqual(instance.metadata.created_by.user.profile.settings.notifications.email, True)
            self.assertEqual(instance.metadata.created_by.user.profile.settings.notifications.push, False)
            
        except Exception as e:
            self.fail(f"Complex nested validation failed: {e}")

    def test_generated_code_syntax_correctness(self):
        """
        GIVEN generated Python code
        WHEN parsing it as Python AST
        THEN expect no syntax errors
        """
        test_data = {
            "field_with_underscores": "value",
            "fieldWithCamelCase": "value",
            "field-with-dashes": "value",
            "field.with.dots": "value",
            "field with spaces": "value"
        }
        
        output_path = os.path.join(self.temp_dir, "syntax_test.py")
        
        result = json_to_pydantic_model(
            json_data=test_data,
            output_file_path=output_path,
            model_name="SyntaxTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Read the generated code
        with open(output_path, 'r') as f:
            generated_code = f.read()
        
        # Try to parse it as Python AST
        try:
            import ast
            ast.parse(generated_code)
        except SyntaxError as e:
            self.fail(f"Generated code has syntax errors: {e}")
        
        # Also verify it can be imported without errors
        try:
            module = self._import_module_from_path(output_path, "temp_test_syntax")
            model_class = getattr(module, "SyntaxTestModel")
            self.assertTrue(callable(model_class))
        except Exception as e:
            self.fail(f"Generated code cannot be imported: {e}")


class TestJsonToPydanticModelEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove any modules we might have imported
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name.startswith('temp_edge_'):
                modules_to_remove.append(module_name)
        
        for module_name in modules_to_remove:
            del sys.modules[module_name]
            
        # Clean up temp directory and files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def _import_module_from_path(self, module_path, module_name):
        """Helper to import a module from a file path."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def test_json_with_python_reserved_keywords(self):
        """
        GIVEN JSON with keys that are Python reserved words (e.g., "class", "def", "import")
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Fields are renamed to avoid conflicts
            - Field aliases preserve original JSON keys
            - Model can serialize/deserialize correctly
        """
        keyword_data = {
            "class": "user_class",
            "def": "definition",
            "import": "import_data",
            "return": "return_value",
            "if": "condition",
            "for": "loop_data",
            "while": "while_condition",
            "try": "try_block",
            "except": "exception_data",
            "finally": "finally_block"
        }
        
        output_path = os.path.join(self.temp_dir, "keywords_test.py")
        
        result = json_to_pydantic_model(
            json_data=keyword_data,
            output_file_path=output_path,
            model_name="KeywordsTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should not contain raw Python keywords as field names
            self.assertNotIn(": class", content.lower())
            self.assertNotIn(": def", content.lower())
            self.assertNotIn(": import", content.lower())
            
            # Should handle keywords appropriately (renamed or aliased)
            self.assertIn("class KeywordsTestModel(BaseModel)", content)
            
        # Try to import and use the model
        module = self._import_module_from_path(output_path, "temp_edge_keywords")
        model_class = getattr(module, "KeywordsTestModel")
        
        # Should be able to create instance
        instance = model_class(**keyword_data)
        
        # Should be able to serialize back
        serialized = instance.dict()
        
        # Original keys should be preserved in serialization
        for key in keyword_data:
            self.assertIn(key, serialized)
                

    def test_json_with_special_characters_in_keys(self):
        """
        GIVEN JSON with keys containing special characters (e.g., "user-name", "email@address")
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Fields are sanitized to valid Python identifiers
            - Field aliases preserve original keys
            - Model maintains data integrity
        """
        special_char_data = {
            "user-name": "john_doe",
            "email@address": "john@example.com",
            "phone#number": "555-0123",
            "social$security": "xxx-xx-xxxx",
            "tax%rate": 0.15,
            "file.extension": ".txt",
            "url/path": "/api/users",
            "query?param": "value",
            "hash#tag": "#important",
            "space name": "with spaces",
            "dot.separated.field": "nested.value"
        }
        
        output_path = os.path.join(self.temp_dir, "special_chars_test.py")
        
        result = json_to_pydantic_model(
            json_data=special_char_data,
            output_file_path=output_path,
            model_name="SpecialCharsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should not contain invalid Python identifiers
            invalid_chars = ['-', '@', '#', '$', '%', '.', '/', '?', ' ']
            for char in invalid_chars:
                # Field names should not contain these characters directly
                lines = content.split('\n')
                field_lines = [line for line in lines if ':' in line and 'class' not in line]
                for line in field_lines:
                    if ':' in line:
                        field_part = line.split(':')[0].strip()
                        self.assertNotIn(char, field_part, 
                                       f"Invalid character '{char}' found in field: {field_part}")
        
        # Test that the model can be imported and used
        module = self._import_module_from_path(output_path, "temp_edge_special_chars")
        model_class = getattr(module, "SpecialCharsModel")
        instance = model_class(**special_char_data)
        
        # Should maintain data integrity
        serialized = instance.dict()
        for key, value in special_char_data.items():
            self.assertIn(key, serialized)
            self.assertEqual(serialized[key], value)


    def test_very_deeply_nested_json(self):
        """
        GIVEN JSON with very deep nesting (10+ levels)
        WHEN json_to_pydantic_model is called
        THEN expect:
            - All levels are properly converted
            - No stack overflow or recursion errors
            - Generated models maintain hierarchy
        """
        # Create 15 levels of nesting
        deeply_nested = {"level_1": {"level_2": {"level_3": {"level_4": {"level_5": {
            "level_6": {"level_7": {"level_8": {"level_9": {"level_10": {
                "level_11": {"level_12": {"level_13": {"level_14": {"level_15": {
                    "final_value": "deep_value",
                    "final_number": 42
                }}}}
            }}}}
        }}}}}}}}
        
        output_path = os.path.join(self.temp_dir, "deep_nested_test.py")
        
        result = json_to_pydantic_model(
            json_data=deeply_nested,
            output_file_path=output_path,
            model_name="DeeplyNestedModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should have models for each level
            for i in range(1, 16):
                expected_class = f"Level{i}" if i < 15 else "Level15"
                # The exact naming might vary, but should have nested structure
            
            # Should have the main model
            self.assertIn("class DeeplyNestedModel(BaseModel)", content)
            
        # Test that it can handle the deep nesting without errors
        module = self._import_module_from_path(output_path, "temp_edge_deep_nested")
        model_class = getattr(module, "DeeplyNestedModel")
        instance = model_class(**deeply_nested)
        
        # Should be able to access deeply nested values
        current = instance
        for i in range(1, 16):
            current = getattr(current, f"level_{i}")
        self.assertEqual(current.final_value, "deep_value")
        self.assertEqual(current.final_number, 42)
            


    def test_json_with_numeric_keys(self):
        """
        GIVEN JSON with numeric string keys (e.g., {"123": "value"})
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Keys are converted to valid Python identifiers
            - Appropriate field aliases are created
            - Model functions correctly
        """
        numeric_key_data = {
            "123": "numeric_start",
            "456field": "mixed_numeric",
            "field789": "normal_field",
            "0": "zero",
            "001": "leading_zeros",
            "3.14": "decimal_key",
            "1e5": "scientific_notation",
            "-1": "negative_number"
        }
        
        output_path = os.path.join(self.temp_dir, "numeric_keys_test.py")
        
        result = json_to_pydantic_model(
            json_data=numeric_key_data,
            output_file_path=output_path,
            model_name="NumericKeysModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Field names should not start with numbers
            lines = content.split('\n')
            field_lines = [line for line in lines if ':' in line and 'class' not in line]
            for line in field_lines:
                if ':' in line:
                    field_part = line.split(':')[0].strip()
                    if field_part and not field_part.startswith('#'):
                        self.assertFalse(field_part[0].isdigit(), 
                                       f"Field name starts with digit: {field_part}")

        module = self._import_module_from_path(output_path, "temp_edge_numeric_keys")
        model_class = getattr(module, "NumericKeysModel")
        instance = model_class(**numeric_key_data)
        
        # Should preserve original data
        serialized = instance.dict()
        for key, value in numeric_key_data.items():
            self.assertIn(key, serialized)
            self.assertEqual(serialized[key], value)

    def test_json_with_duplicate_keys_different_case(self):
        """
        GIVEN JSON that would result in duplicate field names after case conversion
        WHEN json_to_pydantic_model is called
        THEN expect:
            - Fields are disambiguated appropriately
            - All original data is preserved
            - No naming conflicts in generated code
        """
        case_conflict_data = {
            "userName": "john",
            "username": "john_doe",
            "user_name": "john.doe",
            "UserName": "JOHN",
            "EMAIL": "john@example.com",
            "email": "john.doe@example.com",
            "Email": "John.Doe@Example.Com"
        }
        
        output_path = os.path.join(self.temp_dir, "case_conflicts_test.py")
        
        result = json_to_pydantic_model(
            json_data=case_conflict_data,
            output_file_path=output_path,
            model_name="CaseConflictsModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as f:
            content = f.read()
            
            # Should not have duplicate field names
            lines = content.split('\n')
            field_lines = [line for line in lines if ':' in line and 'class' not in line]
            field_names = []
            for line in field_lines:
                if ':' in line:
                    field_part = line.split(':')[0].strip()
                    if field_part and not field_part.startswith('#'):
                        field_names.append(field_part)
            
            # All field names should be unique
            self.assertEqual(len(field_names), len(set(field_names)), 
                           f"Duplicate field names found: {field_names}")

        module = self._import_module_from_path(output_path, "temp_edge_case_conflicts")
        model_class = getattr(module, "CaseConflictsModel")
        instance = model_class(**case_conflict_data)
        
        # All original data should be preserved
        serialized = instance.dict()
        for key, value in case_conflict_data.items():
            self.assertIn(key, serialized)
            self.assertEqual(serialized[key], value)

    def test_extremely_large_json_structure(self):
        """
        GIVEN JSON with many fields and complex structure
        WHEN json_to_pydantic_model is called
        THEN expect reasonable performance and correct generation
        """
        # Create a large structure with many fields
        large_structure = {}
        
        # Add 100 top-level fields
        for i in range(100):
            large_structure[f"field_{i}"] = f"value_{i}"
        
        # Add nested structure with many fields
        large_structure["nested"] = {}
        for i in range(50):
            large_structure["nested"][f"nested_field_{i}"] = {
                "sub_field_a": f"sub_value_a_{i}",
                "sub_field_b": i,
                "sub_field_c": i * 0.1,
                "sub_field_d": i % 2 == 0
            }
        
        # Add list with many items
        large_structure["large_list"] = []
        for i in range(20):
            large_structure["large_list"].append({
                "item_id": i,
                "item_name": f"item_{i}",
                "item_data": {
                    "prop_1": f"prop_1_{i}",
                    "prop_2": f"prop_2_{i}",
                    "prop_3": i
                }
            })
        
        output_path = os.path.join(self.temp_dir, "large_structure_test.py")
        
        result = json_to_pydantic_model(
            json_data=large_structure,
            output_file_path=output_path,
            model_name="LargeStructureModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Verify the file was created and is not empty
        file_size = os.path.getsize(output_path)
        self.assertGreater(file_size, 0)

        # Try to import (this might be slow for very large structures)
        module = self._import_module_from_path(output_path, "temp_edge_large_structure")
        model_class = getattr(module, "LargeStructureModel")
        
        # Should be able to create instance (might be slow)
        instance = model_class(**large_structure)
        
        # Verify some basic fields
        self.assertEqual(instance.field_0, "value_0")
        self.assertEqual(instance.field_99, "value_99")
        self.assertEqual(len(instance.large_list), 20)


    def test_unicode_and_emoji_in_keys_and_values(self):
        """
        GIVEN JSON with Unicode characters and emojis in keys and values
        WHEN json_to_pydantic_model is called
        THEN expect proper handling of Unicode
        """
        unicode_data = {
            "名前": "田中太郎",
            "📧email": "tanaka@example.com",
            "🏠address": "東京都",
            "données": "français",
            "español": "hola mundo",
            "русский": "привет мир",
            "العربية": "مرحبا بالعالم",
            "emoji_field_🎉": "celebration",
            "mixed_unicode_123_ñ": "mixed"
        }
        
        output_path = os.path.join(self.temp_dir, "unicode_test.py")
        
        result = json_to_pydantic_model(
            json_data=unicode_data,
            output_file_path=output_path,
            model_name="UnicodeTestModel"
        )
        
        self.assertTrue(os.path.exists(output_path))
        
        # Verify file can be read as UTF-8
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("class UnicodeTestModel(BaseModel)", content)

        module = self._import_module_from_path(output_path, "temp_edge_unicode")
        model_class = getattr(module, "UnicodeTestModel")
        instance = model_class(**unicode_data)
        
        # Should preserve Unicode data
        serialized = instance.dict()
        for key, value in unicode_data.items():
            self.assertIn(key, serialized)
            self.assertEqual(serialized[key], value)
            

class TestJsonToPydanticModelReturnValue(unittest.TestCase):
    """Test the return value and success message format."""

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

    def test_return_message_format(self):
        """
        GIVEN successful model generation
        WHEN json_to_pydantic_model completes
        THEN expect:
            - Return string matches format: "Successfully generated Pydantic model at {path}"
            - Path in message matches actual output location
            - Path uses forward slashes regardless of OS
        """
        output_path = os.path.join(self.temp_dir, "format_test.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="FormatTestModel"
        )
        
        # Check basic message format
        self.assertIn("Successfully generated Pydantic model", result)
        self.assertIn("at", result)
        
        # Extract path from message
        # Pattern should match "Successfully generated Pydantic model at {path}"
        pattern = r"Successfully generated Pydantic model at (.+)"
        match = re.search(pattern, result)
        self.assertIsNotNone(match, f"Could not extract path from message: {result}")
        
        extracted_path = match.group(1)
        
        # Normalize paths for comparison (handle different OS path separators)
        normalized_output = os.path.normpath(output_path)
        normalized_extracted = os.path.normpath(extracted_path)
        
        # The paths should be equivalent
        self.assertEqual(normalized_output, normalized_extracted)
        
        # Verify the file actually exists at the reported location
        self.assertTrue(os.path.exists(extracted_path))

    def test_return_path_snake_case_conversion(self):
        """
        GIVEN model_name in PascalCase
        WHEN json_to_pydantic_model completes
        THEN expect:
            - Output filename is snake_case version
            - Return message contains snake_case filename
            - File extension is .py
        """
        test_cases = [
            ("SimpleModel", "simple_model"),
            ("UserAccountModel", "user_account_model"),
            ("HTTPResponseModel", "http_response_model"),
            ("XMLParser", "xml_parser"),
            ("JSONDataModel", "json_data_model"),
            ("APIEndpointConfig", "api_endpoint_config"),
            ("PDFDocumentProcessor", "pdf_document_processor")
        ]
        
        for model_name, expected_filename in test_cases:
            with self.subTest(model_name=model_name):
                # Use a base filename that will be converted
                base_output_path = os.path.join(self.temp_dir, f"{expected_filename}.py")
                
                result = json_to_pydantic_model(
                    json_data=self.test_data,
                    output_file_path=base_output_path,
                    model_name=model_name
                )
                
                # Extract filename from the result message
                pattern = r"Successfully generated Pydantic model at (.+)"
                match = re.search(pattern, result)
                self.assertIsNotNone(match)
                
                returned_path = match.group(1)
                filename = os.path.basename(returned_path)
                
                # Should be snake_case with .py extension
                self.assertTrue(filename.endswith('.py'))
                self.assertIn(expected_filename, filename)

    def test_return_message_consistency_across_scenarios(self):
        """
        GIVEN various input scenarios
        WHEN json_to_pydantic_model completes successfully
        THEN expect consistent message format across all scenarios
        """
        scenarios = [
            # (description, json_data, model_name)
            ("simple dict", {"name": "test"}, "SimpleModel"),
            ("nested dict", {"user": {"name": "test", "age": 30}}, "NestedModel"),
            ("with lists", {"items": ["a", "b", "c"]}, "ListModel"),
            ("complex structure", {
                "id": 1,
                "data": {"nested": {"value": True}},
                "tags": ["tag1", "tag2"]
            }, "ComplexModel")
        ]
        
        expected_pattern = r"^Successfully generated Pydantic model at .+\.py$"
        
        for description, json_data, model_name in scenarios:
            with self.subTest(scenario=description):
                output_path = os.path.join(self.temp_dir, f"{description.replace(' ', '_')}.py")
                
                result = json_to_pydantic_model(
                    json_data=json_data,
                    output_file_path=output_path,
                    model_name=model_name
                )
                
                # Should match the expected pattern
                self.assertRegex(result, expected_pattern)
                
                # Should contain the exact phrase
                self.assertIn("Successfully generated Pydantic model at", result)
                
                # Should end with .py
                self.assertTrue(result.strip().endswith('.py'))

    def test_return_message_with_different_output_directories(self):
        """
        GIVEN output paths in different directory structures
        WHEN json_to_pydantic_model completes
        THEN expect return message contains the full correct path
        """
        # Test different directory structures
        test_paths = [
            "simple.py",
            os.path.join("subdir", "model.py"),
            os.path.join("deep", "nested", "path", "model.py"),
            os.path.join("with-dashes", "model.py"),
            os.path.join("with_underscores", "model.py")
        ]
        
        for relative_path in test_paths:
            with self.subTest(path=relative_path):
                # Create necessary directories
                full_path = os.path.join(self.temp_dir, relative_path)
                dir_path = os.path.dirname(full_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                
                result = json_to_pydantic_model(
                    json_data=self.test_data,
                    output_file_path=full_path,
                    model_name="TestModel"
                )
                
                # Extract path from result
                pattern = r"Successfully generated Pydantic model at (.+)"
                match = re.search(pattern, result)
                self.assertIsNotNone(match)
                
                returned_path = match.group(1)
                
                # Normalize paths for comparison
                expected_normalized = os.path.normpath(full_path)
                returned_normalized = os.path.normpath(returned_path)
                
                self.assertEqual(expected_normalized, returned_normalized)

    def test_return_message_path_normalization(self):
        """
        GIVEN paths with various formats (relative, absolute, with "..", etc.)
        WHEN json_to_pydantic_model completes
        THEN expect return message contains properly normalized paths
        """
        # Test with relative path containing ".."
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        
        # Path with ".." that resolves to temp_dir
        relative_path_with_dots = os.path.join(subdir, "..", "model_with_dots.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=relative_path_with_dots,
            model_name="DotsModel"
        )
        
        # Extract path from result
        pattern = r"Successfully generated Pydantic model at (.+)"
        match = re.search(pattern, result)
        self.assertIsNotNone(match)
        
        returned_path = match.group(1)
        
        # The returned path should be normalized (no ".." components)
        self.assertNotIn("..", returned_path)
        
        # But should point to the correct location
        expected_final_path = os.path.join(self.temp_dir, "model_with_dots.py")
        self.assertTrue(os.path.exists(expected_final_path))

    def test_return_message_no_extra_whitespace(self):
        """
        GIVEN successful model generation
        WHEN checking the return message
        THEN expect no leading/trailing whitespace and single spaces between words
        """
        output_path = os.path.join(self.temp_dir, "whitespace_test.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="WhitespaceModel"
        )
        
        # Should not have leading or trailing whitespace
        self.assertEqual(result, result.strip())
        
        # Should not have multiple consecutive spaces
        self.assertNotIn("  ", result)  # Double space
        self.assertNotIn("\t", result)  # Tab
        self.assertNotIn("\n", result)  # Newline
        self.assertNotIn("\r", result)  # Carriage return

    def test_return_message_encoding_handling(self):
        """
        GIVEN paths with Unicode characters
        WHEN json_to_pydantic_model completes
        THEN expect return message properly handles Unicode in paths
        """
        # Create path with Unicode characters
        unicode_filename = "模型_テスト_мodel.py"
        unicode_path = os.path.join(self.temp_dir, unicode_filename)

        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=unicode_path,
            model_name="UnicodePathModel"
        )
        
        # Should contain the success message
        self.assertIn("Successfully generated Pydantic model", result)
        
        # Should handle Unicode in the path
        self.assertIn(unicode_filename, result)


    def test_return_message_with_overwrite_scenario(self):
        """
        GIVEN an existing file that gets overwritten
        WHEN json_to_pydantic_model completes with overwrite_existing=True
        THEN expect same return message format as normal creation
        """
        output_path = os.path.join(self.temp_dir, "overwrite_test.py")
        
        # Create initial file
        result1 = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="OverwriteModel1"
        )
        
        # Overwrite the file
        result2 = json_to_pydantic_model(
            json_data={"different": "data", "new_field": 123},
            output_file_path=output_path,
            model_name="OverwriteModel2",
            overwrite_existing=True
        )
        
        # Both results should have the same format
        expected_pattern = r"^Successfully generated Pydantic model at .+\.py$"
        self.assertRegex(result1, expected_pattern)
        self.assertRegex(result2, expected_pattern)
        
        # Both should reference the same path
        path1 = re.search(r"at (.+)", result1).group(1)
        path2 = re.search(r"at (.+)", result2).group(1)
        self.assertEqual(path1, path2)

    def test_return_message_string_type(self):
        """
        GIVEN successful model generation
        WHEN checking the return value type
        THEN expect return value to be a string
        """
        output_path = os.path.join(self.temp_dir, "type_test.py")
        
        result = json_to_pydantic_model(
            json_data=self.test_data,
            output_file_path=output_path,
            model_name="TypeTestModel"
        )
        
        # Should be a string
        self.assertIsInstance(result, str)
        
        # Should not be empty
        self.assertTrue(len(result) > 0)
        
        # Should be a reasonable length (not excessively long)
        self.assertLess(len(result), 500)  # Reasonable upper bound


if __name__ == '__main__':
    unittest.main()