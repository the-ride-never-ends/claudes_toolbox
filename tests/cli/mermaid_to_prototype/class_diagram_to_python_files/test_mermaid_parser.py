#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test file for class_diagram_to_python_files/mermaid_parser.py
Following Google-style docstrings with pseudocode and test-driven development approach.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call
from pathlib import Path
import sys
import tempfile
import os
from typing import Dict, List, Any, Optional

# Import modules under test
try:
    sys.path.insert(0, '/home/kylerose1946/claudes_toolbox/claudes_toolbox/tools/cli/mermaid_to_prototype/class_diagram_to_python_files')
    import tools.cli.mermaid_to_prototype.class_diagram_to_python_files._mermaid_parser as _mermaid_parser
except ImportError as e:
    raise ImportError(f"Failed to import necessary modules: {e}")


class TestParseClassDiagram(unittest.TestCase):
    """
    Comprehensive unit tests for the parse_class_diagram() function.
    
    Tests cover:
    - Basic class diagram parsing
    - Class definitions with attributes and methods
    - Relationships between classes
    - Notes and annotations
    - Namespaces and generics
    - Error handling for invalid input
    """

    def setUp(self) -> None:
        """
        Set up test fixtures before each test method.
        
        Creates sample Mermaid diagram content for testing various scenarios.
        """
        # Basic class diagram
        self.basic_diagram = """
        classDiagram
            class Animal {
                +String name
                +int age
                +makeSound() void
            }
        """
        
        # Complex diagram with relationships
        self.complex_diagram = """
        classDiagram
            class Animal {
                +String name
                +int age
                +makeSound() void
            }
            class Dog {
                +String breed
                +bark() void
            }
            Animal <|-- Dog : inherits
        """

    def test_parse_class_diagram_basic_success(self):
        """
        Test parsing a basic class diagram with single class.
        
        Pseudocode:
        1. Create basic Mermaid class diagram content
        2. Call parse_class_diagram()
        3. Verify returned data structure contains expected classes
        4. Verify class attributes and methods are parsed correctly
        5. Verify visibility modifiers are handled
        
        Expected behavior:
        - Should return dictionary with 'classes' key
        - Classes should contain name, attributes, methods
        - Visibility modifiers should be parsed correctly
        """
        # Test execution
        result = _mermaid_parser.parse_class_diagram(self.basic_diagram)
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertIn('classes', result)
        self.assertIn('relationships', result)
        self.assertIn('notes', result)
        self.assertIn('namespaces', result)
        
        # Verify class parsing
        classes = result['classes']
        self.assertEqual(len(classes), 1)
        
        animal_class = classes[0]
        self.assertEqual(animal_class['name'], 'Animal')
        self.assertEqual(len(animal_class['attributes']), 2)
        self.assertEqual(len(animal_class['methods']), 1)

    def test_parse_class_diagram_empty_content(self):
        """
        Test parsing with empty or None content.
        
        Pseudocode:
        1. Test with None content
        2. Test with empty string
        3. Test with whitespace-only string
        4. Verify ValueError is raised for all cases
        5. Verify error messages are descriptive
        
        Expected behavior:
        - Should raise ValueError for invalid content
        - Error message should indicate content cannot be empty
        """
        # Test None content
        with self.assertRaises(ValueError) as context:
            _mermaid_parser.parse_class_diagram(None)
        self.assertIn("Content cannot be empty", str(context.exception))
        
        # Test empty string
        with self.assertRaises(ValueError) as context:
            _mermaid_parser.parse_class_diagram("")
        self.assertIn("Content cannot be empty", str(context.exception))
        
        # Test whitespace only
        with self.assertRaises(ValueError) as context:
            _mermaid_parser.parse_class_diagram("   \n\t  ")
        self.assertIn("Content cannot be empty", str(context.exception))

    def test_parse_class_diagram_with_relationships(self):
        """
        Test parsing class diagram with relationships.
        
        Pseudocode:
        1. Create diagram with inheritance relationship
        2. Call parse_class_diagram()
        3. Verify relationships are parsed correctly
        4. Verify relationship types and labels
        5. Verify from/to class references
        
        Expected behavior:
        - Should parse inheritance relationships
        - Should identify relationship type correctly
        - Should capture relationship labels
        """
        # Test execution
        result = _mermaid_parser.parse_class_diagram(self.complex_diagram)
        
        # Verify relationships
        relationships = result['relationships']
        self.assertEqual(len(relationships), 1)
        
        relationship = relationships[0]
        self.assertEqual(relationship['from'], 'Animal')
        self.assertEqual(relationship['to'], 'Dog')
        self.assertEqual(relationship['type'], 'inheritance')
        self.assertEqual(relationship['label'], 'inherits')

    def test_parse_class_diagram_with_comments(self):
        """
        Test parsing diagram with comments.
        
        Pseudocode:
        1. Create diagram with %% comments
        2. Call parse_class_diagram()
        3. Verify comments are removed/ignored
        4. Verify diagram parsing continues normally
        5. Test both line comments and inline comments
        
        Expected behavior:
        - Comments should be stripped from content
        - Parsing should continue normally
        - Comments should not affect class definitions
        """
        diagram_with_comments = """
        %% This is a comment
        classDiagram
            %% Another comment
            class Animal {
                +String name %% inline comment
                +makeSound() void
            }
        """
        
        # Test execution
        result = _mermaid_parser.parse_class_diagram(diagram_with_comments)
        
        # Verify parsing succeeded despite comments
        self.assertIsInstance(result, dict)
        classes = result['classes']
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0]['name'], 'Animal')


class TestValidateSyntax(unittest.TestCase):
    """
    Comprehensive unit tests for the validate_syntax() function.
    
    Tests cover:
    - Valid Mermaid syntax validation
    - Invalid syntax detection
    - Brace balance checking
    - classDiagram directive validation
    - Edge cases and malformed input
    """

    def test_validate_syntax_valid_diagram(self):
        """
        Test syntax validation with valid diagrams.
        
        Pseudocode:
        1. Create valid Mermaid class diagram
        2. Call validate_syntax()
        3. Verify returns True
        4. Test multiple valid diagram variations
        5. Verify all pass validation
        
        Expected behavior:
        - Should return True for valid syntax
        - Should handle various valid patterns
        - Should accept properly balanced braces
        """
        valid_diagrams = [
            """
            classDiagram
                class Animal {
                    +String name
                }
            """,
            """
            classDiagram
                class Dog
                class Cat
                Dog --> Cat
            """,
            "classDiagram\nclass Simple"
        ]
        
        for diagram in valid_diagrams:
            with self.subTest(diagram=diagram[:50]):
                result = _mermaid_parser.validate_syntax(diagram)
                self.assertTrue(result)

    def test_validate_syntax_invalid_diagram(self):
        """
        Test syntax validation with invalid diagrams.
        
        Pseudocode:
        1. Create invalid Mermaid diagrams
        2. Call validate_syntax()
        3. Verify returns False
        4. Test missing directive, unbalanced braces, etc.
        5. Verify all fail validation
        
        Expected behavior:
        - Should return False for invalid syntax
        - Should detect missing classDiagram directive
        - Should detect unbalanced braces
        """
        invalid_diagrams = [
            "",  # Empty
            "class Animal",  # Missing classDiagram
            "classDiagram\nclass Animal { { }",  # Unbalanced braces
            "classDiagram\nclass Animal { } }",  # Extra closing brace
        ]
        
        for diagram in invalid_diagrams:
            with self.subTest(diagram=diagram[:50]):
                result = _mermaid_parser.validate_syntax(diagram)
                self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
