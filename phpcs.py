import datetime
import os
import re
import subprocess
import threading
import time
import sublime
import sublime_plugin
import sys
import string

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser
from os.path import expanduser

class Pref:

    project_file = None

    keys = [
        "show_debug",
        "extensions_to_execute",
        "extensions_to_blacklist",
        "phpcs_execute_on_save",
        "phpcs_show_errors_on_save",
        "phpcs_show_gutter_marks",
        "phpcs_outline_for_errors",
        "phpcs_show_errors_in_status",
        "phpcs_show_quick_panel",
        "phpcs_php_prefix_path",
        "phpcs_commands_to_php_prefix",
        "phpcs_icon_scope_color",
        "phpcs_sniffer_run",
        "phpcs_command_on_save",
        "phpcs_executable_path",
        "phpcs_additional_args",
        "php_cs_fixer_on_save",
        "php_cs_fixer_show_quick_panel",
        "php_cs_fixer_executable_path",
        "php_cs_fixer_additional_args",
        "phpcbf_on_save",
        "phpcbf_show_quick_panel",
        "phpcbf_executable_path",
        "phpcbf_additional_args",
        "phpcs_linter_run",
        "phpcs_linter_command_on_save",
        "phpcs_php_path",
        "phpcs_linter_regex",
        "phpmd_run",
        "phpmd_command_on_save",
        "phpmd_executable_path",
        "phpmd_additional_args",
        "scheck_run",
        "scheck_command_on_save",
        "scheck_executable_path",
        "scheck_additional_args"
    ]

    templated_keys = {
        "phpcs_php_prefix_path",
        "phpcs_executable_path",
        "php_cs_fixer_executable_path",
        "phpcbf_executable_path",
        "phpcs_php_path",
        "phpmd_executable_path",
        "scheck_executable_path",
    }

    def load(self):
        self.settings = sublime.load_settings('phpcs.sublime-settings')
        self.settings = self.apply_settings_template(self.settings)

        if sublime.active_window() is not None and sublime.active_window().active_view() is not None:
            project_settings = sublime.active_window().active_view().settings()
            if project_settings.has("phpcs"):
                project_settings.clear_on_change('phpcs')
                self.project_settings = project_settings.get('phpcs')
                project_settings.add_on_change('phpcs', pref.load)
            else:
                self.project_settings = {}
        else:
            self.project_settings = {}

        for key in self.keys:
            self.settings.clear_on_change(key)
            setattr(self, key, self.get_setting(key))
            self.settings.add_on_change(key, pref.load)

    def get_setting(self, key):
        if key in self.project_settings:
            return self.project_settings.get(key)
        else:
            return self.settings.get(key)

    def set_setting(self, key, value):
        if key in self.project_settings:
            self.project_settings[key] = value
        else:
            self.settings.set(key, value)

    def apply_settings_template(self, settings):
        # must only be defined after plugin_loaded()
        template_variables = {
            "st_cache_path": sublime.cache_path(),
            "st_executable_path": sublime.executable_path(),
            "st_installed_packages_path": sublime.installed_packages_path(),
            "st_packages_path": sublime.packages_path(),
            "user_home_path": os.path.expanduser("~"),
        }

        for key in self.templated_keys:
            settings.set(
                key,
                string.Template(settings.get(key))
                      .safe_substitute(template_variables)
            )

        return settings


pref = Pref()

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
    st_version = 3

if st_version == 2:
    pref.load()

def plugin_loaded():
    pref.load()

def debug_message(msg):
    if pref.show_debug == True:
        print("[Phpcs] " + str(msg))


class CheckstyleError():
    """Represents an error that needs to be displayed on the UI for the user"""
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def get_line(self):
        return self.line

    def get_message(self):
        data = self.message

        if st_version == 3:
            return HTMLParser().unescape(data)
        else:
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                data = data.decode(sublime.active_window().active_view().settings().get('fallback_encoding'))
            return HTMLParser().unescape(data)

    def set_point(self, point):
        self.point = point

    def get_point(self):
        return self.point


