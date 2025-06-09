#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for python_code_generator.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from pathlib import Path
import sys
import tempfile
import os
import re
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    import tools.cli.mermaid_to_prototype.class_diagram_to_python_files.python_code_generator as python_code_generator
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestGenerateClassCodeMainFunction(unittest.TestCase):
    """
    Test suite for the main generate_class_code() function.
    
    Tests cover:
    - Complete class generation pipeline
    - Different class types (regular, abstract, enum, interface)
    - Various generation options
    - Code structure validation
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates standard class definitions and options for testing.
        """
        # Standard class definition
        self.basic_class_def = {
            'name': 'Animal',
            'attributes': [
                {'name': 'name', 'data_type': 'String', 'visibility': 'public'},
                {'name': 'age', 'data_type': 'int', 'visibility': 'public'}
            ],
            'methods': [
                {
                    'name': 'makeSound',
                    'visibility': 'public',
                    'return_type': 'void',
                    'parameters': []
                }
            ],
            'annotations': []
        }
        
        # Default options
        self.default_options = {
            'include_docstrings': True,
            'include_type_hints': True,
            'naming_convention': 'snake_case'
        }

    def test_generate_basic_class_with_all_features(self):
        """
        Test generating a basic class with attributes and methods.
        
        Pseudocode:
        1. Create class definition with attributes and methods
        2. Call generate_class_code with default options
        3. Verify class header is generated correctly
        4. Verify docstring is included
        5. Verify __init__ method with attributes
        6. Verify methods are generated
        
        Expected behavior:
        - Complete class structure should be generated
        - Proper Python syntax should be used
        - Type hints should be included when enabled
        """
        result = python_code_generator.generate_class_code(
            self.basic_class_def, 
            self.default_options
        )
        
        # Verify class structure
        self.assertIn("class Animal:", result)
        self.assertIn('"""Animal class."""', result)
        self.assertIn("def __init__(self):", result)
        self.assertIn("def make_sound(self) -> None:", result)
        
        # Verify attributes are initialized
        self.assertIn("self.name: str = \"\"", result)
        self.assertIn("self.age: int = 0", result)
        
        # Verify proper indentation and structure
        lines = result.split('\n')
        class_line = next(line for line in lines if 'class Animal:' in line)
        self.assertFalse(class_line.startswith(' '))  # Class should not be indented

    def test_generate_abstract_class(self):
        """
        Test generating an abstract class with abstract methods.
        
        Pseudocode:
        1. Create class definition with 'abstract' annotation
        2. Add abstract method to the definition
        3. Call generate_class_code
        4. Verify ABC inheritance
        5. Verify abstract method decorators
        6. Verify proper imports are generated
        
        Expected behavior:
        - Class should inherit from ABC
        - Abstract methods should have @abstractmethod decorator
        - Proper imports should be included
        """
        abstract_class_def = {
            'name': 'AbstractAnimal',
            'attributes': [],
            'methods': [
                {
                    'name': 'makeSound',
                    'visibility': 'public',
                    'return_type': 'void',
                    'parameters': [],
                    'is_abstract': True
                }
            ],
            'annotations': ['abstract']
        }
        
        result = python_code_generator.generate_class_code(
            abstract_class_def, 
            self.default_options
        )
        
        # Verify ABC import
        self.assertIn("from abc import ABC, abstractmethod", result)
        
        # Verify class inheritance
        self.assertIn("class AbstractAnimal(ABC):", result)
        
        # Verify abstract method
        self.assertIn("@abstractmethod", result)
        self.assertIn("def make_sound(self) -> None:", result)

    def test_generate_enum_class(self):
        """
        Test generating an enumeration class.
        
        Pseudocode:
        1. Create class definition with 'enumeration' annotation
        2. Add enum values as attributes
        3. Call generate_class_code
        4. Verify Enum inheritance
        5. Verify enum values are properly formatted
        6. Verify no __init__ method is generated
        
        Expected behavior:
        - Class should inherit from Enum
        - Enum values should be class attributes
        - No __init__ method should be generated
        """
        enum_class_def = {
            'name': 'Color',
            'attributes': [
                {'name': 'RED', 'data_type': 'String'},
                {'name': 'GREEN', 'data_type': 'String'},
                {'name': 'BLUE', 'data_type': 'String'}
            ],
            'methods': [],
            'annotations': ['enumeration']
        }
        
        result = python_code_generator.generate_class_code(
            enum_class_def, 
            self.default_options
        )
        
        # Verify Enum import and inheritance
        self.assertIn("from enum import Enum", result)
        self.assertIn("class Color(Enum):", result)
        
        # Verify enum values
        self.assertIn('RED = "RED"', result)
        self.assertIn('GREEN = "GREEN"', result)
        self.assertIn('BLUE = "BLUE"', result)
        
        # Verify no __init__ method
        self.assertNotIn("def __init__", result)

    def test_generate_interface_class(self):
        """
        Test generating an interface class.
        
        Pseudocode:
        1. Create class definition with 'interface' annotation
        2. Add methods to the interface
        3. Call generate_class_code
        4. Verify ABC inheritance
        5. Verify interface docstring
        6. Verify no __init__ method is generated
        
        Expected behavior:
        - Class should inherit from ABC
        - Should have interface-specific docstring
        - No __init__ method should be generated
        """
        interface_class_def = {
            'name': 'Drawable',
            'attributes': [],
            'methods': [
                {
                    'name': 'draw',
                    'visibility': 'public',
                    'return_type': 'void',
                    'parameters': []
                }
            ],
            'annotations': ['interface']
        }
        
        result = python_code_generator.generate_class_code(
            interface_class_def, 
            self.default_options
        )
        
        # Verify ABC inheritance
        self.assertIn("class Drawable(ABC):", result)
        
        # Verify interface docstring
        self.assertIn('"""Drawable interface."""', result)
        
        # Verify no __init__ method
        self.assertNotIn("def __init__", result)

    def test_generate_class_without_docstrings(self):
        """
        Test generating class with docstrings disabled.
        
        Pseudocode:
        1. Create basic class definition
        2. Set include_docstrings option to False
        3. Call generate_class_code
        4. Verify no docstrings are included
        5. Verify class structure is still correct
        
        Expected behavior:
        - No docstrings should be present in generated code
        - Class structure should remain intact
        """
        options = self.default_options.copy()
        options['include_docstrings'] = False
        
        result = python_code_generator.generate_class_code(
            self.basic_class_def, 
            options
        )
        
        # Verify no docstrings
        self.assertNotIn('"""', result)
        
        # Verify class structure still exists
        self.assertIn("class Animal:", result)
        self.assertIn("def __init__(self):", result)

    def test_generate_class_without_type_hints(self):
        """
        Test generating class with type hints disabled.
        
        Pseudocode:
        1. Create basic class definition
        2. Set include_type_hints option to False
        3. Call generate_class_code
        4. Verify no type hints are included
        5. Verify attributes and methods still work
        
        Expected behavior:
        - No type hints should be present
        - Methods should not have -> return type annotations
        - Attributes should not have type annotations
        """
        options = self.default_options.copy()
        options['include_type_hints'] = False
        
        result = python_code_generator.generate_class_code(
            self.basic_class_def, 
            options
        )
        
        # Verify no type hints
        self.assertNotIn(": str", result)
        self.assertNotIn(": int", result)
        self.assertNotIn("-> None", result)
        
        # Verify attributes still assigned
        self.assertIn("self.name = \"\"", result)
        self.assertIn("self.age = 0", result)

    def test_generate_empty_class(self):
        """
        Test generating a class with no attributes or methods.
        
        Pseudocode:
        1. Create class definition with empty attributes and methods
        2. Call generate_class_code
        3. Verify class has pass statement
        4. Verify proper class structure
        
        Expected behavior:
        - Class should contain pass statement
        - Basic class structure should be maintained
        """
        empty_class_def = {
            'name': 'EmptyClass',
            'attributes': [],
            'methods': [],
            'annotations': []
        }
        
        result = python_code_generator.generate_class_code(
            empty_class_def, 
            self.default_options
        )
        
        # Verify pass statement is included
        self.assertIn("pass", result)
        
        # Verify basic structure
        self.assertIn("class EmptyClass:", result)


