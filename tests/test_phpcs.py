import os
from unittest import TestCase
from unittest.mock import patch

import sublime

from Phpcs.phpcs import (
    CodeBeautifier,
    Fixer,
    Linter,
    MessDetector,
    Pref,
    Sniffer,
)


class TestSniffer(TestCase):
    def test_we_can_build_up_the_correct_executable_string_when_we_prefix(self):
        php_path = "/opt/homebrew/bin/php"
        s = sublime.load_settings("phpcs.sublime-settings")

        s.set("phpcs_php_prefix_path", php_path)
        s.set("phpcs_commands_to_php_prefix", "Sniffer")

        args = Sniffer().get_executable_args()
        self.assertIn(php_path, args)

    def test_we_can_build_up_the_correct_executable_string_when_we_dont_prefix(self):
        s = sublime.load_settings("phpcs.sublime-settings")

        s.set("phpcs_php_prefix_path", "/opt/homebrew/bin/php")
        s.set("phpcs_commands_to_php_prefix", "")
        s.set("phpcs_executable_path", "")

        args = Sniffer().get_executable_args()
        self.assertIn("phpcs", args)

    @patch("Phpcs.phpcs.Sniffer.shell_out")
    def test_we_can_parse_phpcs_standards_output(self, shell_mock):
        shell_mock.return_value = (
            "The installed coding standards are One, NeutronStandard, Two and Three"
        )
        standards = Sniffer().get_standards_available()

        expected = ["One", "NeutronStandard", "Two", "Three"]

        self.assertEqual(expected, standards)


