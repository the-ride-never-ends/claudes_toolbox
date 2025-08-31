
import ast
from pydantic import BaseModel, FilePath
from pathlib import Path

from enum import StrEnum


class CodeAntiPatternError(AssertionError):
    """Code contains one or more anti-patterns."""
    pass

class TestFileAntiPatternError(AssertionError):
    """A file test contains one or more test file anti-patterns."""
    pass

class TestAntiPatternError(AssertionError):
    """A test contains one or more testing anti-patterns."""
    pass



class ArchitectureAntiPatternError(AssertionError):
    """Code contains one or more architecture anti-patterns."""
    pass





# Test Anti-pattern errors
# See https://testsmells.org/pages/testsmells.html, 7-28-2025

class AssertionRouletteError(TestAntiPatternError):
    """Raised if a test has non-documented assertions.
    
    Example:
        def test_example():
            assert function_to_test() == expected_value  # No message provided
    """
    pass

class ConditionalTestLogicError(TestAntiPatternError):
    """Raised if a test contains one or more conditional logic statements.
    
    Example:
        def test_example():
            result = function_to_test()
            if result:
                assert function() == expected_value
            else:
                assert function() == another_expected_value
    """
    pass

class ConstructionInitializationError(TestAntiPatternError):
    """Raised if a test contains constructor initialization.
    
    Example:
        def test_example():
            obj = ClassName()  # Constructor initialization
            assert obj.method() == expected_value
    """
    pass

class DefaultTestError(TestAntiPatternError):
    """Raised if a test is an example of a test."
    
    Example:
        def test_example():
            pass  # No implementation provided
    """
    pass

class DuplicateAssertError(TestAntiPatternError):
    """Raised if a test checks the same condition multiple times within the same test method.
    
    Example:
        def test_example():
            value = 1
            assert method(value) == True  # First assert
            value = 2
            assert method(value) == True  # Duplicate assert, should raise an error
    """
    pass

class EagerTestError(TestAntiPatternError):
    """
    Raised if a test invokes more than one public method of a class.
    
    Example:
        def test_example():
            obj = ClassName()
            assert obj.some_method() == expected_value1
            assert obj.another_method() == expected_value2  # Invokes another method
    """
    pass

class EmptyTestError(TestAntiPatternError):
    """Raised if a test does not contain executable statements.
    
    Example:
        def test_example():
            pass  # No executable statements
    """
    pass

class ExceptionHandlingInTestError(TestAntiPatternError):
    """Raised if a test explicitly passes or fails based on the test itself throwing an exception.
    
    Example:
        def test_example():
            try:
                function_to_test()
            except ExpectedException:
                assert True  # Test passes if exception is raised
            else:
                assert False, "Expected exception was not raised"
    """
    pass

class GeneralFixtureError(TestAntiPatternError):
    """
    Raised if a test only accesses part of a fixture.

    Example:
        class TestExample:
        
            def setup_method(self):
                self.fixture = FixtureClass()  # Only accessing part of the fixture
                self.fixture.some_value = 42
                self.fixture.another_value = 100

            def test_example(self):
                assert self.fixture.some_value == 42
                assert self.fixture.another_value == 100

            def test_example(self):
                assert self.fixture.some_value == 42  # Only using some_value, not the entire fixture
    """
    pass

class IgnoredTestError(TestAntiPatternError):
    """
    Raised if a test is suppressed from running.
    
    Example:
        @pytest.mark.skip(reason="This test is ignored")
        def test_example():
            assert function_to_test() == expected_value  # This test will not run
    """
    pass

class LazyTestError(TestAntiPatternError):
    """
    Occurs when multiple test methods invoke the same method of the production object in the exact same way.
    
    Example:
        def test_example1():
            assert function_to_test() == expected_value1

        def test_example2():
            assert function_to_test() == expected_value2  # Invokes the same method as in test_example1
    """
    pass

class MagicNumberTestError(TestAntiPatternError):
    """Raised if a test uses assert statements that contains numeric literals (i.e., magic numbers) as parameters.

    They should be replaced with named constants or variables to improve readability and maintainability.

    Example:
        def test_example():
            assert function_to_test(420) == expected_value  # 420 is a magic number
    """
    pass

class MysteryGuestError(TestAntiPatternError):
    """
    Raised if a test uses external resources not created by the testing framework (e.g. files, database, etc.).
    Mocks, stubs, fakes, or temporary resources created by the testing framework should be used instead.

    Example:
        def test_example():
            with open('some_random_file.txt', 'r') as file:  # Using an external resource
                content = file.read()
            assert content == expected_value  # Test relies on an external file
    """
    pass

class RedundantPrintError(TestAntiPatternError):
    """Raised if a test contains print or logging statements.
    
    Example:
        def test_example():
            print("This is a debug message")  # Print statement in the test
            assert function_to_test() == expected_value

        def test_example():
            logging.debug("This is a debug message")  # Logging statement in the test
            assert function_to_test() == expected_value
    """
    pass

