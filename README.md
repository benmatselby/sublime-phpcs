sublime-phpcs
=============

This plugin adds PHP CodeSniffer, PHP Coding Standards Fixer, the PHP Linter, PHP Mess Detector, Scheck support to Sublime Text.

For more information about this plugin such as features, installation requirements etc, please click [here](http://www.soulbroken.co.uk/code/sublimephpcs/)


FAQ
---

### What do I do when I get "No such file or directory" error?

```
OSError: [Error 2] No such file or directory
```

* Well, first of all you need to check that you have PHP_CodeSniffer, and if being used, the phpmd application.
* If you have these applications installed, then it sounds like those applications are not in your PATH, or cannot be found in your PATH by the Python runtime, so configure "phpcs_php_path", "phpcs_executable_path", "phpmd_executable_path" and "php_cs_fixer_executable_path" with the actual paths to those applications

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

You can then change the ctrl+super+t combination to something of your choosing.
