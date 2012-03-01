import datetime
import os
import re
import subprocess
import time
import sublime
import sublime_plugin


def debug_message(msg):
    print "[Phpcs] " + msg

settings = sublime.load_settings('phpcs.sublime-settings')


class Pref:
    @staticmethod
    def load():
        Pref.phpcs_additional_args = settings.get('phpcs_additional_args', {})
        Pref.phpcs_execute_on_save = settings.get('phpcs_execute_on_save', {})
        Pref.phpcs_show_gutter_marks = settings.get('phpcs_show_gutter_marks')
        Pref.phpcs_show_quick_panel = settings.get('phpcs_show_quick_panel')
        Pref.phpcs_show_errors_in_status = settings.get('phpcs_show_errors_in_status')
        Pref.phpcs_display_errors_on_save = settings.get('phpcs_display_errors_on_save')

Pref.load()


class PhpcsTextBase(sublime_plugin.TextCommand):
    def run(self, args):
        debug_message('Not implemented')

    def is_php_buffer(self):
        if re.search('.+\PHP.tmLanguage', self.view.settings().get('syntax')):
            return True
        return False


class PhpcsCommand():
    # Instances, indexed on the view id.
    instances = {}

    # Return an existing instance for the given view, or create a new one.
    @staticmethod
    def instance(view):
        if view.id() not in PhpcsCommand.instances:
            PhpcsCommand.instances[view.id()] = PhpcsCommand(view)
        return PhpcsCommand.instances[view.id()]

    def __init__(self, view):
        self.view = view
        self.clear()

    def clear(self):
        self.checkstyle_report = []
        self.error_list = []
        self.region_set = []
        self.error_lines = {}

    def run(self, event=None):
        self.clear()
        self.event = event
        self.view.erase_regions("checkstyle")

        args = ['phpcs']
        args.append("--report=checkstyle")

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.phpcs_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        args.append(os.path.normpath(self.view.file_name()))

        self.execute(args)

    def execute(self, cmd):
        debug_message(' '.join(cmd))

        if sublime.platform() == "windows":
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        if proc.stdout:
            report = proc.communicate()[0]

            self.parse_report(report)

            if len(self.error_list) > 0:
                if Pref.phpcs_show_gutter_marks == True:
                    self.view.add_regions("checkstyle", self.region_set, "checkstyle", "dot", sublime.PERSISTENT)

                if Pref.phpcs_show_quick_panel == True:
                    if self.event == 'on_post_save' and not Pref.phpcs_display_errors_on_save:
                        return
                    self.show_quick_panel()
            else:
                debug_message("No phpcs sniff errors")

    def parse_report(self, report):
        # debug_message(report)
        lines = re.finditer('.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source', report)

        count = 0
        for line in lines:
            line_no = int(line.group('line')) - 1
            count += 1
            pt = self.view.text_point(int(line.group('line')) - 1, 0)
            self.region_set.append(sublime.Region(pt))
            self.error_list.append('(' + line.group('line') + ') ' + line.group('message'))
            self.checkstyle_report.append([line.group('line'), line.group('message'), pt])
            self.error_lines[line_no] = line.group('message')

        debug_message("Phpcs found " + str(count) + " errors")

    def show_quick_panel(self):
        self.view.window().show_quick_panel(self.error_list, self.on_quick_panel_done)

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        pt = self.checkstyle_report[picked][2]
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(pt))
        self.view.show(pt)


class PhpcsSniffThisFile(PhpcsTextBase):
    def run(self, edit):
        PhpcsCommand.instance(self.view).run()

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


class PhpcsShowPreviousErrorsCommand(PhpcsTextBase):
    def run(self, args):
        PhpcsCommand.instance(self.view).show_quick_panel()

    def description(self):
        if not self.is_php_buffer():
            return 'Invalid file format'
        else:
            return 'Show previous sniffer errors...'

    def is_enabled(self):
        return self.is_php_buffer() and \
            len(PhpcsCommand.instance(self.view).error_list) > 0


def update_statusbar(view, lineno, cmd):
    errors = []

    if lineno in cmd.error_lines:
        errors.append(cmd.error_lines[lineno])

    if errors:
        view.set_status('Phpcs', '; '.join(errors))
    else:
        view.erase_status('Phpcs')


class PhpcsEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if Pref.phpcs_execute_on_save == True:
            if re.search('.+\PHP.tmLanguage', view.settings().get('syntax')):
                PhpcsCommand.instance(view).run('on_post_save')

    def on_selection_modified(self, view):
        if not Pref.phpcs_show_errors_in_status:
            return

        if view.is_scratch():
            return

        # Only check in PHP contexts.
        if not re.search('.+\PHP.tmLanguage', view.settings().get('syntax')):
            return

        lastSelectedLineNo = view.rowcol(view.sel()[0].end())[0]

        cmd = PhpcsCommand.instance(view)

        update_statusbar(view, lastSelectedLineNo, cmd)
