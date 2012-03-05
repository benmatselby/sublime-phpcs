import datetime
import os
import re
import subprocess
import time
import sublime
import sublime_plugin


settings = sublime.load_settings('phpcs.sublime-settings')

class Pref:
    @staticmethod
    def load():
        Pref.phpcs_additional_args = settings.get('phpcs_additional_args', {})
        Pref.phpcs_execute_on_save = bool(settings.get('phpcs_execute_on_save'))
        Pref.phpcs_show_errors_on_save = bool(settings.get('phpcs_show_errors_on_save'))
        Pref.phpcs_show_gutter_marks = bool(settings.get('phpcs_show_gutter_marks'))
        Pref.phpcs_show_errors_in_status = bool(settings.get('phpcs_show_errors_in_status'))
        Pref.phpcs_show_quick_panel = bool(settings.get('phpcs_show_quick_panel'))
        Pref.phpcs_linter_run = bool(settings.get('phpcs_linter_run'))
        Pref.phpcs_linter_regex = settings.get('phpcs_linter_regex')
        Pref.phpcs_executable_path = settings.get('phpcs_executable_path')

Pref.load()

settings.add_on_change('phpcs_additional_args', lambda:Pref().load())
settings.add_on_change('phpcs_execute_on_save', lambda:Pref().load())
settings.add_on_change('phpcs_show_errors_on_save', lambda:Pref().load())
settings.add_on_change('phpcs_show_gutter_marks', lambda:Pref().load())
settings.add_on_change('phpcs_show_errors_in_status', lambda:Pref().load())
settings.add_on_change('phpcs_show_quick_panel', lambda:Pref().load())
settings.add_on_change('phpcs_linter_run', lambda:Pref().load())
settings.add_on_change('phpcs_linter_regex', lambda:Pref().load())


def debug_message(msg):
    print "[Phpcs] " + msg


class CheckstyleError():
    """Represents an error that needs to be displayed on the UI for the user"""
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def get_line(self):
        return self.line

    def get_message(self):
        return self.message

    def set_point(self, point):
        self.point = point

    def get_point(self):
        return self.point


class ShellCommand():
    """Base class for shelling out a command to the terminal"""
    def __init__(self):
        self.error_list = []

    def get_errors(self, path):
        self.execute(path)
        return self.error_list

    def shell_out(self, cmd):
        data = None
        debug_message(' '.join(cmd))

        if sublime.platform() == "windows":
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        if proc.stdout:
            data = proc.communicate()[0]

        return data

    def execute(self, path):
        debug_message('Command not implemented')


class Sniffer(ShellCommand):
    """Concrete class for PHP_CodeSniffer"""
    def execute(self, path):
        if Pref.phpcs_executable_path != "":
            args = [Pref.phpcs_executable_path]
        else:
            args = ['phpcs']

        args.append("--report=checkstyle")

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.phpcs_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        args.append(os.path.normpath(path))
        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source', report)

        for line in lines:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)


class Linter(ShellCommand):
    """Content class for php -l"""
    def execute(self, path):
        if Pref.phpcs_linter_run != True:
            return

        args = ["php"]
        args.append("-l")
        args.append("-d display_errors=On")
        args.append(os.path.normpath(path))

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        line = re.search(Pref.phpcs_linter_regex, report)
        if line != None:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)


class PhpcsCommand():
    """Main plugin class for building the checkstyle report"""
    def __init__(self, window):
        self.window = window
        self.checkstyle_reports = []
        self.report = []
        self.event = None

    def run(self, path, event=None):
        self.event = event
        self.checkstyle_reports.append(['Linter', Linter().get_errors(path), 'cross'])
        self.checkstyle_reports.append(['Sniffer', Sniffer().get_errors(path), 'dot'])
        self.generate()

    def generate(self):
        error_list = []
        region_set = []

        for shell_command, report, icon in self.checkstyle_reports:
            self.window.active_view().erase_regions('checkstyle')
            self.window.active_view().erase_regions(shell_command)

            debug_message(shell_command + ' found ' + str(len(report)) + ' errors')
            for error in report:
                pt = self.window.active_view().text_point(int(error.get_line()) - 1, 0)
                region_set.append(sublime.Region(pt))
                error_list.append('(' + error.get_line() + ') ' + error.get_message())
                error.set_point(pt)
                self.report.append(error)

            if len(error_list) > 0:
                if Pref.phpcs_show_gutter_marks == True:
                    self.window.active_view().add_regions(shell_command, region_set, shell_command, icon)

        if Pref.phpcs_show_quick_panel == True:
            # Skip showing the errors if we ran on save, and the option isn't set.
            if self.event == 'on_save' and not Pref.phpcs_show_errors_on_save:
                return
            self.window.active_view().window().show_quick_panel(error_list, self.on_quick_panel_done)

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        pt = self.report[picked].get_point()
        self.window.active_view().sel().clear()
        self.window.active_view().sel().add(sublime.Region(pt))
        self.window.active_view().show(pt)


class PhpcsTextBase(sublime_plugin.TextCommand):
    """Base class for Text commands in the plugin, mainly here to check php files"""
    def run(self, args):
        debug_message('Not implemented')

    def is_php_buffer(self):
        if re.search('.+\PHP.tmLanguage', self.view.settings().get('syntax')):
            return True
        return False


class PhpcsSniffThisFile(PhpcsTextBase):
    """Command to sniff the open file"""
    def run(self, args):
        cmd = PhpcsCommand(self.view.window())
        cmd.run(self.view.file_name())

    def description(self):
        if not self.is_php_buffer():
            return "Invalid file format"
        else:
            return 'Sniff this file...'

    def is_enabled(self):
        if not self.is_php_buffer():
            return False
        return True


class PhpcsClearSnifferMarksCommand(PhpcsTextBase):
    def run(self, args):
        self.view.erase_regions("checkstyle")

    def description(self):
        if not self.is_php_buffer():
            return "Invalid file format"
        else:
            return 'Clear sniffer marks...'

    def is_enabled(self):
        if not self.is_php_buffer():
            return False
        return True


class PhpcsEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):

        if Pref.phpcs_execute_on_save == True:

            if re.search('.+\PHP.tmLanguage', view.settings().get('syntax')):

                PhpcsCommand(view.window()).run(view.file_name(), 'on_save')