class ShellCommand():
    """Base class for shelling out a command to the terminal"""
    def __init__(self):
        self.error_list = []

        # Default the working directory for the shell command to the user's home dir.
        self.workingDir = expanduser("~")

    def setWorkingDir(self, dir):
        self.workingDir = dir

    def get_errors(self, path):
        self.execute(path)
        return self.error_list

    def shell_out(self, cmd):
        data = None

        for i, arg in enumerate(cmd):
            if isinstance(arg, str) and arg.startswith('~'):
                cmd[i] = os.path.expanduser(arg)

        if st_version == 3:
            debug_message(' '.join(cmd))
        else:
            for index, arg in enumerate(cmd[:]):
                cmd[index] = arg.encode(sys.getfilesystemencoding())

            debug_message(' '.join(cmd))

        debug_message(' '.join(cmd))

        info = None
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE

        debug_message("cwd: " + self.workingDir)
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info, cwd=self.workingDir)


        if proc.stdout:
            data = proc.communicate()[0]

        if st_version == 3:
            return data.decode()
        else:
            return data

    def execute(self, path):
        debug_message('Command not implemented')


class Sniffer(ShellCommand):
    """Concrete class for PHP_CodeSniffer"""
    def execute(self, path):
        if pref.phpcs_sniffer_run != True:
            return

        args = []

        if pref.phpcs_php_prefix_path != "" and self.__class__.__name__ in pref.phpcs_commands_to_php_prefix:
            args = [pref.phpcs_php_prefix_path]

        if pref.phpcs_executable_path != "":
            application_path = pref.phpcs_executable_path
        else:
            application_path = 'phpcs'

        if (len(args) > 0):
            args.append(application_path)
        else:
            args = [application_path]

        args.append("--report=checkstyle")

        # Add the additional arguments from the settings file to the command
        for key, value in pref.phpcs_additional_args.items():
            arg = key
            if key == "--runtime-set":
                args.append(arg)
                args.append(value)
            elif value != "":
                arg += "=" + value
            args.append(arg)

        target = os.path.normpath(path)

        # Set the working directory for the command to the path of the target file, allowing
        # phpcs the opportunity to find a default configuration file (phpcs.xml) in the file's path.
        self.setWorkingDir(os.path.dirname(target))

        args.append(target)
        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*line="(?P<line>\d+)" column="(?P<column>\d+)" severity="(?P<severity>\w+)" message="(?P<message>.*)" source', report)

        for line in lines:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)

    def get_standards_available(self):
        if pref.phpcs_executable_path != "":
            application_path = pref.phpcs_executable_path
        else:
            application_path = 'phpcs'

        args = []
        args.append(application_path)
        args.append('-i')

        output = self.shell_out(args)
        standards = output[35:].replace('and', ',').strip().split(', ')
        return standards

class Fixer(ShellCommand):
    """Concrete class for PHP-CS-Fixer"""
    def execute(self, path):

        args = []

        if pref.phpcs_php_prefix_path != "" and self.__class__.__name__ in pref.phpcs_commands_to_php_prefix:
            args = [pref.phpcs_php_prefix_path]

        if pref.php_cs_fixer_executable_path != "":
            if (len(args) > 0):
                args.append(pref.php_cs_fixer_executable_path)
            else:
                args = [pref.php_cs_fixer_executable_path]
        else:
            debug_message("php_cs_fixer_executable_path is not set, therefore cannot execute")
            sublime.error_message('The "php_cs_fixer_executable_path" is not set, therefore cannot execute this command')
            return

        args.append("fix")
        args.append(os.path.normpath(path))
        args.append("--verbose")

        # Add the additional arguments from the settings file to the command
        for key, value in pref.php_cs_fixer_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*(?P<line>\d+)\) (?P<file>.*)', report)

        for line in lines:
            error = CheckstyleError(line.group('line'), line.group('file'))
            self.error_list.append(error)

