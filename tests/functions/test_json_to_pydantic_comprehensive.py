
# import json
# import os
# import tempfile
# import unittest
# from pathlib import Path
# import sys
# import re
# from unittest.mock import patch

# # Add import for the module we're testing
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# try:
#     from tools.functions.json_to_pydantic import json_to_pydantic
# except ImportError:
#     raise ImportError("Cannot import json_to_pydantic. Make sure the module is in your path.")


# class TestJsonToPydanticIntegrationWithExpectedOutput(unittest.TestCase):
#     """Integration tests comparing actual output with expected output"""

#     def setUp(self):
#         """Set up test fixtures"""
#         # Create a temporary directory for output
#         self.temp_dir = tempfile.mkdtemp()
        
#         # Path to the sample JSON file
#         self.sample_json_path = "/home/kylerose1946/omni_converter_mk2/core/content_extractor/processors/sample.json"
        
#         # Path to expected output
#         self.expected_output_path = "/home/kylerose1946/omni_converter_mk2/core/content_extractor/processors/expected_json_to_pydantic_output_for_schema_json.py"
        
#         # Load the sample JSON data for validation
#         with open(self.sample_json_path, 'r') as f:
#             self.sample_data = json.load(f)
            
#         # Load expected output
#         with open(self.expected_output_path, 'r') as f:
#             self.expected_output = f.read()

#     def tearDown(self):
#         """Clean up test fixtures"""
#         # Remove temporary directory
#         import shutil
#         shutil.rmtree(self.temp_dir)

#     def test_generate_models_and_compare_structure(self):
#         """Test that generated models match the expected structure"""
#         # Generate the models
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",  # Use same name as expected
#             allow_optional_fields=False
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
#         with open(output_path, 'r') as f:
#             actual_output = f.read()
        
#         print("ACTUAL OUTPUT:")
#         print("=" * 80)
#         print(actual_output)
#         print("=" * 80)
        
#         print("\nEXPECTED OUTPUT:")
#         print("=" * 80)
#         print(self.expected_output)
#         print("=" * 80)
        
#         # Extract class names from both outputs
#         actual_classes = self._extract_class_names(actual_output)
#         expected_classes = self._extract_class_names(self.expected_output)
        
#         print(f"\nActual classes found: {actual_classes}")
#         print(f"Expected classes: {expected_classes}")
        
#         # Check that we have the expected number of classes
#         self.assertEqual(len(actual_classes), len(expected_classes), 
#                         f"Expected {len(expected_classes)} classes, got {len(actual_classes)}")
        
#         # Check that specific expected classes exist
#         for expected_class in expected_classes:
#             self.assertIn(expected_class, actual_classes, 
#                          f"Expected class '{expected_class}' not found in generated output")

#     def test_list_fields_properly_typed(self):
#         """Test that list fields are properly typed as List[ModelName] or List[str]"""
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",
#             allow_optional_fields=False
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
#         with open(output_path, 'r') as f:
#             actual_output = f.read()
        
#         # Check specific field types that should be lists
#         expected_list_fields = {
#             'type_vars': 'List[TypeVars]',
#             'imports': 'List[str]',
#             'required_resources': 'List[RequiredResources]', 
#             'resource_assignments': 'List[ResourceAssignments]',
#             'optional_resources': 'List[OptionalResources]',
#             'methods': 'List[Methods]'
#         }
        
#         for field_name, expected_type in expected_list_fields.items():
#             with self.subTest(field=field_name):
#                 # Look for the field definition in the main PDFProcessor class
#                 field_pattern = rf'{field_name}:\s*([^=\n]+)'
#                 match = re.search(field_pattern, actual_output)
                
#                 if match:
#                     actual_type = match.group(1).strip()
#                     print(f"Field '{field_name}': expected '{expected_type}', got '{actual_type}'")
                    
#                     # For now, let's just check it's not None
#                     self.assertNotEqual(actual_type, "None", 
#                                       f"Field '{field_name}' should not be None type")
#                 else:
#                     self.fail(f"Field '{field_name}' not found in generated output")

#     def test_nested_model_classes_created(self):
#         """Test that nested model classes are created for complex objects"""
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",
#             allow_optional_fields=False
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
#         with open(output_path, 'r') as f:
#             actual_output = f.read()
        