class TestGenerateInitFileFunction(unittest.TestCase):
    """
    Test suite for the generate_init_file() function.
    
    Tests cover:
    - Init file structure generation
    - Import statements creation
    - __all__ list generation
    - Multiple class handling
    """

    def test_generate_init_file_with_multiple_classes(self):
        """
        Test generating __init__.py file with multiple classes.
        
        Pseudocode:
        1. Create list of class information dictionaries
        2. Call generate_init_file
        3. Verify module docstring is included
        4. Verify import statements for each class
        5. Verify __all__ list contains all classes
        
        Expected behavior:
        - Should contain proper import statements
        - Should include __all__ list with all class names
        - Should have module-level docstring
        """
        classes = [
            {'name': 'Animal', 'filename': 'animal.py'},
            {'name': 'Dog', 'filename': 'dog.py'},
            {'name': 'Cat', 'filename': 'cat.py'}
        ]
        
        result = python_code_generator.generate_init_file(classes)
        
        # Verify module docstring
        self.assertIn('"""Generated Python classes from Mermaid class diagram."""', result)
        
        # Verify imports
        self.assertIn("from .animal import Animal", result)
        self.assertIn("from .dog import Dog", result)
        self.assertIn("from .cat import Cat", result)
        
        # Verify __all__ list
        self.assertIn("__all__ = [", result)
        self.assertIn("'Animal',", result)
        self.assertIn("'Dog',", result)
        self.assertIn("'Cat',", result)

    def test_generate_init_file_with_single_class(self):
        """
        Test generating __init__.py file with single class.
        
        Pseudocode:
        1. Create list with single class information
        2. Call generate_init_file
        3. Verify single import statement
        4. Verify __all__ list contains single class
        
        Expected behavior:
        - Should work correctly with single class
        - Should maintain proper structure
        """
        classes = [
            {'name': 'SingleClass', 'filename': 'single_class.py'}
        ]
        
        result = python_code_generator.generate_init_file(classes)
        
        # Verify single import
        self.assertIn("from .single_class import SingleClass", result)
        
        # Verify __all__ with single entry
        self.assertIn("__all__ = [", result)
        self.assertIn("'SingleClass',", result)

    def test_generate_init_file_with_empty_class_list(self):
        """
        Test generating __init__.py file with empty class list.
        
        Pseudocode:
        1. Create empty class list
        2. Call generate_init_file
        3. Verify basic structure is maintained
        4. Verify empty __all__ list
        
        Expected behavior:
        - Should handle empty list gracefully
        - Should still include basic structure
        """
        classes = []
        
        result = python_code_generator.generate_init_file(classes)
        
        # Verify basic structure
        self.assertIn('"""Generated Python classes from Mermaid class diagram."""', result)
        self.assertIn("__all__ = [", result)
        self.assertIn("]", result)


