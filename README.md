Sublime PHP CodeSniffer
=======================

This plugin adds PHP CodeSniffer support to Sublime Text 2.

Installation
------------

Use Sublime Text 2's [Package Control](http://wbond.net/sublime_packages/package_control) (Preferences -> Package Control -> Install Package -> PHP CodeSniffer) to install this plugin.

Or

Simply checkout the git repo into “~/Library/Application Support/Sublime Text 2/Packages/Phpcs or the equivalent folder on Windows or Linux.


PHP CodeSniffer Support For Sublime Text 2
------------------------------------------

This plugin adds support for running PHP CodeSniffer and the PHP linter from inside Sublime Text 2.

Right-click in the editor to:

* Sniff the current file

You can also open up the Command Palette (CTRL + SHIFT + P on Linux), and type
'PHP CodeSniffer' to see what you can do with PHP CodeSniffer in the currently open file.

For more information on how to run this plugin, visit [here](http://soulbroken.co.uk/code/sublimephpcs)


Configuration
-------------

You can configure:

* phpcs_additional_args - This is the extra information you want to pass to the phpcs command. For example which “standard” you want to run, and if you want to show warnings or not
* phpcs_execute_on_save - Do you want the code sniffer plugin to run on file save for php files?
* phpcs_show_gutter_marks - Do you want the errors to be displayed in the gutter?
* phpcs_show_quick_panel - Do you want the errors to be displayed in the quick panel?
* phpcs_linter_run - Do you want the PHP linter to run?
* phpcs_linter_regex - The regex for the PHP linter output
* phpcs_executable_path - The path to the phpcs executable. If empty string, use PATH to find it
* phpcs_show_errors_on_save - Do you want the errors to be displayed in quick_panel on save?
* phpcs_show_errors_in_status - Do you want the errors to be displayed in status bar when clicking on the line with error?


Requirements
------------

Requirements for this plugin:

* PHP_CodeSniffer 1.3.* (potentially works with lower versions, but this hasn't been tested)
* Python 2.6

This plugin has been tested on:

* Mac OS X 10.6.8 (2.6.1 r261:67515, Jun 24 2010, 21:47:49) and 10.7.3 (2.6.7 r267:88850, Jul 31 2011, 19:30:54)
* Ubuntu 11.10 (2.6.6 r266:84292, Jun 16 2011, 22:35:51)
* Windows XP (2.6.5 r265:79096, Mar 19 2010, 21:48:26)


