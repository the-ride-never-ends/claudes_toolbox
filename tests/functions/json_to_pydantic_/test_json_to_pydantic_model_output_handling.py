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


if __name__ == '__main__':
    unittest.main()