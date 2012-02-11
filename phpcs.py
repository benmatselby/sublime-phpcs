import datetime
import functools
import os
import re
import subprocess
import time
import thread
import sublime
import sublime_plugin
from xml.dom.minidom import parse, parseString


class Pref:
    def load(self):
        settings = sublime.load_settings('phpcs.sublime-settings')
        Pref.phpcs_additional_args = settings.get('phpcs_additional_args', {})
        Pref.phpcs_execute_on_save = settings.get('phpcs_execute_on_save', {})
        Pref.phpcs_show_gutter_marks = settings.get('phpcs_show_gutter_marks')
        Pref.phpcs_show_quick_panel = settings.get('phpcs_show_quick_panel')

Pref().load()


class ActiveFile:
    searched_folders = {}
    search_results_cache = {}
    last_search_time = None


class ActiveView(ActiveFile):
    def is_php_buffer(self):
        # is this a PHP buffer?
        if re.search('.+\PHP.tmLanguage', self.view.settings().get('syntax')):
            return True
        return False

    def file_name(self):
        return self.view.file_name()


class PhpcsTextBase(sublime_plugin.TextCommand, ActiveView):
    def run(self, args):
        print 'Not implemented'


class PhpcsCommand():
    def __init__(self, window):
        self.window = window
        self.checkstyleData = []

    def run(self, path):

        self.window.active_view().erase_regions("checkstyle")
        if os.path.isdir(path):
            dir = path
        else:
            dir = os.path.dirname(path)
        target = path

        cmd = "cd '" + dir + "' && phpcs --report=checkstyle"

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.phpcs_additional_args.items():
            cmd = cmd + " " + key
            if value != "":
                cmd = cmd + "=" + value

        cmd = cmd + " '" + path + "'"
        self.execute(cmd)

    def execute(self, cmd):
        print cmd
        proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        if proc.stdout:
            regionSet = []
            errorList = []
            data = proc.communicate()[0]
            print data
            dataXml = parseString(data)

            files = dataXml.getElementsByTagName("file")

            for fileXml in files:
                errors = fileXml.getElementsByTagName("error")
                for errorXml in errors:
                    line = errorXml.getAttribute("line")
                    message = "(" + line + ") - " + errorXml.getAttribute("message")

                    pt = self.window.active_view().text_point(int(line) - 1, 0)

                    regionSet.append(sublime.Region(pt))
                    errorList.append(message)
                    self.checkstyleData.append([line, message, pt])

            if data != "":
                if Pref.phpcs_show_gutter_marks == True:
                    self.window.active_view().add_regions("checkstyle", regionSet, "checkstyle", "dot", sublime.PERSISTENT)

                if Pref.phpcs_show_quick_panel == True and len(errorList) > 0:
                    self.window.active_view().window().show_quick_panel(errorList, self.on_quick_panel_done)
            else:
                print "no phpcs sniff errors"

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        pt = self.checkstyleData[picked][2]
        self.window.active_view().sel().clear()
        self.window.active_view().sel().add(sublime.Region(pt))
        self.window.active_view().show(pt)


class PhpcsSniffThisFile(PhpcsTextBase):
    def run(self, args):
        print "Running PhpcsSniffThisFile"

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