class TestHelperFunctionsNamingAndTypes(unittest.TestCase):
    """
    Test suite for helper functions dealing with naming conventions and type conversion.
    
    Tests cover:
    - Naming convention applications
    - Type conversion from Mermaid to Python
    - Default value generation
    """

    def test_apply_naming_convention_snake_case(self):
        """
        Test applying snake_case naming convention.
        
        Pseudocode:
        1. Test various camelCase and PascalCase names
        2. Apply snake_case convention
        3. Verify correct conversion to snake_case
        
        Expected behavior:
        - CamelCase should convert to snake_case
        - Already snake_case names should remain unchanged
        """
        options = {'naming_convention': 'snake_case'}
        
        test_cases = [
            ('camelCase', 'camel_case'),
            ('PascalCase', 'pascal_case'),
            ('XMLHttpRequest', 'x_m_l_http_request'),
            ('simple', 'simple'),
            ('already_snake_case', 'already_snake_case'),
            ('getHTMLContent', 'get_h_t_m_l_content')
        ]
        
        for input_name, expected_output in test_cases:
            result = python_code_generator._apply_naming_convention(input_name, options)
            self.assertEqual(result, expected_output, 
                           f"Failed for input '{input_name}': expected '{expected_output}', got '{result}'")

    def test_apply_naming_convention_preserve(self):
        """
        Test applying preserve naming convention.
        
        Pseudocode:
        1. Test various name formats
        2. Apply preserve convention
        3. Verify names remain unchanged
        
        Expected behavior:
        - All names should remain exactly as provided
        """
        options = {'naming_convention': 'preserve'}
        
        test_cases = [
            'camelCase',
            'PascalCase',
            'snake_case',
            'XMLHttpRequest',
            'simple'
        ]
        
        for name in test_cases:
            result = python_code_generator._apply_naming_convention(name, options)
            self.assertEqual(result, name)

    def test_apply_naming_convention_default(self):
        """
        Test applying default naming convention (should be snake_case).
        
        Pseudocode:
        1. Test with empty options dictionary
        2. Verify default behavior is snake_case
        
        Expected behavior:
        - Should default to snake_case conversion
        """
        options = {}  # No naming_convention specified
        
        result = python_code_generator._apply_naming_convention('CamelCase', options)
        self.assertEqual(result, 'camel_case')

    def test_convert_type_to_python_basic_types(self):
        """
        Test converting basic Mermaid types to Python types.
        
        Pseudocode:
        1. Test conversion of common Mermaid types
        2. Verify correct Python type hints are returned
        
        Expected behavior:
        - String/string should convert to str
        - int/Integer should convert to int
        - Boolean/bool should convert to bool
        - void should convert to None
        """
        test_cases = [
            ('String', 'str'),
            ('string', 'str'),
            ('int', 'int'),
            ('Integer', 'int'),
            ('Boolean', 'bool'),
            ('bool', 'bool'),
            ('double', 'float'),
            ('float', 'float'),
            ('void', 'None'),
            ('Any', 'Any')
        ]
        
        for mermaid_type, expected_python_type in test_cases:
            result = python_code_generator._convert_type_to_python(mermaid_type)
            self.assertEqual(result, expected_python_type)

    def test_convert_type_to_python_generic_types(self):
        """
        Test converting generic Mermaid types to Python types.
        
        Pseudocode:
        1. Test conversion of generic types like List~T~
        2. Verify proper generic type syntax
        
        Expected behavior:
        - List~String~ should convert to List[str]
        - List~int~ should convert to List[int]
        """
        test_cases = [
            ('List~String~', 'List[str]'),
            ('List~int~', 'List[int]'),
            ('List~Boolean~', 'List[bool]')
        ]
        
        for mermaid_type, expected_python_type in test_cases:
            result = python_code_generator._convert_type_to_python(mermaid_type)
            self.assertEqual(result, expected_python_type)

    def test_convert_type_to_python_unknown_types(self):
        """
        Test converting unknown types (should pass through unchanged).
        
        Pseudocode:
        1. Test conversion of custom/unknown types
        2. Verify they pass through unchanged
        
        Expected behavior:
        - Unknown types should be returned as-is
        """
        unknown_types = ['CustomType', 'MyClass', 'SomeInterface']
        
        for unknown_type in unknown_types:
            result = python_code_generator._convert_type_to_python(unknown_type)
            self.assertEqual(result, unknown_type)

    def test_get_default_value_basic_types(self):
        """
        Test getting default values for basic attribute types.
        
        Pseudocode:
        1. Test default value generation for common types
        2. Verify appropriate Python default values
        
        Expected behavior:
        - String types should default to empty string
        - Numeric types should default to zero
        - Boolean should default to False
        - Collections should default to empty collections
        """
        test_cases = [
            ('String', '""'),
            ('string', '""'),
            ('str', '""'),
            ('int', '0'),
            ('Integer', '0'),
            ('Boolean', 'False'),
            ('bool', 'False'),
            ('double', '0.0'),
            ('float', '0.0'),
            ('List', '[]'),
            ('Dict', '{}')
        ]
        
        for attr_type, expected_default in test_cases:
            result = python_code_generator._get_default_value(attr_type)
            self.assertEqual(result, expected_default)

    def test_get_default_value_generic_types(self):
        """
        Test getting default values for generic types.
        
        Pseudocode:
        1. Test default values for types containing List or Dict
        2. Verify proper collection defaults
        
        Expected behavior:
        - Any type containing 'List' should default to []
        - Any type containing 'Dict' should default to {}
        """
        test_cases = [
            ('List[str]', '[]'),
            ('Dict[str, int]', '{}'),
            ('List~String~', '[]'),
            ('MyListType', '[]'),  # Contains 'List'
            ('MyDictionary', '{}')  # Contains 'Dict'
        ]
        
        for attr_type, expected_default in test_cases:
            result = python_code_generator._get_default_value(attr_type)
            self.assertEqual(result, expected_default)

    def test_get_default_value_unknown_types(self):
        """
        Test getting default values for unknown types.
        
        Pseudocode:
        1. Test default value for unrecognized types
        2. Verify None is returned as fallback
        
        Expected behavior:
        - Unknown types should default to None
        """
        unknown_types = ['CustomType', 'MyClass', 'UnknownType']
        
        for unknown_type in unknown_types:
            result = python_code_generator._get_default_value(unknown_type)
            self.assertEqual(result, 'None')


