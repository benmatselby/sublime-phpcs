import os
import re
import sys
import sublime
from unittest import TestCase


from Phpcs.phpcs import Sniffer


class TestDiffViewInternalFunctions(TestCase):
    def test_we_can_build_up_the_correct_executable_string_when_we_prefix(self):
        php_path = "/bin/php"
        s = sublime.load_settings("phpcs.sublime-settings")

        s.set("phpcs_php_prefix_path", php_path)
        s.set("phpcs_commands_to_php_prefix", "Sniffer")

        args = Sniffer().get_executable_args()
        self.assertIn(php_path, args)

    def test_we_can_build_up_the_correct_executable_string_when_we_dont_prefix(self):
        s = sublime.load_settings("phpcs.sublime-settings")

        s.set("phpcs_php_prefix_path", "/bin/php")
        s.set("phpcs_commands_to_php_prefix", "")
        s.set("phpcs_executable_path", "")

        args = Sniffer().get_executable_args()
        self.assertIn("phpcs", args)
