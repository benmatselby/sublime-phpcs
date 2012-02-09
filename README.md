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

Right-click in the side-bar to:

* Sniff all files in a folder

You can also open up the Command Palette (CTRL + SHIFT + P on Linux), and type
'PHP CodeSniffer' to see what you can do with PHP CodeSniffer in the currently open file.


Configuration
-------------

You can configure:

* phpcs_additional_args - Arguments that you want appending to the phpcs command
* phpcs_execute_on_save - Do you want the code sniffer to be run when you save a php file


Contributions Welcome
---------------------

PHP CodeSniffer support is based on:
[PHPUnit plugin](https://github.com/stuartherbert/sublime-phpunit) which is based on
[Ruby Tests plugin](https://github.com/maltize/sublime-text-2-ruby-tests)_

Requests for features, and pull requests with patches, are most welcome :)