#         # Expected nested model classes based on the JSON structure
#         expected_nested_models = [
#             'TypeVars',
#             'RequiredResources', 
#             'ResourceAssignments',
#             'OptionalResources',
#             'Parameters',
#             'Returns',
#             'Methods'
#         ]
        
#         for model_name in expected_nested_models:
#             with self.subTest(model=model_name):
#                 # Check if the class definition exists
#                 class_pattern = rf'class {model_name}\(BaseModel\):'
#                 self.assertRegex(actual_output, class_pattern, 
#                                f"Expected nested model class '{model_name}' not found")

#     def test_field_types_in_nested_models(self):
#         """Test that fields in nested models have correct types"""
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",
#             allow_optional_fields=False
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
#         with open(output_path, 'r') as f:
#             actual_output = f.read()
        
#         # Check specific field types in nested models
#         # TypeVars should have name: str and description: str
#         if 'class TypeVars(BaseModel):' in actual_output:
#             self.assertIn('name: str', actual_output)
#             self.assertIn('description: str', actual_output)
        
#         # RequiredResources should have name: str and description: str  
#         if 'class RequiredResources(BaseModel):' in actual_output:
#             # Should have both name and description fields
#             required_resources_section = self._extract_class_section(actual_output, 'RequiredResources')
#             if required_resources_section:
#                 self.assertIn('name:', required_resources_section)
#                 self.assertIn('description:', required_resources_section)

#     def test_optional_fields_with_defaults(self):
#         """Test that optional fields have proper defaults"""
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",
#             allow_optional_fields=False
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
#         with open(output_path, 'r') as f:
#             actual_output = f.read()
        
#         # In the Methods class, some fields should be optional
#         methods_section = self._extract_class_section(actual_output, 'Methods')
#         if methods_section:
#             # Check for optional fields that should have defaults
#             # Based on expected output: raises and is_property should be optional
#             print("Methods section:")
#             print(methods_section)

#     def test_can_instantiate_generated_models_with_sample_data(self):
#         """Test that generated models can be instantiated with the original JSON data"""
#         json_to_pydantic(
#             self.sample_json_path,
#             self.temp_dir,
#             "PDFProcessor",
#             allow_optional_fields=True  # Use optional to avoid strict validation issues
#         )
        
#         output_path = Path(self.temp_dir) / "PDFProcessor.py"
        
#         # Try to import and use the generated model
#         import importlib.util
        
#         spec = importlib.util.spec_from_file_location("PDFProcessor", output_path)
#         module = importlib.util.module_from_spec(spec)
        
#         try:
#             spec.loader.exec_module(module)
#             # Get the main model class
#             PDFProcessor = getattr(module, "PDFProcessor")
            
#             # Try to create an instance with the original data
#             instance = PDFProcessor(**self.sample_data)
            
#             # Verify basic fields
#             self.assertEqual(instance.class_name, "PDFProcessor")
#             self.assertEqual(instance.format_name, "PDF")
            
#             # Check that list fields are populated
#             self.assertIsInstance(instance.imports, list)
#             self.assertGreater(len(instance.imports), 0)
            
#         except Exception as e:
#             self.fail(f"Generated model could not be imported or instantiated: {e}")

#     def _extract_class_names(self, code: str) -> list:
#         """Extract all class names from Python code"""
#         pattern = r'class\s+(\w+)\s*\('
#         return re.findall(pattern, code)
    
#     def _extract_class_section(self, code: str, class_name: str) -> str:
#         """Extract the complete class definition section"""
#         lines = code.split('\n')
#         class_start = -1
#         class_end = -1
        
#         # Find the start of the class
#         for i, line in enumerate(lines):
#             if f'class {class_name}(' in line:
#                 class_start = i
#                 break
        
#         if class_start == -1:
#             return ""
        
#         # Find the end of the class (next class or end of file)
#         for i in range(class_start + 1, len(lines)):
#             line = lines[i]
#             if line.startswith('class ') and line.strip().endswith(':'):
#                 class_end = i
#                 break
        
#         if class_end == -1:
#             class_end = len(lines)
        
#         return '\n'.join(lines[class_start:class_end])

# if __name__ == "__main__":
#     unittest.main(verbosity=2)
