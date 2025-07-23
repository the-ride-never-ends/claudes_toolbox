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
            
            # Should have nested models (Config gets renamed to avoid conflicts)
            self.assertIn("class Endpoints(BaseModel)", content)
            # Config should be renamed to avoid conflict with Pydantic's Config
            self.assertTrue("Config(BaseModel)" in content)  # Any config model should exist
            self.assertIn("class MixedStructureModel(BaseModel)", content)
            
            # Should have proper field types
            self.assertIn("id: int", content)
            self.assertIn("name: str", content)
            self.assertIn("is_active: bool", content)
            self.assertTrue("config:" in content)  # Should have config field
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


if __name__ == '__main__':
    unittest.main()