class RedundantAssertionError(TestAntiPatternError):
    """Raised if a test contains assertion statements that are always true or always false.
    
    Example:
        def test_example():
            assert True  # Always true, redundant assertion
            assert False  # Always false, redundant assertion
    """
    pass

class ResourceOptimismError(TestAntiPatternError):
    """Raised if a test does not confirm that an external resource (e.g., File) used by test method exists.
    
    Example:
        def test_example():
            some_mocked_resource = MockResource()  # Assuming this resource should exist
            assert function_to_test(some_mocked_resource) == expected_value  # Test assumes resource exists
    """
    pass

class SensitiveEqualityTests(TestAntiPatternError):
    """Raised if a test when the __str__ method is used within a test method.
    
    Example:
        assert str(obj) == "expected string"
    """
    pass

class SleepyTestError(TestAntiPatternError):
    """Raised if a test stops a thread during the test.
    
    Example:
        def test_example():
            time.sleep(1)  # Test stops the thread for 1 second
            assert function_to_test() == expected_value
    """
    pass

class UnknownTestError(TestAntiPatternError):
    """Raised if a test does not indicate that it is a test. This is confirmed by checking the following:
    - 1. Does not start with 'test_'.
    - 2. Does not contain the snake-case name of the callable being tested.
    - 3. Does not have have a "when" clause followed by a "then" clause.
    - 4. Does not contain a docstring with the GIVEN-WHEN-THEN format.
    - 5. Does not contain an assert statement.
    """
    pass


# Based on https://bytedev.medium.com/things-ive-learned-from-writing-a-lot-of-unit-tests-2d234d0cfccf, 7/28/2025

class TestIsTooLongError(TestAntiPatternError):
    """Raised if a test is over a preset number of lines of code, not including the docstring."""
    pass

class TestIsForNonPublicCallableError(TestAntiPatternError):
    """Raised if a test is for a non-public callable (i.e., starts with an underscore).
    
    Example:
        def test_example():
            assert _private_function() == expected_value  # Testing a non-public callable

        def test_example():
            obj = _PrivateClass()  # Testing a non-public class
            assert obj._private_method() == expected_value  # Testing a non-public method
    """
    pass




# Test File Anti-pattern errors

class TestFileContainsTooManyTestsError(TestFileAntiPatternError):
    """Raised if a test file contains more than a pre-set number of tests."""
    pass

class TestFileIsTooLongError(TestFileAntiPatternError):
    """Raised if a test file is over a pre-set number of lines, including docstrings."""
    pass

class ResourceOptimismTestFileError(TestFileAntiPatternError):
    """
    Raised if a test file does not confirm that an external resource exists. 
    This includes but is not limited to:
        - Files
        - Databases
        - Network resources
        - Imports (e.g., modules, packages, libraries, etc.)
        - Imported callables and their expected behavior.

    Example:
        import library # Test file does not confirm that library exists
        import local_module  # Test file does not confirm that external_module exists
        from local_module import function_to_test, ClassToTest  # Test file does not confirm that function_to_test exists

        def test_example():
            result = ClassToTest().method_to_test() # Test file does not confirm that method_to_test exists
            assert function_to_test() == True 
    """
    pass


class BrokenContractError(AssertionError):
    """Raised when a function or method contract is broken."""
    pass

class DeadCodeError(AssertionError):
    """Raised when public function or method is unreachable or unused in a codebase."""
    pass


class CheatingError(AssertionError):
    """
    An error indicating that a test has been written or changed to pass 
    without actually testing the functionality.
    """


class MockingCallableUnderTestError(CheatingError):
    """Raised when a test is not testing the actual callable, but rather a mock, stub, or fake."""
    pass

class ModifiedDocstringError(CheatingError):
    """Raised when a docstring is modified without consent from the developer."""
    pass

class ModifiedTestError(CheatingError):
    """Raised when a test implementation is modified without consent from the developer."""
    pass

class ModifiedFixtureError(CheatingError):
    """Raised when a fixture is modified without consent from the developer."""
    pass

class HardcodedReturnError(CheatingError):
    """
    Raised when a callable under tests returns values that match specific test inputs.
    
    Note that this is context-specific. It should be raised in cases where the callable 
        under test is expected to return different values based on its logic.
    """
    pass



class UnbalancedTestTypeRatioError(TestAntiPatternError):
    """Raised if the ratio of unit tests to integration tests falls outside the 70/20/10 rule."""
    pass


