class TestImportGenerationFunction(unittest.TestCase):
    """
    Test suite for the _generate_imports() function.
    
    Tests cover:
    - Import statement generation for different class types
    - ABC and abstractmethod imports for abstract classes
    - Enum imports for enumerations
    - Typing imports for type hints
    """

    def test_generate_imports_for_abstract_class(self):
        """
        Test import generation for abstract classes.
        
        Pseudocode:
        1. Create class definition with abstract annotation
        2. Call _generate_imports
        3. Verify ABC and abstractmethod imports
        
        Expected behavior:
        - Should import ABC and abstractmethod from abc
        """
        class_def = {
            'name': 'AbstractClass',
            'annotations': ['abstract'],
            'methods': [{'is_abstract': True}],
            'attributes': []
        }
        options = {'include_type_hints': True}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        self.assertIn("from abc import ABC, abstractmethod", result)

    def test_generate_imports_for_enum_class(self):
        """
        Test import generation for enumeration classes.
        
        Pseudocode:
        1. Create class definition with enumeration annotation
        2. Call _generate_imports
        3. Verify Enum import
        
        Expected behavior:
        - Should import Enum from enum
        """
        class_def = {
            'name': 'ColorEnum',
            'annotations': ['enumeration'],
            'methods': [],
            'attributes': []
        }
        options = {'include_type_hints': True}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        self.assertIn("from enum import Enum", result)

    def test_generate_imports_for_generic_class(self):
        """
        Test import generation for generic classes.
        
        Pseudocode:
        1. Create class definition with generic types
        2. Call _generate_imports
        3. Verify TypeVar and Generic imports
        
        Expected behavior:
        - Should import TypeVar and Generic from typing
        """
        class_def = {
            'name': 'GenericClass',
            'annotations': [],
            'generic_types': ['T', 'U'],
            'methods': [],
            'attributes': []
        }
        options = {'include_type_hints': True}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        self.assertIn("from typing import TypeVar, Generic", result)

    def test_generate_imports_for_complex_types(self):
        """
        Test import generation when complex typing is needed.
        
        Pseudocode:
        1. Create class definition with List, Dict, Optional types
        2. Call _generate_imports
        3. Verify appropriate typing imports
        
        Expected behavior:
        - Should import List, Dict, Optional from typing as needed
        """
        class_def = {
            'name': 'ComplexClass',
            'annotations': [],
            'attributes': [
                {'data_type': 'List[str]'},
                {'data_type': 'Dict[str, int]'},
                {'data_type': 'Optional[str]'}
            ],
            'methods': [
                {
                    'return_type': 'List[int]',
                    'parameters': [
                        {'type': 'Dict[str, str]'},
                        {'type': 'Optional[bool]'}
                    ]
                }
            ]
        }
        options = {'include_type_hints': True}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        # Should contain typing imports
        self.assertIn("from typing import", result)
        self.assertIn("List", result)
        self.assertIn("Dict", result)
        self.assertIn("Optional", result)

    def test_generate_imports_with_type_hints_disabled(self):
        """
        Test import generation when type hints are disabled.
        
        Pseudocode:
        1. Create class definition with complex types
        2. Set include_type_hints to False
        3. Call _generate_imports
        4. Verify minimal imports (only ABC/Enum if needed)
        
        Expected behavior:
        - Should not include typing imports when type hints disabled
        - Should still include ABC/Enum imports if class requires them
        """
        class_def = {
            'name': 'ComplexClass',
            'annotations': ['abstract'],
            'attributes': [{'data_type': 'List[str]'}],
            'methods': [{'is_abstract': True}]
        }
        options = {'include_type_hints': False}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        # Should still have ABC import for abstract class
        self.assertIn("from abc import ABC, abstractmethod", result)
        
        # Should not have typing imports
        self.assertNotIn("from typing import List", result)

    def test_generate_imports_with_no_special_requirements(self):
        """
        Test import generation for simple class with no special imports needed.
        
        Pseudocode:
        1. Create simple class definition with basic types
        2. Call _generate_imports
        3. Verify empty or minimal import result
        
        Expected behavior:
        - Should return empty string or minimal imports
        - No unnecessary imports should be included
        """
        class_def = {
            'name': 'SimpleClass',
            'annotations': [],
            'attributes': [
                {'data_type': 'str'},
                {'data_type': 'int'}
            ],
            'methods': [
                {
                    'return_type': 'str',
                    'parameters': [{'type': 'int'}]
                }
            ]
        }
        options = {'include_type_hints': True}
        
        result = python_code_generator._generate_imports(class_def, options)
        
        # Should be empty or contain only minimal imports
        self.assertFalse(result or result.strip() == "")


