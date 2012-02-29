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


Contributions Welcome
---------------------

Requests for features, and pull requests with patches, are most welcome :)
