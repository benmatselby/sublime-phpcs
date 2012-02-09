import datetime
import functools
import os
import re
import subprocess
import time
import thread
import sublime
import sublime_plugin


class Pref:
    def load(self):
        settings = sublime.load_settings('phpcs.sublime-settings')
        Pref.phpcs_additional_args = settings.get('phpcs_additional_args', {})
        Pref.phpcs_execute_on_save = settings.get('phpcs_execute_on_save', {})

Pref().load()


# the AsyncProcess class has been cribbed from:
# https://github.com/maltize/sublime-text-2-ruby-tests/blob/master/run_ruby_test.py
class AsyncProcess(object):
    def __init__(self, cmd, listener):
        self.cmd = cmd
        self.listener = listener
        print "DEBUG_EXEC: " + self.cmd
        self.proc = subprocess.Popen([self.cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.proc.stdout:
            thread.start_new_thread(self.read_stdout, ())
        if self.proc.stderr:
            thread.start_new_thread(self.read_stderr, ())

    def read_stdout(self):
        while True:
            data = os.read(self.proc.stdout.fileno(), 2 ** 15)
            if data != "":
                sublime.set_timeout(functools.partial(self.listener.append_data, self.proc, data), 0)
            else:
                self.proc.stdout.close()
                self.listener.is_running = False
                break

    def read_stderr(self):
        while True:
            data = os.read(self.proc.stderr.fileno(), 2 ** 15)
            if data != "":
                sublime.set_timeout(functools.partial(self.listener.append_data, self.proc, data), 0)
            else:
                self.proc.stderr.close()
                self.listener.is_running = False
                self.listener.append_data(self.proc, "\n--- PROCESS COMPLETE ---")
                break


# the StatusProcess class has been cribbed from:
# https://github.com/maltize/sublime-text-2-ruby-tests/blob/master/run_ruby_test.py
class StatusProcess(object):
    def __init__(self, msg, listener):
        self.msg = msg
        self.listener = listener
        thread.start_new_thread(self.run_thread, ())

    def run_thread(self):
        progress = ""
        while True:
            if self.listener.is_running:
                if len(progress) >= 10:
                    progress = ""
                progress += "."
                sublime.set_timeout(functools.partial(self.listener.update_status, self.msg, progress), 0)
                time.sleep(1)
            else:
                break


class OutputView(object):
    def __init__(self, name, window):
        self.output_name = name
        self.window = window

    def show_output(self):
        self.ensure_output_view()
        self.window.run_command("show_panel", {"panel": "output." + self.output_name})

    def show_empty_output(self):
        self.ensure_output_view()
        self.clear_output_view()
        self.show_output()

    def ensure_output_view(self):
        if not hasattr(self, 'output_view'):
            self.output_view = self.window.get_output_panel(self.output_name)

    def clear_output_view(self):
        self.ensure_output_view()
        self.output_view.set_read_only(False)
        edit = self.output_view.begin_edit()
        self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
        self.output_view.end_edit(edit)
        self.output_view.set_read_only(True)

    def append_data(self, proc, data):
        str = data.decode("utf-8")
        str = str.replace('\r\n', '\n').replace('\r', '\n')

        selection_was_at_end = (len(self.output_view.sel()) == 1
          and self.output_view.sel()[0]
            == sublime.Region(self.output_view.size()))
        self.output_view.set_read_only(False)
        edit = self.output_view.begin_edit()
        self.output_view.insert(edit, self.output_view.size(), str)
        if selection_was_at_end:
            self.output_view.show(self.output_view.size())
        self.output_view.end_edit(edit)
        self.output_view.set_read_only(True)


class CommandBase:
    def __init__(self, window):
        self.window = window

    def show_output(self):
        if not hasattr(self, 'output_view'):
            self.output_view = OutputView('phpcs', self.window)

        self.output_view.show_output()

    def show_empty_output(self):
        if not hasattr(self, 'output_view'):
            self.output_view = OutputView('phpcs', self.window)

        self.output_view.clear_output_view()
        self.output_view.show_output()

    def start_async(self, caption, executable):
        self.is_running = True
        self.proc = AsyncProcess(executable, self)
        StatusProcess(caption, self)

    def append_data(self, proc, data):
        self.output_view.append_data(proc, data)

    def update_status(self, msg, progress):
        sublime.status_message(msg + " " + progress)


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


class ActiveWindow(ActiveFile):
    def file_name(self):
        if hasattr(self, '_file_name'):
            return self._file_name

        return None

    def determine_filename(self, args=[]):
        if len(args) == 0:
            active_view = self.window.active_view()
            filename = active_view.file_name()
        else:
            filename = args[0]

        self._file_name = filename

    def is_php_buffer(self):
        ext = os.path.splitext(self.file_name())[1]
        if ext == 'php':
            return True
        return False


class PhpcsTextBase(sublime_plugin.TextCommand, ActiveView):
    def run(self, args):
        print 'Not implemented'


class PhpcsCommand(CommandBase):
    def run(self, path):
        self.show_empty_output()

        if os.path.isdir(path):
            dir = path
        else:
            dir = os.path.dirname(path)
        target = path

        cmd = "cd '" + dir + "' && phpcs"

        # Add the additional arguments from the settings file to the command
        for key, value in Pref.phpcs_additional_args.items():
            cmd = cmd + " " + key
            if value != "":
                cmd = cmd + "=" + value

        cmd = cmd + " '" + path + "'"

        self.append_data(self, "$ " + cmd + "\n")
        self.start_async("Running PHP CodeSniffer", cmd)


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

class PhpcsWindowBase(sublime_plugin.WindowCommand, ActiveWindow):
    def run(self, paths=[]):
        print "not implemented"

class PhpcsSniffAllFiles(PhpcsWindowBase):
    def run(self, paths=[]):

        cmd = PhpcsCommand(self.window)
        cmd.run(paths[0])

    def description(self):
        return 'Sniff all files...'


class PhpcsEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):

        if Pref.phpcs_execute_on_save == True:

            if re.search('.+\PHP.tmLanguage', view.settings().get('syntax')):

                view.window().run_command("phpcs_sniff_this_file")