class CodeBeautifier(ShellCommand):
    """Concrete class for phpcbf"""
    def execute(self, path):

        args = []

        if pref.phpcs_php_prefix_path != "" and self.__class__.__name__ in pref.phpcs_commands_to_php_prefix:
            args = [pref.phpcs_php_prefix_path]

        if pref.phpcbf_executable_path != "":
            if (len(args) > 0):
                args.append(pref.phpcbf_executable_path)
            else:
                args = [pref.phpcbf_executable_path]
        else:
            debug_message("phpcbf_executable_path is not set, therefore cannot execute")
            sublime.error_message('The "phpcbf_executable_path" is not set, therefore cannot execute this command')
            return

        args.append(os.path.normpath(path))

        # Add the additional arguments from the settings file to the command
        for key, value in pref.phpcbf_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*\((?P<number>\d+) fixable violations\)', report)

        for line in lines:
            error = CheckstyleError(0, line.group('number') + " fixed violations")
            self.error_list.append(error)

class MessDetector(ShellCommand):
    """Concrete class for PHP Mess Detector"""
    def execute(self, path):
        if pref.phpmd_run != True:
            return

        args = []

        if pref.phpcs_php_prefix_path != "" and self.__class__.__name__ in pref.phpcs_commands_to_php_prefix:
            args = [pref.phpcs_php_prefix_path]

        if pref.phpmd_executable_path != "":
            application_path = pref.phpmd_executable_path
        else:
            application_path = 'phpmd'

        if (len(args) > 0):
            args.append(application_path)
        else:
            args = [application_path]

        args.append(os.path.normpath(path))
        args.append('text')

        for key, value in pref.phpmd_additional_args.items():
            arg = key
            if value != "":
                arg += "=" + value
            args.append(arg)

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*:(?P<line>\d+)[ \t]+(?P<message>.*)', report)

        for line in lines:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)


class Scheck(ShellCommand):
    """Concrete class for Scheck"""
    def execute(self, path):
        if pref.scheck_run != True:
            return

        args = []

        if pref.phpcs_php_prefix_path != "" and self.__class__.__name__ in pref.phpcs_commands_to_php_prefix:
            args = [pref.phpcs_php_prefix_path]

        if pref.scheck_executable_path != "":
            application_path = pref.scheck_executable_path
        else:
            application_path = 'scheck'

        if (len(args) > 0):
            args.append(application_path)
        else:
            args = [application_path]

        for key, value in pref.scheck_additional_args.items():
            args.append(key)
            if value != "":
                args.append(value)

        args.append(os.path.normpath(path))

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        lines = re.finditer('.*:(?P<line>\d+):(?P<column>\d+): CHECK: (?P<message>.*)', report)

        for line in lines:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)


class Linter(ShellCommand):
    """Content class for php -l"""
    def execute(self, path):
        if pref.phpcs_linter_run != True:
            return

        if pref.phpcs_php_path != "":
            args = [pref.phpcs_php_path]
        else:
            args = ['php']

        args.append("-l")
        args.append("-d display_errors=On")
        args.append(os.path.normpath(path))

        self.parse_report(args)

    def parse_report(self, args):
        report = self.shell_out(args)
        debug_message(report)
        line = re.search(pref.phpcs_linter_regex, report)
        if line != None:
            error = CheckstyleError(line.group('line'), line.group('message'))
            self.error_list.append(error)


