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