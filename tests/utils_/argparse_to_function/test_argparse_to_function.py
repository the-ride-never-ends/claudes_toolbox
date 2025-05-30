import unittest
from argparse import ArgumentParser
from typing import Dict, Any

from argparse_docstring_generator import (
    extract_argument_traits,
    format_google_docstring,
    generate_function_signature_and_doc,
    DEFAULT_DB_PATH
)

class TestArgparseDocstringGenerator(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser(description="Test CLI")
        self.parser.add_argument("--flag", action="store_true", help="A boolean flag")
        self.parser.add_argument("--path", type=str, default="/tmp", help="A file path")
        self.parser.add_argument("--count", type=int, required=True, help="A required count")

        subparsers = self.parser.add_subparsers(dest="command", help="Subcommands")
        test_sub = subparsers.add_parser("sub", help="Subcommand example")
        test_sub.add_argument("--verbose", action="store_true", help="Enable verbosity")
        test_sub.add_argument("--limit", type=int, default=10, help="Limit value")

        self.structure: Dict[str, Any] = {
            "parser": {
                "description": self.parser.description,
                "arguments": extract_argument_traits(self.parser)
            }
        }

    def test_extract_argument_traits(self):
        args = self.structure["parser"]["arguments"]
        self.assertIn("flag", args)
        self.assertEqual(args["flag"]["action"], "_StoreTrueAction")
        self.assertEqual(args["path"]["default"], "/tmp")
        self.assertTrue(args["count"]["required"])

    def test_format_google_docstring(self):
        docstring = format_google_docstring(self.structure)
        self.assertIn("flag (bool)", docstring)
        self.assertIn("path (str), optional, default=/tmp", docstring)
        self.assertIn("count (int)", docstring)

    def test_generate_function_signature_and_doc(self):
        output = generate_function_signature_and_doc(self.structure)
        self.assertIn("def sub(", output)
        self.assertIn("flag: bool", output)
        self.assertIn("path: str = '/tmp'", output)
        self.assertIn("count: int", output)
        self.assertIn("verbose: bool", output)
        self.assertIn("limit: int = 10", output)

class TestArgparseEdgeCases(unittest.TestCase):

    def test_positional_and_nargs(self):
        parser = ArgumentParser(description="Edge case parser")
        parser.add_argument("positional", nargs="+", help="One or more positional args")
        parser.add_argument("--multi", nargs="*", help="Zero or more options")

        structure = {
            "parser": {
                "description": parser.description,
                "arguments": extract_argument_traits(parser)
            }
        }

        args = structure["parser"]["arguments"]
        self.assertIn("positional", args)
        self.assertEqual(args["positional"]["nargs"], "+")
        self.assertIn("multi", args)
        self.assertEqual(args["multi"]["nargs"], "*")

        output = generate_function_signature_and_doc(structure)
        self.assertIn("positional: str", output)  # should default to str
        self.assertIn("multi: str = None", output)  # nargs * often interpreted as list or optional

    def test_choices_type(self):
        parser = ArgumentParser(description="Choices and types")
        parser.add_argument("--mode", choices=["a", "b", "c"], help="Mode option")

        structure = {
            "parser": {
                "description": parser.description,
                "arguments": extract_argument_traits(parser)
            }
        }

        args = structure["parser"]["arguments"]
        self.assertIn("mode", args)
        self.assertIn("choices", args["mode"])
        self.assertEqual(args["mode"]["choices"], ["a", "b", "c"])

        output = generate_function_signature_and_doc(structure)
        self.assertIn("mode: str = None", output)

if __name__ == '__main__':
    unittest.main()