class PhpcsCommand():
    """Main plugin class for building the checkstyle report"""

    # Class variable, stores the instances.
    instances = {}

    @staticmethod
    def instance(view, allow_new=True):
        '''Return the last-used instance for a given view.'''
        view_id = view.id()
        if view_id not in PhpcsCommand.instances:
            if not allow_new:
                return False
            PhpcsCommand.instances[view_id] = PhpcsCommand(view)
        return PhpcsCommand.instances[view_id]

    def __init__(self, view):
        self.view = view
        self.checkstyle_reports = []
        self.report = []
        self.event = None
        self.error_lines = {}
        self.error_list = []
        self.shell_commands = ['Linter', 'Sniffer', 'MessDetector']
        self.standards = []

    def run(self, path, event=None):
        self.event = event
        self.checkstyle_reports = []
        self.report = []

        if event != 'on_save':
            if pref.phpcs_linter_run:
                self.checkstyle_reports.append(['Linter', Linter().get_errors(path), 'dot'])
            if pref.phpcs_sniffer_run:
                self.checkstyle_reports.append(['Sniffer', Sniffer().get_errors(path), 'dot'])
            if pref.phpmd_run:
                self.checkstyle_reports.append(['MessDetector', MessDetector().get_errors(path), 'dot'])
            if pref.scheck_run:
                self.checkstyle_reports.append(['Scheck', Scheck().get_errors(path), 'dot'])
        else:
            if pref.phpcs_linter_command_on_save and pref.phpcs_linter_run:
                self.checkstyle_reports.append(['Linter', Linter().get_errors(path), 'dot'])
            if pref.phpcs_command_on_save and pref.phpcs_sniffer_run:
                self.checkstyle_reports.append(['Sniffer', Sniffer().get_errors(path), 'dot'])
            if pref.phpmd_command_on_save and pref.phpmd_run:
                self.checkstyle_reports.append(['MessDetector', MessDetector().get_errors(path), 'dot'])
            if pref.scheck_command_on_save and pref.scheck_run:
                self.checkstyle_reports.append(['Scheck', Scheck().get_errors(path), 'dot'])

        sublime.set_timeout(self.generate, 0)

    def clear_sniffer_marks(self):
        for region in self.shell_commands:
            self.view.erase_regions(region)

    def set_status_bar(self):
        if not pref.phpcs_show_errors_in_status:
            return

        if self.view.is_scratch():
            return

        line = self.view.rowcol(self.view.sel()[0].end())[0]
        errors = self.get_errors(line)
        if errors:
            self.view.set_status('Phpcs', errors)
        else:
            self.view.erase_status('Phpcs')

    def generate(self):
        self.error_list = []
        region_set = []
        self.error_lines = {}

        for shell_command, report, icon in self.checkstyle_reports:
            self.view.erase_regions('checkstyle')
            self.view.erase_regions(shell_command)

            debug_message(shell_command + ' found ' + str(len(report)) + ' errors')
            for error in report:
                line = int(error.get_line())
                pt = self.view.text_point(line - 1, 0)
                region_line = self.view.line(pt)
                region_set.append(region_line)
                self.error_list.append('(' + str(line) + ') ' + error.get_message())
                error.set_point(pt)
                self.report.append(error)
                self.error_lines[line] = error.get_message()

            if len(self.error_list) > 0:
                icon = icon if pref.phpcs_show_gutter_marks else ''
                outline = sublime.DRAW_OUTLINED if pref.phpcs_outline_for_errors else sublime.HIDDEN
                if pref.phpcs_show_gutter_marks or pref.phpcs_outline_for_errors:
                    if pref.phpcs_icon_scope_color == None:
                        debug_message("WARN: phpcs_icon_scope_color is not defined, so resorting to phpcs colour scope")
                        pref.phpcs_icon_scope_color = "phpcs"
                    self.view.add_regions(shell_command, region_set, pref.phpcs_icon_scope_color, icon, outline)

        if pref.phpcs_show_quick_panel == True:
            # Skip showing the errors if we ran on save, and the option isn't set.
            if self.event == 'on_save' and not pref.phpcs_show_errors_on_save:
                return
            self.show_quick_panel()

    def show_quick_panel(self):
        self.view.window().show_quick_panel(self.error_list, self.on_quick_panel_done)

    def fix_standards_errors(self, tool, path):
        self.error_lines = {}
        self.error_list = []
        self.report = []

        if tool == "CodeBeautifier":
            fixes = CodeBeautifier().get_errors(path)
        else:
            fixes = Fixer().get_errors(path)

        for fix in fixes:
            self.error_list.append(fix.get_message())

        if pref.php_cs_fixer_show_quick_panel == True:
            self.show_quick_panel()

    def display_coding_standards(self):
        self.standards = Sniffer().get_standards_available()
        self.view.window().show_quick_panel(self.standards, self.on_coding_standard_change)

    def on_coding_standard_change(self, picked):
        if picked == -1:
            return

        current_additional_args = pref.get_setting('phpcs_additional_args')
        current_additional_args['--standard'] = self.standards[picked].replace(' ', '')

        pref.set_setting('phpcs_additional_args', current_additional_args)
        debug_message(current_additional_args)

    def on_quick_panel_done(self, picked):
        if picked == -1:
            return

        if (len(self.report) > 0):
            pt = self.report[picked].get_point()
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(pt))
            self.view.show(pt)
            self.set_status_bar()

    def get_errors(self, line):
        if not line + 1 in self.error_lines:
            return False

        return self.error_lines[line + 1]

    def get_next_error(self, line):
        current_line = line + 1

        cache_error=None
        # todo: Need a way of getting the line count of the current file!
        cache_line=1000000
        for error in self.report:
            error_line = error.get_line()

            if cache_error != None:
                cache_line = cache_error.get_line()

            if int(error_line) > int(current_line) and int(error_line) < int(cache_line):
                cache_error = error

        if cache_error != None:
            pt = cache_error.get_point()
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(pt))
            self.view.show(pt)