class TestPrefPlatformResolution(TestCase):
    def setUp(self):
        self.pref = Pref()

    def test_string_value_passes_through_unchanged(self):
        result = self.pref._resolve_platform_value("/usr/bin/phpcs")
        self.assertEqual("/usr/bin/phpcs", result)

    def test_empty_string_passes_through_unchanged(self):
        result = self.pref._resolve_platform_value("")
        self.assertEqual("", result)

    def test_non_platform_dict_passes_through_unchanged(self):
        value = {"--standard": "PSR2", "-n": ""}
        result = self.pref._resolve_platform_value(value)
        self.assertEqual(value, result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="osx")
    def test_dict_resolves_to_osx_value(self, _):
        value = {
            "windows": "c:\\xampp\\php\\bin\\phpcs",
            "linux": "/usr/bin/phpcs",
            "osx": "/usr/local/bin/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("/usr/local/bin/phpcs", result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="linux")
    def test_dict_resolves_to_linux_value(self, _):
        value = {
            "windows": "c:\\xampp\\php\\bin\\phpcs",
            "linux": "/usr/bin/phpcs",
            "osx": "/usr/local/bin/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("/usr/bin/phpcs", result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="windows")
    def test_dict_resolves_to_windows_value(self, _):
        value = {
            "windows": "c:\\xampp\\php\\bin\\phpcs",
            "linux": "/usr/bin/phpcs",
            "osx": "/usr/local/bin/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("c:\\xampp\\php\\bin\\phpcs", result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="osx")
    def test_dict_falls_back_to_default_when_platform_missing(self, _):
        value = {
            "windows": "c:\\xampp\\php\\bin\\phpcs",
            "default": "/usr/bin/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("/usr/bin/phpcs", result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="osx")
    def test_dict_returns_empty_string_when_platform_and_default_missing(self, _):
        value = {
            "windows": "c:\\xampp\\php\\bin\\phpcs",
            "linux": "/usr/bin/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("", result)

    @patch("Phpcs.phpcs.sublime.platform", return_value="linux")
    def test_dict_prefers_platform_over_default(self, _):
        value = {
            "linux": "/usr/bin/phpcs",
            "default": "/opt/phpcs",
        }
        result = self.pref._resolve_platform_value(value)
        self.assertEqual("/usr/bin/phpcs", result)

    def test_none_value_passes_through(self):
        result = self.pref._resolve_platform_value(None)
        self.assertIsNone(result)

    def test_list_value_passes_through(self):
        value = ["Sniffer", "Fixer"]
        result = self.pref._resolve_platform_value(value)
        self.assertEqual(["Sniffer", "Fixer"], result)

    def test_boolean_value_passes_through(self):
        result = self.pref._resolve_platform_value(True)
        self.assertTrue(result)


class TestWorkingDirectory(TestCase):
    """Test that all tool classes set the working directory to the target file's directory."""

    def setUp(self):
        self.test_path = os.path.normpath(
            "/home/user/projects/myapp/src/Controller.php"
        )
        self.expected_dir = os.path.dirname(self.test_path)

    @patch("Phpcs.phpcs.Sniffer.shell_out", return_value="")
    def test_sniffer_sets_working_dir(self, _):
        s = sublime.load_settings("phpcs.sublime-settings")
        s.set("phpcs_sniffer_run", True)
        s.set("phpcs_executable_path", "/usr/bin/phpcs")
        s.set("phpcs_php_prefix_path", "")
        s.set("phpcs_additional_args", {})

        sniffer = Sniffer()
        sniffer.execute(self.test_path)
        self.assertEqual(self.expected_dir, sniffer.workingDir)

    @patch("Phpcs.phpcs.Fixer.shell_out", return_value="")
    def test_fixer_sets_working_dir(self, _):
        s = sublime.load_settings("phpcs.sublime-settings")
        s.set("php_cs_fixer_executable_path", "/usr/bin/php-cs-fixer")
        s.set("phpcs_php_prefix_path", "")
        s.set("php_cs_fixer_additional_args", {})

        fixer = Fixer()
        fixer.execute(self.test_path)
        self.assertEqual(self.expected_dir, fixer.workingDir)

    @patch("Phpcs.phpcs.CodeBeautifier.shell_out", return_value="")
    def test_code_beautifier_sets_working_dir(self, _):
        s = sublime.load_settings("phpcs.sublime-settings")
        s.set("phpcbf_executable_path", "/usr/bin/phpcbf")
        s.set("phpcs_php_prefix_path", "")
        s.set("phpcbf_additional_args", {})

        beautifier = CodeBeautifier()
        beautifier.execute(self.test_path)
        self.assertEqual(self.expected_dir, beautifier.workingDir)

    @patch("Phpcs.phpcs.MessDetector.shell_out", return_value="")
    def test_mess_detector_sets_working_dir(self, _):
        s = sublime.load_settings("phpcs.sublime-settings")
        s.set("phpmd_run", True)
        s.set("phpmd_executable_path", "/usr/bin/phpmd")
        s.set("phpcs_php_prefix_path", "")
        s.set("phpmd_additional_args", {})

        detector = MessDetector()
        detector.execute(self.test_path)
        self.assertEqual(self.expected_dir, detector.workingDir)

    @patch("Phpcs.phpcs.Linter.shell_out", return_value="")
    def test_linter_sets_working_dir(self, _):
        s = sublime.load_settings("phpcs.sublime-settings")
        s.set("phpcs_linter_run", True)
        s.set("phpcs_php_path", "/usr/bin/php")
        s.set("phpcs_linter_regex", "(?P<message>.*) on line (?P<line>\\d+)")

        linter = Linter()
        linter.execute(self.test_path)
        self.assertEqual(self.expected_dir, linter.workingDir)


class TestPrefVariableExpansion(TestCase):
    """Test that Sublime Text variables are expanded in setting values."""

    def setUp(self):
        self.pref = Pref()
        self.variables = {
            "project_path": "/home/user/projects/myapp",
            "folder": "/home/user/projects/myapp",
            "file": "/home/user/projects/myapp/src/Controller.php",
            "file_path": "/home/user/projects/myapp/src",
        }

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_string_with_project_path_is_expanded(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        result = self.pref._expand_variables("${project_path}/.php-cs-fixer.php")
        self.assertEqual("/home/user/projects/myapp/.php-cs-fixer.php", result)

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_string_with_folder_is_expanded(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        result = self.pref._expand_variables("${folder}/vendor/bin/phpcs")
        self.assertEqual("/home/user/projects/myapp/vendor/bin/phpcs", result)

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_string_without_variables_passes_through(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        result = self.pref._expand_variables("/usr/bin/phpcs")
        self.assertEqual("/usr/bin/phpcs", result)

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_empty_string_passes_through(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        result = self.pref._expand_variables("")
        self.assertEqual("", result)

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_dict_values_are_expanded_recursively(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        value = {"--config": "${project_path}/.php-cs-fixer.php", "-n": ""}
        result = self.pref._expand_variables(value)
        self.assertEqual(
            {"--config": "/home/user/projects/myapp/.php-cs-fixer.php", "-n": ""},
            result,
        )

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_boolean_value_passes_through(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        result = self.pref._expand_variables(True)
        self.assertTrue(result)

    @patch("Phpcs.phpcs.sublime.active_window")
    def test_list_value_is_expanded_recursively(self, mock_window):
        mock_window.return_value.extract_variables.return_value = self.variables
        value = ["Sniffer", "${project_path}/vendor/bin/phpcs"]
        result = self.pref._expand_variables(value)
        self.assertEqual(
            ["Sniffer", "/home/user/projects/myapp/vendor/bin/phpcs"], result
        )

    def test_returns_value_unchanged_when_no_window(self):
        with patch("Phpcs.phpcs.sublime.active_window", return_value=None):
            result = self.pref._expand_variables("${project_path}/.php-cs-fixer.php")
            self.assertEqual("${project_path}/.php-cs-fixer.php", result)