class TestClassHeaderAndDocstringGeneration(unittest.TestCase):
    """
    Test suite for class header and docstring generation functions.
    
    Tests cover:
    - Class header generation with inheritance
    - Docstring generation for different class types
    - Generic type handling
    """

    def test_generate_class_header_simple_class(self):
        """
        Test generating header for simple class without inheritance.
        
        Pseudocode:
        1. Create simple class definition
        2. Call _generate_class_header
        3. Verify basic class header format
        
        Expected behavior:
        - Should generate "class ClassName:" format
        """
        class_def = {
            'name': 'SimpleClass',
            'annotations': []
        }
        options = {}
        
        result = python_code_generator._generate_class_header(class_def, options)
        
        self.assertEqual(result, "class SimpleClass:")

    def test_generate_class_header_abstract_class(self):
        """
        Test generating header for abstract class.
        
        Pseudocode:
        1. Create class definition with abstract annotation
        2. Call _generate_class_header
        3. Verify ABC inheritance
        
        Expected behavior:
        - Should generate "class ClassName(ABC):" format
        """
        class_def = {
            'name': 'AbstractClass',
            'annotations': ['abstract']
        }
        options = {}
        
        result = python_code_generator._generate_class_header(class_def, options)
        
        self.assertEqual(result, "class AbstractClass(ABC):")

    def test_generate_class_header_enum_class(self):
        """
        Test generating header for enumeration class.
        
        Pseudocode:
        1. Create class definition with enumeration annotation
        2. Call _generate_class_header
        3. Verify Enum inheritance
        
        Expected behavior:
        - Should generate "class ClassName(Enum):" format
        """
        class_def = {
            'name': 'ColorEnum',
            'annotations': ['enumeration']
        }
        options = {}
        
        result = python_code_generator._generate_class_header(class_def, options)
        
        self.assertEqual(result, "class ColorEnum(Enum):")

    def test_generate_class_header_generic_class(self):
        """
        Test generating header for generic class.
        
        Pseudocode:
        1. Create class definition with generic types
        2. Call _generate_class_header
        3. Verify Generic inheritance with type parameters
        
        Expected behavior:
        - Should generate "class ClassName(Generic[T, U]):" format
        """
        class_def = {
            'name': 'GenericClass',
            'annotations': [],
            'generic_types': ['T', 'U']
        }
        options = {}
        
        result = python_code_generator._generate_class_header(class_def, options)
        
        self.assertEqual(result, "class GenericClass(Generic[T, U]):")

    def test_generate_class_docstring_different_types(self):
        """
        Test generating docstrings for different class types.
        
        Pseudocode:
        1. Test docstring generation for each class type
        2. Verify appropriate docstring content
        
        Expected behavior:
        - Different class types should have appropriate docstrings
        - Interface should say "interface"
        - Abstract should say "Abstract"
        - Enum should say "enumeration"
        """
        test_cases = [
            ({'name': 'Regular', 'annotations': []}, 'Regular class.'),
            ({'name': 'MyInterface', 'annotations': ['interface']}, 'MyInterface interface.'),
            ({'name': 'AbstractBase', 'annotations': ['abstract']}, 'Abstract AbstractBase class.'),
            ({'name': 'ColorEnum', 'annotations': ['enumeration']}, 'ColorEnum enumeration.')
        ]
        
        for class_def, expected_docstring in test_cases:
            result = python_code_generator._generate_class_docstring(class_def)
            self.assertEqual(result, expected_docstring)


