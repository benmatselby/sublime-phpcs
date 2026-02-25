from unittest import TestCase
from unittest.mock import patch

import sublime

from Phpcs.phpcs import Pref, Sniffer


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
