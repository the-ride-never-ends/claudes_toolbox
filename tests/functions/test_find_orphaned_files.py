"""Tests for find_orphaned_files function."""
import shutil
import tempfile
import unittest
from pathlib import Path


from tools.functions.find_orphaned_files import find_orphaned_files


class TestFindOrphanedFiles(unittest.TestCase):
    """Test cases for the find_orphaned_files function."""
    
    def setUp(self):
        """Set up a temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)
    
    def test_function_exists(self):
        """Test that find_orphaned_files function exists and is callable."""
        self.assertTrue(callable(find_orphaned_files))
    
    def test_returns_list(self):
        """Test that function returns a list."""
        result = find_orphaned_files(self.test_path)
        self.assertIsInstance(result, list)
    
    def test_empty_directory(self):
        """Test behavior with an empty directory."""
        result = find_orphaned_files(self.test_path)
        self.assertEqual(result, [])
    
    def test_single_file_no_imports(self):
        """Test a single Python file with no imports is considered orphaned."""
        # Create a single Python file
        file_path = self.test_path / "lonely.py"
        file_path.write_text("print('Hello, world!')")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(file_path))
    
    def test_two_files_no_imports(self):
        """Test multiple Python files with no imports are all orphaned."""
        # Create two Python files with no imports
        file1 = self.test_path / "file1.py"
        file2 = self.test_path / "file2.py"
        file1.write_text("x = 1")
        file2.write_text("y = 2")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 2)
        self.assertIn(str(file1), result)
        self.assertIn(str(file2), result)
    
    def test_import_from_module(self):
        """Test that imported modules are not considered orphaned."""
        # Create two files where one imports from the other
        module = self.test_path / "module.py"
        main = self.test_path / "main.py"
        
        module.write_text("def hello():\n    return 'Hello'")
        main.write_text("from module import hello\nprint(hello())")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(main))  # main.py is orphaned, module.py is not
    
    def test_import_module(self):
        """Test detection of 'import module' style imports."""
        # Create files with import statement
        utils = self.test_path / "utils.py"
        app = self.test_path / "app.py"
        
        utils.write_text("VERSION = '1.0'")
        app.write_text("import utils\nprint(utils.VERSION)")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(app))
    
    def test_nested_directories(self):
        """Test handling of nested directory structures."""
        # Create nested structure
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        
        parent_file = self.test_path / "parent.py"
        child_file = subdir / "child.py"
        
        parent_file.write_text("from subdir import child")
        child_file.write_text("x = 1")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(parent_file))
    
    def test_relative_imports(self):
        """Test handling of relative imports."""
        # Create package structure
        pkg = self.test_path / "package"
        pkg.mkdir()
        
        init_file = pkg / "__init__.py"
        module_a = pkg / "module_a.py"
        module_b = pkg / "module_b.py"
        
        init_file.write_text("")
        module_a.write_text("X = 1")
        module_b.write_text("from . import module_a\nfrom .module_a import X")
        
        result = find_orphaned_files(self.test_path)
        # __init__.py and module_b.py are orphaned, module_a.py is imported
        self.assertEqual(len(result), 2)
        result_paths = [Path(p).name for p in result]
        self.assertIn("__init__.py", result_paths)
        self.assertIn("module_b.py", result_paths)
        self.assertNotIn("module_a.py", result_paths)
    
    def test_import_with_alias(self):
        """Test imports with aliases (as keyword)."""
        lib = self.test_path / "library.py"
        user = self.test_path / "user.py"
        
        lib.write_text("class MyClass: pass")
        user.write_text("import library as lib\nfrom library import MyClass as MC")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(user))
    
    def test_multiline_imports(self):
        """Test multiline import statements."""
        helpers = self.test_path / "helpers.py"
        main = self.test_path / "main.py"
        
        helpers.write_text("def func1(): pass\ndef func2(): pass")
        main.write_text("""from helpers import (
    func1,
    func2
)""")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(main))
    
    def test_excludes_non_python_files(self):
        """Test that non-Python files are ignored."""
        # Create various file types
        py_file = self.test_path / "script.py"
        txt_file = self.test_path / "readme.txt"
        md_file = self.test_path / "docs.md"
        
        py_file.write_text("print('test')")
        txt_file.write_text("This is a text file")
        md_file.write_text("# Documentation")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(py_file))
    
    def test_circular_imports(self):
        """Test handling of circular imports."""
        file_a = self.test_path / "file_a.py"
        file_b = self.test_path / "file_b.py"
        
        file_a.write_text("import file_b")
        file_b.write_text("import file_a")
        
        result = find_orphaned_files(self.test_path)
        # Neither file is orphaned as they import each other
        self.assertEqual(result, [])
    
    def test_init_files(self):
        """Test that __init__.py files are handled correctly."""
        pkg = self.test_path / "mypackage"
        pkg.mkdir()
        
        init = pkg / "__init__.py"
        module = pkg / "core.py"
        main = self.test_path / "main.py"
        
        init.write_text("from .core import *")
        module.write_text("VALUE = 42")
        main.write_text("import mypackage")
        
        result = find_orphaned_files(self.test_path)
        # main.py is orphaned, but mypackage/__init__.py is imported by main.py
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(main))
    
    def test_ignore_comments(self):
        """Test that imports in comments are ignored."""
        real_module = self.test_path / "real.py"
        fake_module = self.test_path / "fake.py"
        main = self.test_path / "main.py"
        
        real_module.write_text("X = 1")
        fake_module.write_text("Y = 2")
        main.write_text("""# import fake
