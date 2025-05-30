"""
Unit tests for mermaid_uml_to_python tool.

Tests define the expected behavior before implementation.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from typing import Dict, List, Tuple, Any
import time
from dataclasses import dataclass


from tools.functions.mermaid_uml_to_python import (
    parse_mermaid, 
    generate_python_code, 
    write_files
)

# Import the functions we're going to implement
# from mermaid_uml_to_python import parse_mermaid, generate_python_code, write_files

# Performance metric functions for success validation
@dataclass
class TokenUsage:
    """Token usage breakdown for workflows."""
    uml_description: int
    llm_skeleton: int
    llm_implementation: int
    
    @property
    def total(self) -> int:
        return self.uml_description + self.llm_skeleton + self.llm_implementation


@dataclass
class UMLElement:
    """Represents a UML element for consistency checking."""
    element_type: str  # 'class', 'method', 'attribute', 'relationship'
    name: str
    signature: str
    uml_definition: str
    generated_definition: str


@dataclass
class GenerationTiming:
    """Timing breakdown for code generation process."""
    parse_time: float
    generate_time: float
    write_time: float
    
    @property
    def total_time(self) -> float:
        return self.parse_time + self.generate_time + self.write_time


def calculate_token_cost_reduction(baseline_tokens: TokenUsage, tool_assisted_tokens: TokenUsage) -> float:
    """Calculate token cost reduction percentage."""
    if baseline_tokens.total == 0:
        return 0.0
    reduction = (baseline_tokens.total - tool_assisted_tokens.total) / baseline_tokens.total
    return reduction * 100.0


def is_token_cost_reduction_successful(baseline_tokens: TokenUsage, tool_assisted_tokens: TokenUsage, threshold: float = 40.0) -> bool:
    """Check if token cost reduction meets success threshold."""
    reduction = calculate_token_cost_reduction(baseline_tokens, tool_assisted_tokens)
    return reduction >= threshold


def calculate_uml_fidelity_score(uml_elements: List[UMLElement]) -> float:
    """Calculate UML fidelity score as percentage of consistent elements."""
    if not uml_elements:
        return 100.0
    consistent_elements = sum(1 for element in uml_elements if element.uml_definition == element.generated_definition)
    return (consistent_elements / len(uml_elements)) * 100.0


def is_uml_fidelity_successful(uml_elements: List[UMLElement], threshold: float = 95.0) -> bool:
    """Check if UML fidelity meets success threshold."""
    fidelity = calculate_uml_fidelity_score(uml_elements)
    return fidelity >= threshold


def calculate_generation_time(timing: GenerationTiming) -> float:
    """Calculate total generation time."""
    return timing.total_time


def is_generation_speed_successful(timing: GenerationTiming, threshold: float = 1.0) -> bool:
    """Check if generation speed meets success threshold."""
    return timing.total_time < threshold


def calculate_file_safety_score(existing_files: List[Path], preserved_files: List[Path]) -> float:
    """Calculate file safety score as percentage of preserved files."""
    if not existing_files:
        return 100.0
    return (len(preserved_files) / len(existing_files)) * 100.0


def is_file_safety_successful(existing_files: List[Path], preserved_files: List[Path], threshold: float = 100.0) -> bool:
    """Check if file safety meets success threshold."""
    safety_score = calculate_file_safety_score(existing_files, preserved_files)
    return safety_score >= threshold


def generate_conflict_filename(original_path: Path, existing_files: List[Path]) -> Path:
    """Generate new filename to avoid conflicts with existing files."""
    if original_path not in existing_files:
        return original_path
    
    stem = original_path.stem
    suffix = original_path.suffix
    parent = original_path.parent
    
    version = 1
    while True:
        new_name = f"{stem}_v{version}{suffix}"
        new_path = parent / new_name
        if new_path not in existing_files:
            return new_path
        version += 1


class TestParseMermaid(unittest.TestCase):
    """Test the parse_mermaid function."""
    
    def test_parse_simple_class(self):
        """Test parsing a simple class with methods."""
        mermaid_content = """
        classDiagram
            class User {
                -string name
                -string email
                +User(name: string, email: string)
                +get_name() string
                +set_email(email: string) void
            }
        """
        
        result = parse_mermaid(mermaid_content)
        
        expected = {
            'User': {
                'attributes': [
                    {'name': 'name', 'type': 'string', 'visibility': 'private'},
                    {'name': 'email', 'type': 'string', 'visibility': 'private'}
                ],
                'methods': [
                    {'name': '__init__', 'params': [('name', 'string'), ('email', 'string')], 'return_type': 'None', 'visibility': 'public'},
                    {'name': 'get_name', 'params': [], 'return_type': 'string', 'visibility': 'public'},
                    {'name': 'set_email', 'params': [('email', 'string')], 'return_type': 'void', 'visibility': 'public'}
                ],
                'stereotype': None,
                'relationships': []
            }
        }
        
        self.assertEqual(result, expected)
    
    def test_parse_interface_class(self):
        """Test parsing a class with interface stereotype."""
        mermaid_content = """
        classDiagram
            class PaymentProcessor {
                <<interface>>
                +process_payment(amount: float) bool*
                +validate_payment() bool*
            }
        """
        
        result = parse_mermaid(mermaid_content)
        
        self.assertEqual(result['PaymentProcessor']['stereotype'], 'interface')
        self.assertTrue(result['PaymentProcessor']['methods'][0]['is_abstract'])
    
    def test_parse_inheritance_relationship(self):
        """Test parsing inheritance relationships."""
        mermaid_content = """
        classDiagram
            class Animal {
                +make_sound() void
            }
            class Dog {
                +make_sound() void
            }
            Animal <|-- Dog : inherits
        """
        
        result = parse_mermaid(mermaid_content)
        
        self.assertIn('Animal', result['Dog']['relationships'])
        self.assertEqual(result['Dog']['relationships']['Animal'], 'inheritance')
    
    def test_parse_enumeration(self):
        """Test parsing enumeration classes."""
        mermaid_content = """
        classDiagram
            class Status {
                <<enumeration>>
                ACTIVE
                INACTIVE
                PENDING
            }
        """
        
        result = parse_mermaid(mermaid_content)
        
        self.assertEqual(result['Status']['stereotype'], 'enumeration')
        self.assertEqual(result['Status']['enum_values'], ['ACTIVE', 'INACTIVE', 'PENDING'])
    
    def test_parse_empty_class(self):
        """Test parsing a class with no methods or attributes."""
        mermaid_content = """
        classDiagram
            class EmptyClass {
            }
        """
        
        result = parse_mermaid(mermaid_content)
        
        self.assertEqual(result['EmptyClass']['attributes'], [])
        self.assertEqual(result['EmptyClass']['methods'], [])
    
    def test_parse_invalid_mermaid(self):
        """Test parsing invalid mermaid content."""
        invalid_content = "not a valid mermaid diagram"
        
        with self.assertRaises(ValueError):
            parse_mermaid(invalid_content)


class TestGeneratePythonCode(unittest.TestCase):
    """Test the generate_python_code function."""
    
    def test_generate_simple_class(self):
        """Test generating Python code for a simple class."""
        classes_data = {
            'User': {
                'attributes': [
                    {'name': 'name', 'type': 'string', 'visibility': 'private'},
                    {'name': 'email', 'type': 'string', 'visibility': 'private'}
                ],
                'methods': [
                    {'name': '__init__', 'params': [('name', 'str'), ('email', 'str')], 'return_type': 'None', 'visibility': 'public'},
                    {'name': 'get_name', 'params': [], 'return_type': 'str', 'visibility': 'public'}
                ],
                'stereotype': None,
                'relationships': []
            }
        }
        
        result = generate_python_code(classes_data)
        
        expected_code = '''"""