class TestMethodGeneration(unittest.TestCase):
    """
    Test suite for method generation functions.
    
    Tests cover:
    - Method signature generation
    - Parameter handling
    - Return type annotations
    - Static and abstract method decorators
    - Visibility handling
    """

    def setUp(self) -> None:
        """Set up test fixtures for method generation tests."""
        self.basic_class_def = {
            'name': 'TestClass',
            'annotations': []
        }
        
        self.default_options = {
            'include_type_hints': True,
            'include_docstrings': True,
            'naming_convention': 'snake_case'
        }

    def test_generate_single_method_basic(self):
        """
        Test generating a basic instance method.
        
        Pseudocode:
        1. Create basic method definition
        2. Call _generate_single_method
        3. Verify method signature and body
        4. Verify proper indentation and structure
        
        Expected behavior:
        - Should generate proper method signature with self
        - Should include return type annotation when enabled
        - Should include docstring when enabled
        """
        method_def = {
            'name': 'getValue',
            'visibility': 'public',
            'return_type': 'String',
            'parameters': [],
            'is_static': False,
            'is_abstract': False
        }
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, self.default_options
        )
        
        # Verify method signature
        self.assertIn("def get_value(self) -> str:", result)
        
        # Verify docstring
        self.assertIn('"""Get Value method."""', result)
        
        # Verify method body
        self.assertIn("pass", result)

    def test_generate_single_method_with_parameters(self):
        """
        Test generating method with parameters.
        
        Pseudocode:
        1. Create method definition with multiple parameters
        2. Call _generate_single_method
        3. Verify parameters are included in signature
        4. Verify type hints for parameters
        
        Expected behavior:
        - Parameters should be included in method signature
        - Type hints should be applied to parameters when enabled
        """
        method_def = {
            'name': 'setValue',
            'visibility': 'public',
            'return_type': 'void',
            'parameters': [
                {'name': 'newValue', 'type': 'String'},
                {'name': 'isValid', 'type': 'Boolean'}
            ],
            'is_static': False,
            'is_abstract': False
        }
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, self.default_options
        )
        
        # Verify method signature with parameters
        self.assertIn("def set_value(self, new_value: str, is_valid: bool) -> None:", result)

    def test_generate_single_method_static(self):
        """
        Test generating static method.
        
        Pseudocode:
        1. Create static method definition
        2. Call _generate_single_method
        3. Verify @staticmethod decorator
        4. Verify no self parameter
        
        Expected behavior:
        - Should include @staticmethod decorator
        - Should not include self parameter
        - Should handle parameters correctly
        """
        method_def = {
            'name': 'createInstance',
            'visibility': 'public',
            'return_type': 'TestClass',
            'parameters': [
                {'name': 'config', 'type': 'String'}
            ],
            'is_static': True,
            'is_abstract': False
        }
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, self.default_options
        )
        
        # Verify static method decorator
        self.assertIn("@staticmethod", result)
        
        # Verify no self parameter
        self.assertIn("def create_instance(config: str) -> TestClass:", result)
        self.assertNotIn("self,", result)

    def test_generate_single_method_abstract(self):
        """
        Test generating abstract method.
        
        Pseudocode:
        1. Create abstract method definition
        2. Call _generate_single_method
        3. Verify @abstractmethod decorator
        4. Verify method has pass statement
        
        Expected behavior:
        - Should include @abstractmethod decorator
        - Should include self parameter
        - Should have pass statement as body
        """
        method_def = {
            'name': 'abstractMethod',
            'visibility': 'public',
            'return_type': 'void',
            'parameters': [],
            'is_static': False,
            'is_abstract': True
        }
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, self.default_options
        )
        
        # Verify abstract method decorator
        self.assertIn("@abstractmethod", result)
        
        # Verify method signature
        self.assertIn("def abstract_method(self) -> None:", result)
        
        # Verify pass statement
        self.assertIn("pass", result)

    def test_generate_single_method_private(self):
        """
        Test generating private method.
        
        Pseudocode:
        1. Create private method definition
        2. Call _generate_single_method
        3. Verify underscore prefix for private visibility
        
        Expected behavior:
        - Private methods should have underscore prefix
        - Method should otherwise be generated normally
        """
        method_def = {
            'name': 'privateMethod',
            'visibility': 'private',
            'return_type': 'void',
            'parameters': [],
            'is_static': False,
            'is_abstract': False
        }
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, self.default_options
        )
        
        # Verify private method name
        self.assertIn("def _private_method(self) -> None:", result)

    def test_generate_single_method_without_type_hints(self):
        """
        Test generating method with type hints disabled.
        
        Pseudocode:
        1. Create method definition with parameters and return type
        2. Disable type hints in options
        3. Call _generate_single_method
        4. Verify no type annotations
        
        Expected behavior:
        - Should not include type hints in signature
        - Should not include return type annotation
        """
        method_def = {
            'name': 'getValue',
            'visibility': 'public',
            'return_type': 'String',
            'parameters': [
                {'name': 'key', 'type': 'String'}
            ],
            'is_static': False,
            'is_abstract': False
        }
        
        options = self.default_options.copy()
        options['include_type_hints'] = False
        
        result = python_code_generator._generate_single_method(
            method_def, self.basic_class_def, options
        )
        
        # Verify no type hints
        self.assertIn("def get_value(self, key):", result)
        self.assertNotIn("-> str", result)
        self.assertNotIn(": str", result)

    def test_generate_methods_multiple_methods(self):
        """
        Test generating multiple methods for a class.
        
        Pseudocode:
        1. Create class definition with multiple methods
        2. Call _generate_methods
        3. Verify all methods are generated
        4. Verify proper separation between methods
        
        Expected behavior:
        - All methods should be generated
        - Methods should be separated by double newlines
        """
        class_def = {
            'name': 'TestClass',
            'annotations': [],
            'methods': [
                {
                    'name': 'method1',
                    'visibility': 'public',
                    'return_type': 'void',
                    'parameters': []
                },
                {
                    'name': 'method2',
                    'visibility': 'public',
                    'return_type': 'String',
                    'parameters': []
                }
            ]
        }
        
        result = python_code_generator._generate_methods(class_def, self.default_options)
        
        # Verify both methods are present
        self.assertIn("def method1(self) -> None:", result)
        self.assertIn("def method2(self) -> str:", result)
        
        # Verify proper separation (double newline)
        self.assertIn("\n\n", result)

    def test_generate_methods_for_enum_class(self):
        """
        Test that methods are not generated for enum classes.
        
        Pseudocode:
        1. Create enum class definition with methods
        2. Call _generate_methods
        3. Verify empty result
        
        Expected behavior:
        - Should return empty string for enum classes
        - No methods should be generated
        """
        class_def = {
            'name': 'ColorEnum',
            'annotations': ['enumeration'],
            'methods': [
                {
                    'name': 'getValue',
                    'visibility': 'public',
                    'return_type': 'String',
                    'parameters': []
                }
            ]
        }
        
        result = python_code_generator._generate_methods(class_def, self.default_options)
        
        # Should be empty for enum
        self.assertEqual(result, "")


