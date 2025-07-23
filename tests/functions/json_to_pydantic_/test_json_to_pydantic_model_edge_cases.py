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
        serialized = instance.model_dump(by_alias=True)
        
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
        serialized = instance.model_dump(by_alias=True)
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
        serialized = instance.model_dump(by_alias=True)
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
        serialized = instance.model_dump(by_alias=True)
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
            "mixed_unicode_123_ñ": "mixed",
            "德语": "Hallo Welt",
            "한국어": "안녕하세요",
            "português": "olá mundo",
            "italiano": "ciao mondo",
            "中文简体": "你好世界",
            "中文繁體": "你好世界",
            "日本語": "こんにちは世界",
            "ελληνικά": "γεια σας κόσμε",
            "עברית": "שלום עולם",
            "हिंदी": "नमस्ते दुनिया",
            "🌍🌎🌏": "world_emojis",
            "🚀rocket": "space",
            "💡idea": "lightbulb",
            "🔥fire": "hot",
            "⚡️lightning": "fast",
            "unicode_∑∆∏": "math_symbols",
            "symbols_©®™": "trademark",
            "currency_€£¥$": "money",
            "fractions_½¼¾": "parts",
            "arrows_←→↑↓": "directions"
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
        serialized = instance.model_dump(by_alias=True)
        for key, value in unicode_data.items():
            self.assertIn(key, serialized)
            self.assertEqual(serialized[key], value)


if __name__ == '__main__':
    unittest.main()