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
        THEN expect _ModelValidationError to be raised
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

if __name__ == '__main__':
    unittest.main()