def _get_ast_tree(file_path: Path) -> ast.AST:    
    """
    Parse a Python file and return its AST.
    
    Args:
        file_path: Path to the Python file.
    
    Returns:
        AST of the file.
    """
    try:
        with open(file_path.resolve(), 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        raise IOError(f"Failed to read file {file_path}: {e}") from e

    try:
        return ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        raise SyntaxError(f"Syntax error in file {file_path}: {e.msg} at line {e.lineno}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while parsing file {file_path}: {e}") from e

_MAX_NUM_TEST_LINES = 10

def _type_check_positive_int(value: int) -> None:
    """
    Check if the value is a positive integer.

    Args:
        value: The value to check.

    Raises:
        TypeError: If the value is not an integer.
        ValueError: If the value is negative.
    """
    if not isinstance(value, int):
        raise TypeError(f"Expected an integer, got '{value}' of type '{type(value).__name__}'.")
    if value <= 0:
        raise ValueError(f"Expected a positive integer, got {value}.")

def _type_check_test(test: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    """
    Check if the test is an AST FunctionDef or AsyncFunctionDef node.

    Args:
        test: The AST node representing the test function.

    Raises:
        TypeError: If the test is not an AST FunctionDef or AsyncFunctionDef node.
    """
    if not isinstance(test, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise TypeError(f"Expected an AST FunctionDef or AsyncFunctionDef node, got '{test}'.")

def _raise_if_test_is_too_long(
        test: ast.FunctionDef | ast.AsyncFunctionDef, 
        max_length: int = _MAX_NUM_TEST_LINES
        ) -> None:
    """
    Check if a test function is too long.

    Args:
        test: The AST node representing the test function.
        max_length: Maximum allowed number of lines in the test function.

    Raises:
        TestIsTooLongError: If the test function exceeds the maximum allowed length.
        TypeError: If the test is not an AST FunctionDef or AsyncFunctionDef node, 
            or if max_length is not an integer.
        ValueError: If max_length is less than or equal to zero.
    """


    _type_check_test(test)
    _type_check_positive_int(max_length)

    # Count the number of lines in the test body
    if len(test.body) > max_length:
        raise TestIsTooLongError(
            f"Test function '{test.name}' exceeds the maximum allowed length of {max_length} lines."
        )

def _raise_if_test_is_for_non_public_callable(
        test: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> None:
    """
    Check if a test is for a non-public callable.

    Args:
        test: The AST node representing the test function.
        callable_name: The name of the callable being tested.

    Raises:
        InternalMethodError: If the test is for a non-public callable (i.e., starts with an underscore).
        TypeError: If the test is not an AST FunctionDef or AsyncFunctionDef node.
    """
    _type_check_test(test)

    # Look in the code's body for the callable name
    callable_name = None
    for node in ast.walk(test):
        if isinstance(node, ast.Call):
            match node.func:
                case ast.Name():  # Direct function call like function_name()
                    if node.func.id.startswith('_'):
                        callable_name = node.func.id
                        break
                case ast.Attribute(): # Method call like obj.method_name()
                    if node.func.attr.startswith('_'):
                        callable_name = node.func.attr
                        break

    if callable_name is not None:
        raise TestIsForNonPublicCallableError(
            f"Test function '{test.name}' is testing a non-public callable '{callable_name}' "
            f"(starts with underscore)."
        )







def raise_if_test_contains_an_anti_pattern(
    *,
    test: ast.FunctionDef | ast.AsyncFunctionDef,
    module_ast: ast.AST
    ) -> None:
    """
    Check if a test contains a testing anti-pattern.

    These include:
        - Has more than one assert statement in its body.
        - Has assert statements that are always true or false.
        - Has assert statements that evaluate against numeric literals (i.e. magic numbers)
        - Has assert statements that do not have a message indicating the reason for a failure of the assert.
        - Contains conditional logic (e.g. "if", "while", etc.).
        - Does not explicitly set default values for the parameters of the callable being tested.
        - Contains constructor initialization.
        - Invokes more than one callable from a class or module.
        - Invokes the same callable multiple times.
        - Contains print or logging statements.
        - Does not contain executable statements.
        - Is suppressed from running or skipped.
        - Uses external resources not directly created by the testing framework (e.g. files, database, etc.).
        - Accesses only part of a fixture if a fixture is used.
        - Does not confirm that an external resource used by the test method exists.
        - Contains a test that does not clearly indicate that it is a test.

    Args:
        test: The AST node representing the test function.


    Raises:

    
    
    """


def _raise_if_test_contains_duplicate_assert(
    test: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
    """
    Check if a test contains duplicate assert statements.

    Args:
        test: The AST node representing the test function.

    Raises:
        DuplicateAssertError: If the test contains duplicate assert statements.

    Example:
        # Example of a test with duplicate assert statements
        def test_example():
            value = 1
            assert method(value) == True  # First assert
            value = 2
            assert method(value) == True  # Duplicate assert, should raise an error
    """


    _type_check_test(test)

    list_of_asserts = []

    for node in ast.walk(test):
        if isinstance(node, ast.Assert):
            # Convert the assert condition to a string representation
            assert_str = ast.dump(node.test)

            if assert_str in list_of_asserts:
                raise DuplicateAssertError(
                    f"Test function '{test.name}' contains duplicate assert statements."
                )
            else:
                list_of_asserts.append(assert_str)


class PythonFile(BaseModel):
    file_path: FilePath
    tree: ast.AST
    checks: list[StrEnum]


class TestFile(BaseModel):
    """
    Represents a test file with its path and content.
    """

    def validate_consumer_contract():
        pass

    def validate_producer_contract():
        pass



