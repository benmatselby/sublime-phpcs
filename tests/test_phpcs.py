import os
import re
import sys
import sublime

from unittest import TestCase
from unittest.mock import patch

from Phpcs.phpcs import Sniffer


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