class PhpcsTextBase(sublime_plugin.TextCommand):
    """Base class for Text commands in the plugin, mainly here to check php files"""
    description = ''

    def run(self, args):
        debug_message('Not implemented')

    def description(self):
        if not PhpcsTextBase.should_execute(self.view):
            return "Invalid file format"
        else:
            return self.description

    @staticmethod
    def should_execute(view):
        if view.file_name() != None:

            try:
                ext = os.path.splitext(view.file_name())[1]
                result = ext[1:] in pref.extensions_to_execute
            except:
                debug_message("Is 'extensions_to_execute' setup correctly")
                return False

            for block in pref.extensions_to_blacklist:
                match = re.search(block, view.file_name())
                if match != None:
                    return False

            return result

        return False


class PhpcsSniffThisFile(PhpcsTextBase):
    """Command to sniff the open file"""
    description = 'Sniff this file...'

    def run(self, args):
        cmd = PhpcsCommand.instance(self.view)
        cmd.run(self.view.file_name())

    def is_enabled(self):
        return PhpcsTextBase.should_execute(self.view)


class PhpcsShowPreviousErrors(PhpcsTextBase):
    '''Command to show the previous sniff errors.'''
    description = 'Display sniff errors...'

    def run(self, args):
        cmd = PhpcsCommand.instance(self.view, False)
        cmd.show_quick_panel()

    def is_enabled(self):
        '''This command is only enabled if it's a PHP buffer with previous errors.'''
        return PhpcsTextBase.should_execute(self.view) \
            and PhpcsCommand.instance(self.view, False) \
            and len(PhpcsCommand.instance(self.view, False).error_list) > 0


class PhpcsGotoNextErrorCommand(PhpcsTextBase):
    """Go to the next error from the current position"""
    def run(self, args):
        line = self.view.rowcol(self.view.sel()[0].end())[0]

        cmd = PhpcsCommand.instance(self.view)
        next_line = cmd.get_next_error(line)

    def is_enabled(self):
        '''This command is only enabled if it's a PHP buffer with previous errors.'''

        return PhpcsTextBase.should_execute(self.view) \
            and PhpcsCommand.instance(self.view, False) \
            and len(PhpcsCommand.instance(self.view, False).error_list) > 0


class PhpcsClearSnifferMarksCommand(PhpcsTextBase):
    """Command to clear the sniffer marks from the view"""
    description = 'Clear sniffer marks...'

    def run(self, args):
        cmd = PhpcsCommand.instance(self.view)
        cmd.clear_sniffer_marks()

    def is_enabled(self):
        return PhpcsTextBase.should_execute(self.view)