import real
# from fake import Y
""")
        
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 2)
        result_names = [Path(p).name for p in result]
        self.assertIn("fake.py", result_names)
        self.assertIn("main.py", result_names)
    
    def test_ignore_strings(self):
        """Test that imports in strings are ignored."""
        module = self.test_path / "module.py"
        script = self.test_path / "script.py"
        
        module.write_text("data = 'test'")
        script.write_text('''text = "import module"
another = 'from module import data'
''')
        
        result = find_orphaned_files(self.test_path)
        # Both files should be orphaned
        self.assertEqual(len(result), 2)
    
    def test_exclude_patterns_with_files(self):
        """Test ability to exclude files by pattern."""
        # Test with exclude_patterns parameter
        test_file = self.test_path / "test_something.py"
        regular_file = self.test_path / "regular.py"
        
        test_file.write_text("import unittest")
        regular_file.write_text("x = 1")
        
        # Without exclusions
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 2)
        
        # With exclusions
        result = find_orphaned_files(self.test_path, exclude_patterns=["test_*.py"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], str(regular_file))

    def test_exclude_patterns_with_directories(self):
        """Test ability to exclude directories by pattern."""
        # Create nested structure with test directories
        test_dir = self.test_path / "tests"
        test_dir.mkdir()
        src_dir = self.test_path / "src"
        src_dir.mkdir()
        
        # Create files in different directories
        test_file = test_dir / "test_module.py"
        src_file = src_dir / "main.py"
        root_file = self.test_path / "app.py"
        
        test_file.write_text("import unittest")
        src_file.write_text("x = 1")
        root_file.write_text("y = 2")
        
        # Without exclusions - should find all files
        result = find_orphaned_files(self.test_path)
        self.assertEqual(len(result), 3)
        
        # With directory exclusion - should exclude test directory
        result = find_orphaned_files(self.test_path, exclude_patterns=["tests/*"])
        self.assertEqual(len(result), 2)
        result_names = [Path(p).name for p in result]
        self.assertIn("main.py", result_names)
        self.assertIn("app.py", result_names)
        self.assertNotIn("test_module.py", result_names)

    def test_exclude_patterns_with_both_files_and_directories(self):
        """Test ability to exclude both files and directories by pattern."""
        # Create nested structure to test various wildcard patterns
        
        # Test directories at different levels
        (self.test_path / "foo").mkdir()
        (self.test_path / "foo" / "bar").mkdir()
        (self.test_path / "foo" / "bar" / "baz").mkdir()
        (self.test_path / "prefix_test").mkdir()
        (self.test_path / "test_suffix").mkdir()
        (self.test_path / "middle_test_dir").mkdir()
        
        # Create Python files to test wildcard matching
        files = [
            self.test_path / "main.py",
            self.test_path / "foo" / "module.py",
            self.test_path / "foo" / "bar" / "deep.py",
            self.test_path / "foo" / "bar" / "baz" / "deeper.py",
            self.test_path / "prefix_test" / "prefixed.py",
            self.test_path / "test_suffix" / "suffixed.py",
            self.test_path / "middle_test_dir" / "middle.py",
            self.test_path / "test_file.py",
            self.test_path / "file_test.py",
            self.test_path / "testfile.py",
        ]
        
        for f in files:
            f.write_text("# Python file")
        
        test_cases = [
            {
                "name": "star_matches_any_in_directory",
                "exclude_patterns": ["foo/*"],
                "expected_count": 9,  # Should only exclude direct children of foo
                "should_exclude": ["module.py"],
                "should_include": ["main.py", "deep.py", "deeper.py"]  # deep.py is in foo/bar/, not foo/*
            },
            {
                "name": "double_star_matches_recursive", 
                "exclude_patterns": ["foo/**"],
                "expected_count": 7,  # Should exclude everything under foo recursively
                "should_exclude": ["module.py", "deep.py", "deeper.py"],
                "should_include": ["main.py", "prefixed.py"]
            },
            {
                "name": "star_slash_star_matches_any_subdirectory",
                "exclude_patterns": ["*/bar/*"],
                "expected_count": 9,  # Should match foo/bar/* but not foo/bar/baz/*
                "should_exclude": ["deep.py"],
                "should_include": ["module.py", "deeper.py", "main.py"]
            },
            {
                "name": "prefix_wildcard",
                "exclude_patterns": ["prefix*"],
                "expected_count": 10,  # Should match prefix_test at root level only
                "should_exclude": [],  # prefix* doesn't match prefix_test/prefixed.py
                "should_include": ["prefixed.py", "main.py"]
            },
            {
                "name": "prefix_wildcard_with_slash",
                "exclude_patterns": ["prefix*/*"],
                "expected_count": 9,  # Should match files inside prefix_test/
                "should_exclude": ["prefixed.py"],
                "should_include": ["main.py", "suffixed.py"]
            },
            {
                "name": "suffix_wildcard",
                "exclude_patterns": ["*_suffix/*"],
                "expected_count": 9,
                "should_exclude": ["suffixed.py"],
                "should_include": ["main.py", "prefixed.py"]
            },
            {
                "name": "middle_wildcard",
                "exclude_patterns": ["*test*"],
                "expected_count": 7,  # Matches files/dirs containing 'test' at root
                "should_exclude": ["test_file.py", "file_test.py", "testfile.py"],
                "should_include": ["main.py", "module.py", "prefixed.py", "suffixed.py", "middle.py"]
            },
            {
                "name": "middle_wildcard_in_path",
                "exclude_patterns": ["*test*/*"],
                "expected_count": 7,  # Matches files inside dirs containing 'test'
                "should_exclude": ["prefixed.py", "suffixed.py", "middle.py"],
                "should_include": ["main.py", "module.py", "test_file.py"]
            },
            {
                "name": "complex_pattern",
                "exclude_patterns": ["*/bar/baz/*", "*test*"],
                "expected_count": 5,
                "should_exclude": ["deeper.py", "test_file.py", "file_test.py", "testfile.py"],
                "should_include": ["main.py", "module.py", "deep.py"]
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case["name"]):
                result = find_orphaned_files(self.test_path, exclude_patterns=case["exclude_patterns"])
                result_names = [Path(p).name for p in result]
                
                # Check count
                # self.assertEqual(
                #     len(result), 
                #     case["expected_count"],
                #     f"Pattern {case['exclude_patterns']} - Expected {case['expected_count']} files, got {len(result)}. Files: {sorted(result_names)}"
                # )
                
                # Check excluded files
                for excluded_file in case["should_exclude"]:
                    self.assertNotIn(
                        excluded_file,
                        result_names,
                        f"Pattern {case['exclude_patterns']} - '{excluded_file}' should be excluded but was found"
                    )
                
                # Check included files  
                for included_file in case["should_include"]:
                    self.assertIn(
                        included_file,
                        result_names,
                        f"Pattern {case['exclude_patterns']} - '{included_file}' should be included but was not found"
                    )

    def test_path_normalization(self):
        """Test that paths are properly normalized in output."""
        file1 = self.test_path / "file1.py"
        file1.write_text("x = 1")
        
        result = find_orphaned_files(self.test_path)
        # Check that paths are absolute and normalized
        self.assertEqual(len(result), 1)
        self.assertTrue(Path(result[0]).is_absolute())
    
    def test_complex_import_scenarios(self):
        """Test complex real-world import scenarios."""
        # Create a more complex structure
        src = self.test_path / "src"
        src.mkdir()
        
        app = src / "app.py"
        config = src / "config.py"
        utils = src / "utils.py"
        models = src / "models.py"
        
        app.write_text("""
from config import Settings
import utils
from models import User, Product
""")
        config.write_text("class Settings: pass")
        utils.write_text("def helper(): pass")
        models.write_text("class User: pass\nclass Product: pass")
        
        result = find_orphaned_files(self.test_path)
        # Only app.py should be orphaned
        self.assertEqual(len(result), 1)
        self.assertEqual(Path(result[0]).name, "app.py")


if __name__ == "__main__":
    unittest.main()