sublime-phpcs
=============

This plugin adds PHP CodeSniffer, PHP Code Beautifier and Fixer, PHP Coding Standards Fixer, the PHP Linter, PHP Mess Detector, Scheck support to Sublime Text.

For more information about this plugin such as features, installation requirements etc, please click [here](https://benmatselby.dev/sublime-phpcs/#configuration)

Configuration
-------------

**You will need to configure this plugin to work for your setup**, please view the options [here](https://benmatselby.dev/sublime-phpcs/#configuration)


FAQ
---

### What do I do when I get "OSError: [Errno 8] Exec format error"?

* This seems to be an issue you may get with regards to wrapper scripts.
* Please make sure that the application/script you are referencing has the correct shebang line, as per [GH-79](https://github.com/benmatselby/sublime-phpcs/issues/79)

### What do I do when I get "OSError: [Error 2] No such file or directory"?

* Well, first of all you need to check that you have PHP_CodeSniffer, and if being used, the phpmd application.
* If you have these applications installed, then it sounds like those applications are not in your PATH, or cannot be found in your PATH by the Python runtime, so configure "phpcs_php_path", "phpcs_executable_path", "phpmd_executable_path" and "php_cs_fixer_executable_path" with the actual paths to those applications

### What do I do when I get "OSError: [Errno 13] Permission denied"?

* It sounds like your path settings are incorrect.
* You need to make sure that when you specifiy the path you include the entire path including the application

```
$ which phpcs
/usr/local/bin/phpcs
```

* That entire output is the path you need in your configs.

### What if I've installed the applications using Homebrew?

If you have installed php-cs-fixer, phpmd or phpcs via homebrew then please make sure that you define the "*_executable_path" option to the .phar application and not the wrapper script that is placed in your bin folder, as this will cause odd behaviour.

### What other Key Bindings can I setup?

The following is a list of commands that you can bind to a keyboard shortcut:

* phpcs_fix_this_file
* phpcs_clear_sniffer_marks
* phpcs_goto_next_error
* phpcs_show_previous_errors
* phpcs_sniff_this_file

In order to achieve this you need to add the following to one of your key bindings settings file:

```json
{ "keys": ["ctrl+super+t"], "command": "phpcs_clear_sniffer_marks" }
```

To decide which "Fixer" to use, you can do:

```json
{ "keys": ["super+k", "super+f"], "command": "phpcs_fix_this_file", "args": {"tool": "CodeBeautifier"}},
```

or

```json
{ "keys": ["super+k", "super+f"], "command": "phpcs_fix_this_file", "args": {"tool": "Fixer"}},
```

You can then change the ctrl+super+t combination to something of your choosing.