class PhpcsFixThisFileCommand(PhpcsTextBase):
    """Command to use php-cs-fixer to 'fix' the file"""
    description = 'Fix coding standard issues (php-cs-fixer)'

    def run(self, args, tool="Fixer"):
        debug_message(tool)
        cmd = PhpcsCommand.instance(self.view)
        cmd.fix_standards_errors(tool, self.view.file_name())

    def is_enabled(self):
        return PhpcsTextBase.should_execute(self.view)


class PhpcsFixThisDirectoryCommand(sublime_plugin.WindowCommand):
    """Command to use php-cs-fixer to 'fix' the directory"""
    def run(self, tool="Fixer", paths=[]):
        cmd = PhpcsCommand.instance(self.window.active_view())
        cmd.fix_standards_errors(tool, os.path.normpath(paths[0]))

    def is_enabled(self):
        if pref.php_cs_fixer_executable_path != '':
            return True
        else:
            return False

    def is_visible(self, paths=[]):
        return True

    def description(self, paths=[]):
        return 'Fix this directory (PHP-CS-Fixer)'


class PhpcsTogglePlugin(PhpcsTextBase):
    """Command to toggle if plugin should execute on save"""
    def run(self, edit, toggle=None):
        if toggle == None:
            if pref.phpcs_execute_on_save == True:
                pref.phpcs_execute_on_save = False
            else:
                pref.phpcs_execute_on_save = True
        else:
            if toggle :
                pref.phpcs_execute_on_save = True
            else:
                pref.phpcs_execute_on_save = False

    def is_enabled(self):
        return PhpcsTextBase.should_execute(self.view)

    def description(self, paths=[]):
        if pref.phpcs_execute_on_save == True:
            description = 'Turn Execute On Save Off'
        else:
            description = 'Turn Execute On Save On'
        return description


class PhpcsSwitchCodingStandard(PhpcsTextBase):
    """Ability to switch the coding standard for this session"""
    def run(self, args):
        cmd = PhpcsCommand.instance(self.view)
        cmd.display_coding_standards()

    def is_enabled(self):
        return PhpcsTextBase.should_execute(self.view)


class PhpcsEventListener(sublime_plugin.EventListener):
    """Event listener for the plugin"""
    def on_post_save(self, view):
        if PhpcsTextBase.should_execute(view):
            if pref.phpcs_execute_on_save == True:
                cmd = PhpcsCommand.instance(view)
                thread = threading.Thread(target=cmd.run, args=(view.file_name(), 'on_save'))
                thread.start()

            if pref.phpcs_execute_on_save == True and pref.php_cs_fixer_on_save == True:
                cmd = PhpcsCommand.instance(view)
                cmd.fix_standards_errors("Fixer", view.file_name())

            if pref.phpcs_execute_on_save == True and pref.phpcbf_on_save == True:
                cmd = PhpcsCommand.instance(view)
                cmd.fix_standards_errors("CodeBeautifier", view.file_name())

    def on_selection_modified(self, view):
        if not PhpcsTextBase.should_execute(view):
            return

        cmd = PhpcsCommand.instance(view, False)
        if isinstance(cmd, PhpcsCommand):
            cmd.set_status_bar()

    def on_pre_save(self, view):
        """ Project based settings, currently able to see an API based way of doing this! """
        if not PhpcsTextBase.should_execute(view) or st_version == 2:
            return

        current_project_file = view.window().project_file_name();
        debug_message('Project files:')
        debug_message(' Current: ' + str(current_project_file))
        debug_message(' Last Known: ' + str(pref.project_file))

        if current_project_file == None:
            debug_message('No project file defined, therefore skipping reload')
            return

        if pref.project_file == current_project_file:
            debug_message('Project files are the same, skipping reload')
        else:
            debug_message('Project files have changed, commence the reload')
            pref.load();
            pref.project_file = current_project_file
