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

This plugin adds support for running PHP CodeSniffer from inside Sublime Text 2.

Right-click in the editor to:

* Sniff the current file

You can also open up the Command Palette (CTRL + SHIFT + P on Linux), and type
'PHP CodeSniffer' to see what you can do with PHP CodeSniffer in the currently open file.


Configuration
-------------

You can configure:

* phpcs_additional_args - This is the extra information you want to pass to the phpcs command. For example which “standard” you want to run, and if you want to show warnings or not
* phpcs_execute_on_save - Do you want the code sniffer plugin to run on file save for php files?
* phpcs_show_gutter_marks - Do you want the errors to be displayed in the gutter?
* phpcs_show_quick_panel - Do you want the errors to be displayed in the quick panel?

Contributions Welcome
---------------------

PHP CodeSniffer support is based on:
_[PHPUnit plugin](https://github.com/stuartherbert/sublime-phpunit) which is based on
[Ruby Tests plugin](https://github.com/maltize/sublime-text-2-ruby-tests)_

Requests for features, and pull requests with patches, are most welcome :)
