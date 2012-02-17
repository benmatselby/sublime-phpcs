import datetime
import os
import re
import subprocess
import time
import sublime
import sublime_plugin

settings = sublime.load_settings('phpcs.sublime-settings')

class Pref:
    def load(self):

        print "Loading phpcs settings"
        Pref.phpcs_additional_args = settings.get('phpcs_additional_args', {})
        Pref.phpcs_execute_on_save = settings.get('phpcs_execute_on_save', {})
        Pref.phpcs_show_gutter_marks = settings.get('phpcs_show_gutter_marks')
        Pref.phpcs_show_quick_panel = settings.get('phpcs_show_quick_panel')

Pref().load()

settings.add_on_change('phpcs_additional_args', lambda:Pref().load())
settings.add_on_change('phpcs_execute_on_save', lambda:Pref().load())
settings.add_on_change('phpcs_show_gutter_marks', lambda:Pref().load())
settings.add_on_change('phpcs_show_quick_panel', lambda:Pref().load())


class PhpcsTextBase(sublime_plugin.TextCommand):
    def run(self, args):
        print 'Not implemented'

    def is_php_buffer(self):
        # is this a PHP buffer?
        if re.search('.+\PHP.tmLanguage', self.view.settings().get('syntax')):
            return True
        return False


class PhpcsCommand():
    def __init__(self, window):
        self.window = window
        self.checkstyle_report = []
        self.error_list = []
        self.region_set = []

    def run(self, path):

        self.window.active_view().erase_regions("checkstyle")

        args = ['phpcs']
        args.append("--report=checkstyle")

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.phpcs_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        args.append(os.path.normpath(path))

        self.execute(args)

    def execute(self, cmd):
        print ' '.join(cmd)

        if sublime.platform() == "windows":
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        if proc.stdout:
            report = proc.communicate()[0]

            self.parse_report(report)

            if len(self.error_list) > 0:
                if Pref.phpcs_show_gutter_marks == True:
                    self.window.active_view().add_regions("checkstyle", self.region_set, "checkstyle", "dot", sublime.PERSISTENT)

                if Pref.phpcs_show_quick_panel == True:
                    self.window.active_view().window().show_quick_panel(self.error_list, self.on_quick_panel_done)
            else:
                print "No phpcs sniff errors"

    def parse_report(self, report):
        print report
        lines = re.finditer('.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source', report)

        count = 0
        for line in lines:
            count += 1
            pt = self.window.active_view().text_point(int(line.group('line')) - 1, 0)
            self.region_set.append(sublime.Region(pt))
            self.error_list.append('(' + line.group('line') + ') ' + line.group('message'))
            self.checkstyle_report.append([line.group('line'), line.group('message'), pt])

        "Phpcs found " + str(count) + " errors"

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        pt = self.checkstyle_report[picked][2]
        self.window.active_view().sel().clear()
        self.window.active_view().sel().add(sublime.Region(pt))
        self.window.active_view().show(pt)


class PhpcsSniffThisFile(PhpcsTextBase):
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

                view.window().run_command("phpcs_sniff_this_file")
