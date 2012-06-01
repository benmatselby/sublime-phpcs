Sublime PHP CodeSniffer, PHP Coding Standards Fixer, Linter and Mess Detector Plugin
====================================================================================

This plugin adds PHP CodeSniffer, PHP Coding Standards Fixer, the PHP Linter and phpmd support to Sublime Text 2.

Installation
------------

Use Sublime Text 2's [Package Control](http://wbond.net/sublime_packages/package_control) (Preferences -> Package Control -> Install Package -> PHP CodeSniffer) to install this plugin.

Or

Simply checkout the git repo into “~/Library/Application Support/Sublime Text 2/Packages/Phpcs or the equivalent folder on Windows or Linux.


PHP CodeSniffer Support For Sublime Text 2
------------------------------------------

This plugin adds support for running PHP CodeSniffer, PHP Coding Standards Fixer, the PHP linter and PHPMD from inside Sublime Text 2.

Right-click in the editor to:

* Sniff the current file

You can also open up the Command Palette (CTRL + SHIFT + P on Linux), and type
'PHP CodeSniffer' to see what you can do with PHP CodeSniffer in the currently open file.

For more information on how to run this plugin, visit [here](http://soulbroken.co.uk/code/sublimephpcs)


Configuration
-------------

You can configure:

**Plugin**

* show_debug - Do you want the debug information to be sent to the console?
* extensions_to_execute - Which filetypes do you want the plugin to execute for?
* phpcs_execute_on_save - Do you want the code sniffer plugin to run on file save for php files?
* phpcs_show_errors_on_save - Do you want the errors to be displayed in quick_panel on save?
* phpcs_show_gutter_marks - Do you want the errors to be displayed in the gutter?
* phpcs_show_errors_in_status - Do you want the errors to be displayed in status bar when clicking on the line with error?
* phpcs_show_quick_panel - Do you want the errors to be displayed in the quick panel?

**PHP_CodeSniffer**

* phpcs_sniffer_run - Do you want the PHPCS checker to run?
* phpcs_executable_path - The path to the phpcs executable. If empty string, use PATH to find it
* phpcs_additional_args - This is the extra information you want to pass to the phpcs command. For example which “standard” you want to run, and if you want to show warnings or not

**PHP CodeSniffer Fixer**

* php_cs_fixer_executable_path - The path to the php-cs-fixer application.
* php_cs_fixer_additional_args - This is the extra information you want to pass to the php-cs-fixer command. For example which "fixers" you want to run

**PHP Linter**

* phpcs_linter_run - Do you want the PHP linter (syntax errors) to run?
* phpcs_php_path - The path to the PHP executable. If empty string, use PATH to find it
* phpcs_linter_regex - The regex for the PHP linter output

**PHP Mess Detector**

* phpmd_run - Do you want the PHPMD to run? Off by default
* phpmd_executable_path - The path to the phpmd executable. If empty string, use PATH to find it
* phpmd_additional_args - This is the extra information you want to pass to the phpcs command. For example which "rulesets" you want to run


Requirements
------------

Requirements for this plugin:

* PHP_CodeSniffer 1.3.* (potentially works with lower versions, but this hasn't been tested)
* Python 2.6

This plugin has been tested on:

* Mac OS X 10.6.8 (2.6.1 r261:67515, Jun 24 2010, 21:47:49) and 10.7.3 (2.6.7 r267:88850, Jul 31 2011, 19:30:54)
* Ubuntu 11.10 (2.6.6 r266:84292, Jun 16 2011, 22:35:51)
* Windows XP (2.6.5 r265:79096, Mar 19 2010, 21:48:26)


FAQ
---

###What do I do when I get "No such file or directory" error?
```
OSError: [Error 2] No such file or directory
```

* Well, first of all you need to check that you have PHP_CodeSniffer, and if being used, the phpmd application.
* If you have these applications installed, then it sounds like those applications are not in your PATH, or cannot be found in your PATH by the Python runtime, so configure "phpcs_php_path", "phpcs_executable_path" and "phpmd_executable_path" with the actual paths to those applications