class TestInitAndAttributeGeneration(unittest.TestCase):
    """
    Test suite for __init__ method and attribute generation.
    
    Tests cover:
    - __init__ method generation with various attribute types
    - Class attribute generation for static attributes
    - Enum value generation
    - Visibility handling for attributes
    """

    def setUp(self) -> None:
        """Set up test fixtures for attribute generation tests."""
        self.default_options = {
            'include_type_hints': True,
            'include_docstrings': True,
            'naming_convention': 'snake_case'
        }

    def test_generate_init_method_with_attributes(self):
        """
        Test generating __init__ method with instance attributes.
        
        Pseudocode:
        1. Create class definition with instance attributes
        2. Call _generate_init_method
        3. Verify __init__ signature and attribute initialization
        4. Verify type hints and default values
        
        Expected behavior:
        - Should generate __init__ method
        - Should initialize all instance attributes
        - Should use appropriate default values
        """
        class_def = {
            'name': 'TestClass',
            'annotations': [],
            'attributes': [
                {
                    'name': 'name',
                    'data_type': 'String',
                    'visibility': 'public',
                    'is_static': False
                },
                {
                    'name': 'count',
                    'data_type': 'int',
                    'visibility': 'public',
                    'is_static': False
                }
            ]
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        # Verify __init__ method structure
        self.assertIn("def __init__(self):", result)
        self.assertIn('"""Initialize the class."""', result)
        
        # Verify attribute initialization
        self.assertIn("self.name: str = \"\"", result)
        self.assertIn("self.count: int = 0", result)

    def test_generate_init_method_with_private_attributes(self):
        """
        Test generating __init__ method with private attributes.
        
        Pseudocode:
        1. Create class definition with private attributes
        2. Call _generate_init_method
        3. Verify private attributes get underscore prefix
        
        Expected behavior:
        - Private attributes should have underscore prefix
        - Protected attributes should have underscore prefix
        """
        class_def = {
            'name': 'TestClass',
            'annotations': [],
            'attributes': [
                {
                    'name': 'privateVar',
                    'data_type': 'String',
                    'visibility': 'private',
                    'is_static': False
                },
                {
                    'name': 'protectedVar',
                    'data_type': 'int',
                    'visibility': 'protected',
                    'is_static': False
                }
            ]
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        # Verify private/protected attribute naming
        self.assertIn("self._private_var: str = \"\"", result)
        self.assertIn("self._protected_var: int = 0", result)

    def test_generate_init_method_for_abstract_class(self):
        """
        Test generating __init__ method for abstract class.
        
        Pseudocode:
        1. Create abstract class definition
        2. Call _generate_init_method
        3. Verify super().__init__() call is included
        
        Expected behavior:
        - Should include super().__init__() call for abstract classes
        """
        class_def = {
            'name': 'AbstractClass',
            'annotations': ['abstract'],
            'attributes': [
                {
                    'name': 'value',
                    'data_type': 'String',
                    'visibility': 'public',
                    'is_static': False
                }
            ]
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        # Verify super() call
        self.assertIn("super().__init__()", result)

    def test_generate_init_method_for_interface(self):
        """
        Test that __init__ method is not generated for interfaces.
        
        Pseudocode:
        1. Create interface class definition
        2. Call _generate_init_method
        3. Verify empty result
        
        Expected behavior:
        - Should return empty string for interfaces
        """
        class_def = {
            'name': 'TestInterface',
            'annotations': ['interface'],
            'attributes': []
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        self.assertEqual(result, "")

    def test_generate_init_method_for_enum(self):
        """
        Test that __init__ method is not generated for enums.
        
        Pseudocode:
        1. Create enum class definition
        2. Call _generate_init_method
        3. Verify empty result
        
        Expected behavior:
        - Should return empty string for enums
        """
        class_def = {
            'name': 'ColorEnum',
            'annotations': ['enumeration'],
            'attributes': []
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        self.assertEqual(result, "")

    def test_generate_init_method_with_no_attributes(self):
        """
        Test generating __init__ method when class has no instance attributes.
        
        Pseudocode:
        1. Create class definition with no attributes
        2. Call _generate_init_method
        3. Verify simple __init__ with pass statement
        
        Expected behavior:
        - Should generate simple __init__ with pass statement
        """
        class_def = {
            'name': 'EmptyClass',
            'annotations': [],
            'attributes': []
        }
        
        result = python_code_generator._generate_init_method(class_def, self.default_options)
        
        self.assertIn("def __init__(self):", result)
        self.assertIn("pass", result)

    def test_generate_class_attributes_static_attributes(self):
        """
        Test generating static class attributes.
        
        Pseudocode:
        1. Create class definition with static attributes
        2. Call _generate_class_attributes
        3. Verify static attributes are generated at class level
        
        Expected behavior:
        - Static attributes should be generated as class variables
        - Should use appropriate type hints and default values
        """
        class_def = {
            'name': 'TestClass',
            'annotations': [],
            'attributes': [
                {
                    'name': 'staticVar',
                    'data_type': 'String',
                    'visibility': 'public',
                    'is_static': True
                },
                {
                    'name': 'count',
                    'data_type': 'int',
                    'visibility': 'public',
                    'is_static': True
                }
            ]
        }
        
        result = python_code_generator._generate_class_attributes(class_def, self.default_options)
        
        # Verify static attributes
        self.assertIn("static_var: str = \"\"", result)
        self.assertIn("count: int = 0", result)

    def test_generate_class_attributes_enum_values(self):
        """
        Test generating enum values as class attributes.
        
        Pseudocode:
        1. Create enum class definition with enum values
        2. Call _generate_class_attributes
        3. Verify enum values are properly formatted
        
        Expected behavior:
        - Enum values should be generated as class attributes
        - Should use proper enum value format
        """
        class_def = {
            'name': 'ColorEnum',
            'annotations': ['enumeration'],
            'attributes': [
                {'name': 'RED', 'data_type': 'String'},
                {'name': 'GREEN', 'data_type': 'String'},
                {'name': 'BLUE', 'data_type': 'String'}
            ]
        }
        
        result = python_code_generator._generate_class_attributes(class_def, self.default_options)
        
        # Verify enum values
        self.assertIn('RED = "RED"', result)
        self.assertIn('GREEN = "GREEN"', result)
        self.assertIn('BLUE = "BLUE"', result)

    def test_generate_class_attributes_no_static_attributes(self):
        """
        Test generating class attributes when there are no static attributes.
        
        Pseudocode:
        1. Create class definition with only instance attributes
        2. Call _generate_class_attributes
        3. Verify empty result
        
        Expected behavior:
        - Should return empty string when no static attributes
        """
        class_def = {
            'name': 'TestClass',
            'annotations': [],
            'attributes': [
                {
                    'name': 'instanceVar',
                    'data_type': 'String',
                    'visibility': 'public',
                    'is_static': False
                }
            ]
        }
        
        result = python_code_generator._generate_class_attributes(class_def, self.default_options)
        
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()