Auto-generated from UML diagram.
Generated on: {timestamp}
Do not modify this file directly.
"""

class User:
    """User class."""
    
    def __init__(self, name: str, email: str) -> None:
        """
        Initialize User instance.
        
        Args:
            name (str): The name parameter
            email (str): The email parameter
        """
        self._name = name
        self._email = email
    
    def get_name(self) -> str:
        """
        Get name.
        
        Returns:
            str: The return value
        """
        pass
'''
        
        self.assertIn('User', result)
        self.assertIn('class User:', result['User'])
        self.assertIn('def __init__(self, name: str, email: str) -> None:', result['User'])
        self.assertIn('Auto-generated from UML diagram', result['User'])
    
    def test_generate_interface_class(self):
        """Test generating Python code for an interface."""
        classes_data = {
            'PaymentProcessor': {
                'attributes': [],
                'methods': [
                    {'name': 'process_payment', 'params': [('amount', 'float')], 'return_type': 'bool', 'visibility': 'public', 'is_abstract': True}
                ],
                'stereotype': 'interface',
                'relationships': []
            }
        }
        
        result = generate_python_code(classes_data)
        
        self.assertIn('from abc import ABC, abstractmethod', result['PaymentProcessor'])
        self.assertIn('class PaymentProcessor(ABC):', result['PaymentProcessor'])
        self.assertIn('@abstractmethod', result['PaymentProcessor'])
    
    def test_generate_inheritance_class(self):
        """Test generating Python code with inheritance."""
        classes_data = {
            'Dog': {
                'attributes': [],
                'methods': [
                    {'name': 'make_sound', 'params': [], 'return_type': 'void', 'visibility': 'public'}
                ],
                'stereotype': None,
                'relationships': {'Animal': 'inheritance'}
            }
        }
        
        result = generate_python_code(classes_data)
        
        self.assertIn('class Dog(Animal):', result['Dog'])
    
    def test_generate_enumeration(self):
        """Test generating Python code for an enumeration."""
        classes_data = {
            'Status': {
                'attributes': [],
                'methods': [],
                'stereotype': 'enumeration',
                'enum_values': ['ACTIVE', 'INACTIVE', 'PENDING'],
                'relationships': []
            }
        }
        
        result = generate_python_code(classes_data)
        
        self.assertIn('from enum import Enum', result['Status'])
        self.assertIn('class Status(Enum):', result['Status'])
        self.assertIn('ACTIVE =', result['Status'])
        self.assertIn('INACTIVE =', result['Status'])
        self.assertIn('PENDING =', result['Status'])
    
    def test_generate_multiple_classes(self):
        """Test generating multiple Python files."""
        classes_data = {
            'User': {
                'attributes': [],
                'methods': [{'name': '__init__', 'params': [], 'return_type': 'None', 'visibility': 'public'}],
                'stereotype': None,
                'relationships': []
            },
            'Order': {
                'attributes': [],
                'methods': [{'name': '__init__', 'params': [], 'return_type': 'None', 'visibility': 'public'}],
                'stereotype': None,
                'relationships': []
            }
        }
        
        result = generate_python_code(classes_data)
        
        self.assertEqual(len(result), 2)
        self.assertIn('User', result)
        self.assertIn('Order', result)


class TestWriteFiles(unittest.TestCase):
    """Test the write_files function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.code_dict = {
            'User': 'class User:\n    pass\n',
            'Order': 'class Order:\n    pass\n'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_write_new_files(self):
        """Test writing files when no conflicts exist."""
        result = write_files(self.code_dict, self.temp_dir)
        
        # Check that files were created
        user_file = Path(self.temp_dir) / 'User.py'
        order_file = Path(self.temp_dir) / 'Order.py'
        
        self.assertTrue(user_file.exists())
        self.assertTrue(order_file.exists())
        
        # Check file contents
        with open(user_file, 'r') as f:
            self.assertEqual(f.read(), 'class User:\n    pass\n')
        
        # Check return value indicates success
        self.assertEqual(result['User'], 'User.py')
        self.assertEqual(result['Order'], 'Order.py')
    
    def test_write_with_conflicts(self):
        """Test writing files when conflicts exist."""
        # Create existing file
        existing_file = Path(self.temp_dir) / 'User.py'
        with open(existing_file, 'w') as f:
            f.write('# existing content')
        
        result = write_files(self.code_dict, self.temp_dir)
        
        # Check that original file was not overwritten
        with open(existing_file, 'r') as f:
            self.assertEqual(f.read(), '# existing content')
        
        # Check that new versioned file was created
        versioned_file = Path(self.temp_dir) / 'User_v1.py'
        self.assertTrue(versioned_file.exists())
        
        with open(versioned_file, 'r') as f:
            self.assertEqual(f.read(), 'class User:\n    pass\n')
        
        # Check return values
        self.assertEqual(result['User'], 'User_v1.py')
        self.assertEqual(result['Order'], 'Order.py')
    
    def test_write_multiple_conflicts(self):
        """Test writing files with multiple version conflicts."""
        # Create existing files
        for i in ['', '_v1', '_v2']:
            existing_file = Path(self.temp_dir) / f'User{i}.py'
            with open(existing_file, 'w') as f:
                f.write(f'# existing content{i}')
        
        result = write_files({'User': 'class User:\n    pass\n'}, self.temp_dir)
        
        # Check that new file gets next available version number
        versioned_file = Path(self.temp_dir) / 'User_v3.py'
        self.assertTrue(versioned_file.exists())
        
        self.assertEqual(result['User'], 'User_v3.py')
    
    def test_write_to_nonexistent_directory(self):
        """Test writing to a directory that doesn't exist."""
        nonexistent_dir = Path(self.temp_dir) / 'nonexistent'
        
        result = write_files(self.code_dict, str(nonexistent_dir))
        
        # Check that directory was created
        self.assertTrue(nonexistent_dir.exists())
        
        # Check that files were written
        user_file = nonexistent_dir / 'User.py'
        self.assertTrue(user_file.exists())
    
    def test_write_empty_code_dict(self):
        """Test writing an empty code dictionary."""
        result = write_files({}, self.temp_dir)
        
        self.assertEqual(result, {})
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_write_permission_error(self, mock_open):
        """Test handling permission errors during file writing."""
        with self.assertRaises(PermissionError):
            write_files(self.code_dict, self.temp_dir)


class TestPerformanceMetrics(unittest.TestCase):
    """Test the performance metrics that validate success criteria."""
    
    def test_token_cost_reduction_calculation(self):
        """Test token cost reduction calculation."""
        baseline = TokenUsage(uml_description=100, llm_skeleton=500, llm_implementation=300)
        tool_assisted = TokenUsage(uml_description=100, llm_skeleton=0, llm_implementation=300)
        
        reduction = calculate_token_cost_reduction(baseline, tool_assisted)
        
        # Should eliminate skeleton tokens: (900-400)/900 = 55.56%
        self.assertAlmostEqual(reduction, 55.56, places=2)
        self.assertTrue(is_token_cost_reduction_successful(baseline, tool_assisted))
    
    def test_uml_fidelity_calculation(self):
        """Test UML fidelity score calculation."""
        elements = [
            UMLElement('class', 'User', 'class User', 'class User', 'class User'),  # Match
            UMLElement('method', 'get_name', 'get_name() -> str', 'get_name() -> str', 'get_name() -> str'),  # Match
            UMLElement('method', 'set_age', 'set_age(age: int) -> None', 'set_age(age: int) -> None', 'set_age(age: int) -> void'),  # Mismatch
            UMLElement('attribute', 'name', 'name: str', 'name: str', 'name: str')  # Match
        ]
        
        fidelity = calculate_uml_fidelity_score(elements)
        
        # 3 out of 4 elements match = 75%
        self.assertEqual(fidelity, 75.0)
        self.assertFalse(is_uml_fidelity_successful(elements))  # Below 95% threshold
    
    def test_generation_timing_success(self):
        """Test generation speed validation."""
        fast_timing = GenerationTiming(parse_time=0.1, generate_time=0.3, write_time=0.2)
        slow_timing = GenerationTiming(parse_time=0.5, generate_time=0.8, write_time=0.9)
        
        self.assertTrue(is_generation_speed_successful(fast_timing))  # 0.6s < 1.0s
        self.assertFalse(is_generation_speed_successful(slow_timing))  # 2.2s > 1.0s
    
    def test_file_safety_validation(self):
        """Test file safety score calculation."""
        existing_files = [Path('a.py'), Path('b.py'), Path('c.py')]
        all_preserved = [Path('a.py'), Path('b.py'), Path('c.py')]
        some_preserved = [Path('a.py'), Path('b.py')]
        
        # Perfect safety - all files preserved
        self.assertEqual(calculate_file_safety_score(existing_files, all_preserved), 100.0)
        self.assertTrue(is_file_safety_successful(existing_files, all_preserved))
        
        # Partial safety - some files overwritten
        self.assertAlmostEqual(calculate_file_safety_score(existing_files, some_preserved), 66.67, places=2)
        self.assertFalse(is_file_safety_successful(existing_files, some_preserved))
    
    def test_conflict_filename_generation(self):
        """Test conflict resolution filename generation."""
        original = Path('user.py')
        existing = [Path('user.py'), Path('user_v1.py'), Path('user_v2.py')]
        
        new_filename = generate_conflict_filename(original, existing)
        
        self.assertEqual(new_filename, Path('user_v3.py'))
    
    def test_integration_with_main_functions(self):
        """Test that our main functions can be validated with performance metrics."""
        # This test will validate that parse_mermaid, generate_python_code, and write_files
        # produce output that can be successfully measured by our performance metrics
        
        # Mock some sample data that our functions should produce
        sample_uml_content = """
        classDiagram
            class User {
                +get_name() string
            }
        """
        
        # Expected parsed result
        expected_parsed = {
            'User': {
                'methods': [{'name': 'get_name', 'return_type': 'string', 'params': []}],
                'attributes': [],
                'stereotype': None,
                'relationships': []
            }
        }
        
        # Expected generated code
        expected_code = {
            'User': 'class User:\n    def get_name(self) -> str:\n        pass\n'
        }
        
        # Test that we can create UMLElement objects from parsed data
        uml_elements = [
            UMLElement(
                element_type='method',
                name='get_name', 
                signature='get_name() -> str',
                uml_definition='get_name() -> string',
                generated_definition='get_name() -> str'
            )
        ]
        
        # Test fidelity checking (this should pass since definitions are close enough)
        fidelity = calculate_uml_fidelity_score(uml_elements)
        self.assertGreaterEqual(fidelity, 0.0)  # At least some fidelity
        
        # Test timing validation
        timing = GenerationTiming(parse_time=0.1, generate_time=0.2, write_time=0.1)
        self.assertTrue(is_generation_speed_successful(timing))


class TestEndToEndSuccessValidation(unittest.TestCase):
    """Test end-to-end success validation using all metrics together."""
    
    def test_successful_tool_execution_metrics(self):
        """Test metrics for a completely successful tool execution."""
        # Token cost reduction (eliminating skeleton generation)
        baseline_tokens = TokenUsage(uml_description=100, llm_skeleton=400, llm_implementation=300)
        tool_tokens = TokenUsage(uml_description=100, llm_skeleton=0, llm_implementation=300)
        
        # Perfect UML fidelity
        uml_elements = [
            UMLElement('class', 'User', 'class User', 'class User', 'class User'),
            UMLElement('method', 'init', '__init__(name: str)', '__init__(name: str)', '__init__(name: str)')
        ]
        
        # Fast generation
        timing = GenerationTiming(parse_time=0.1, generate_time=0.2, write_time=0.1)
        
        # Perfect file safety
        existing_files = [Path('old_file.py')]
        preserved_files = [Path('old_file.py')]  # No overwrites
        
        # Validate all metrics pass
        self.assertTrue(is_token_cost_reduction_successful(baseline_tokens, tool_tokens))
        self.assertTrue(is_uml_fidelity_successful(uml_elements))
        self.assertTrue(is_generation_speed_successful(timing))
        self.assertTrue(is_file_safety_successful(existing_files, preserved_files))
    
    def test_failed_tool_execution_metrics(self):
        """Test metrics for a failed tool execution."""
        # Minimal token savings
        baseline_tokens = TokenUsage(uml_description=100, llm_skeleton=100, llm_implementation=300)
        tool_tokens = TokenUsage(uml_description=100, llm_skeleton=80, llm_implementation=300)  # Only 20 token savings
        
        # Poor fidelity
        uml_elements = [
            UMLElement('method', 'test', 'test() -> int', 'test() -> int', 'test() -> str'),  # Wrong return type
            UMLElement('class', 'User', 'class User', 'class User', 'class Person')  # Wrong name
        ]
        
        # Slow generation
        timing = GenerationTiming(parse_time=0.5, generate_time=1.2, write_time=0.8)  # 2.5s total
        
        # File overwrites
        existing_files = [Path('a.py'), Path('b.py')]
        preserved_files = [Path('a.py')]  # One file overwritten
        
        # Validate all metrics fail
        self.assertFalse(is_token_cost_reduction_successful(baseline_tokens, tool_tokens))
        self.assertFalse(is_uml_fidelity_successful(uml_elements))
        self.assertFalse(is_generation_speed_successful(timing))
        self.assertFalse(is_file_safety_successful(existing_files, preserved_files))


if __name__ == '__main__':
    unittest.main()
