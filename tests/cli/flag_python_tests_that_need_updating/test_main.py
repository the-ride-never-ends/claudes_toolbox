import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock


# Import the module that contains CommandLineInterface. Adjust the import path
# if the CLI code lives in a different location within your project.
from tools.cli.flag_python_tests_that_need_updating.main import CommandLineInterface


class CommandLineInterfaceArgumentTests(unittest.TestCase):
    """Unit tests for CommandLineInterface argument parsing and initialization."""

    def setUp(self):
        # Preserve the original command-line arguments so we can restore them in tearDown
        self._orig_argv = sys.argv.copy()

    def tearDown(self):
        # Always restore the original argv to avoid side-effects between tests
        sys.argv = self._orig_argv

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _build_cli(self, *cli_args: str) -> CommandLineInterface:
        """Instantiate CommandLineInterface with the given CLI arguments.

        Parameters
        ----------
        *cli_args: str
            All CLI tokens that should appear *after* the program name.
        """
        sys.argv = ["test_change_detector.py", *cli_args]
        return CommandLineInterface()

    # ------------------------------------------------------------------
    # Positive cases
    # ------------------------------------------------------------------
    def test_parse_arguments_accepts_long_form_path(self):
        """--path should populate both the parsed Namespace and instance attributes."""
        cli = self._build_cli("--path", "/tmp/project")

        # Check Namespace
        self.assertEqual(cli.args.path, "/tmp/project")
        self.assertFalse(cli.args.reset_state)

        # Check instance attrs
        self.assertEqual(cli.target_path, "/tmp/project")
        self.assertFalse(cli.reset_state)

    def test_parse_arguments_accepts_short_form_path(self):
        """-p should behave identically to --path."""
        cli = self._build_cli("-p", "/tmp/project")
        self.assertEqual(cli.args.path, "/tmp/project")
        self.assertEqual(cli.target_path, "/tmp/project")

    def test_parse_arguments_handles_reset_state_flag(self):
        """--reset-state should toggle reset_state to True."""
        cli = self._build_cli("--path", "/tmp/project", "--reset-state")
        self.assertTrue(cli.args.reset_state)
        self.assertTrue(cli.reset_state)

    # ------------------------------------------------------------------
    # Negative cases
    # ------------------------------------------------------------------
    def test_parse_arguments_requires_path(self):
        """Omitting --path/-p should raise SystemExit (argparse's behaviour)."""
        sys.argv = ["test_change_detector.py"]
        with self.assertRaises(SystemExit):
            CommandLineInterface()


class CommandLineInterfaceMainTests(unittest.TestCase):
    """Thin smoke-test for CommandLineInterface.main().

    Rather than exhaustively validating the orchestration logic here (that
    belongs in dedicated integration tests), we merely verify that main()
    delegates to the collaborating components that *should* exist based on
    the UML diagram. We patch those collaborators with mocks so the test
    remains independent of their concrete implementations. When the real
    code is written, these mocks ensure the call-chain remains intact.
    """

    def setUp(self):
        self._orig_argv = sys.argv.copy()
        sys.argv = [
            "test_change_detector.py",
            "--path",
            str(Path.cwd()),
        ]
        self.JSONOutputWriter = MagicMock()
        self.ReportBuilder = MagicMock()
        self.CodeAnalyzer = MagicMock()
        self.StateManager = MagicMock()

        configs = MagicMock()

        resources = {
            "JSONOutputWriter": self.JSONOutputWriter,
            "ReportBuilder": self.ReportBuilder,
            "CodeAnalyzer": self.CodeAnalyzer,
            "StateManager": self.StateManager,
        }

        # Create a CLI instance fresh for each test to avoid state bleed.
        self.cli = CommandLineInterface(resources=resources, configs=configs)

    def tearDown(self):
        sys.argv = self._orig_argv

    def test_main_orchestrates_all_components(
        self,
        mock_state_manager,
        mock_code_analyzer,
        mock_report_builder,
        mock_json_writer,
    ):
        """main() should instantiate the collaboration graph once each and call write_to_stdout()."""

        # Arrange ----------------------------------------------------------------
        # Configure mocks to provide minimal viable return values so main() can
        # execute without raising exceptions from attribute access.
        state_manager_instance = mock_state_manager.return_value
        state_manager_instance.load_state.return_value = {}
        state_manager_instance.current_state = {}

        code_analyzer_instance = mock_code_analyzer.return_value
        code_analyzer_instance.analyze_codebase.return_value = {}

        report_builder_instance = mock_report_builder.return_value
        report_builder_instance.build_report.return_value = {
            "changes": [],
            "metadata": {},
        }

        json_writer_instance = mock_json_writer.return_value

        # Act --------------------------------------------------------------------
        self.cli.main()

        # Assert -----------------------------------------------------------------
        mock_state_manager.assert_called_once()
        mock_code_analyzer.assert_called_once_with(str(Path.cwd()))
        mock_report_builder.assert_called_once_with([], {})
        json_writer_instance.write_to_stdout.assert_called_once_with(
            report_builder_instance.build_report.return_value
        )


if __name__ == "__main__":
    unittest.main()
