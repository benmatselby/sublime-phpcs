This is a plugin for Sublime Text which provides checkstyle reports using the following tools (all optional):

* PHP_CodeSniffer (phpcs)
* Linter (php -l)
* PHP Mess Detector (phpmd)
* Scheck (scheck, part of Facebook’s pfff toolchain)

You can also configure the plugin to fix the issues using either

* PHP Coding Standards Fixer (php-cs-fixer)
* PHP Code Beautifier (phpcbf) application

##Requirements
Requirements for this plugin, should you want all the options to work:

* PHP_CodeSniffer 3.5+ (potentially works with lower versions, but this hasn’t been tested) - **[Install](https://pear.php.net/package/PHP_CodeSniffer/download/1.3.2)**
* PHPMD 2.8+ (potentially works with lower versions, but this hasn’t been tested) - **[Install](https://github.com/phpmd/phpmd/releases/tag/2.8.1)**
* PHP CS Fixer version 2.6+ (potentially works with lower versions, but this hasn’t been tested) - **[Install](https://github.com/FriendsOfPHP/PHP-CS-Fixer/releases)**

This plugin has been tested on:

* Mac OS X 10.8.2
* Ubuntu 11.10
* Windows 7
* Sublime Text 2
* Sublime Text 3


##Installation
Use Sublime Text’s Package Control (Preferences -> Package Control -> Install Package -> Phpcs) to install this plugin. This is the recommended installation path.

Or

Simply checkout the git repo into “~/Library/Application Support/Sublime Text [VERSION NUMBER]/Packages/ or the equivalent folder on Windows or Linux.

```
$ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
$ git clone git://github.com/benmatselby/sublime-phpcs.git Phpcs
```

In both cases, you may need to then configure the following with the actual path to the application:

* “phpcs_php_path”
* “phpcs_executable_path”
* “phpmd_executable_path”
* “php_cs_fixer_executable_path”

They are optional for the plugin. The path needs to include the application such as “/usr/local/bin/phpcs”.

In order to get the path of the application (On a Mac/Linux based environment), you can use:

```
$ which phpcs
$ which phpmd
$ which php-cs-fixer
$ which phpcbf

```

##Features
* Ability to run PHP_CodeSniffer
* Ability to run php -l on the open file
* Ability to run PHP Mess Detector on the open file
* Ability to run Scheck on the open file
* Show cached results from PHP_CodeSniffer in open file
* Show errors in the Quick Panel
* Show errors in the Gutter
* Highlight the errors in the editor
* Show the error for a given line in the status bar
* Ability to specify the regular expression of the linter errors
* Ability to specify the location of the PHP_CodeSniffer application
* Ability to specify the location of the PHP Mess Detector application
* Ability to run the PHP Coding Standards Fixer tool which fixes most issues in your code when you want to follow the PHP coding standards as defined in the PSR-1 and PSR-2 documents
* Ability to run the PHP Code Beautifier tool which fixes most issues in your code when you want to follow PHP coding standards

Once you have right clicked on a file and selected “PHP CodeSniffer” > “Sniff this file…” you will get the output as shown below (depending on the settings you have defined):


##Configuration
You can also define the configuration for the following settings, be it for a project, user settings or the default settings:

###Plugin

* show_debug – Do you want the debug information to be sent to the console?
* extensions_to_execute – Which filetypes do you want the plugin to execute for?
* extensions_to_blacklist – Override the extensions_to_execute in case you have a sub extension such as twig.php etc.
* phpcs_execute_on_save – Do you want the code sniffer plugin to run on file save for php files?
* phpcs_show_errors_on_save – Do you want the errors to be displayed in quick_panel on save?
* phpcs_show_gutter_marks – Do you want the errors to be displayed in the gutter?
* phpcs_outline_for_errors – Do you want the errors to be highlighted in the editor?
* phpcs_show_errors_in_status – Do you want the errors to be displayed in status bar when clicking on the line with error?
* phpcs_show_quick_panel – Do you want the errors to be displayed in the quick panel?
* phpcs_php_prefix_path – Needed on windows for phar based applications. Also if you cannot make phar executable. Avoid if possible
* phpcs_commands_to_php_prefix – List of commands you want the php path to prefix. This would be useful, if you have some commands as a phar that cannot be run without the php prefix, and others using native command.
* phpcs_icon_scope_color - What colour to stylise the icon. This needs knowledge of theming of Sublime Test, as it uses scope colours from the theme to "tint" the dot icon. See [here](https://www.sublimetext.com/docs/3/api_reference.html#sublime.View)

###PHP_CodeSniffer

* phpcs_sniffer_run – Do you want the PHPCS checker to run?
* phpcs_command_on_save – Do you want the command to execute on save?
* phpcs_executable_path – The path to the phpcs executable. If empty string, use PATH to find it
* phpcs_additional_args – This is the extra information you want to pass to the phpcs command. For example which “standard” you want to run, and if you want to show warnings or not


###PHP CodeSniffer Fixer

* php_cs_fixer_on_save – Do you want to run the fixer on file save?
* php_cs_fixer_show_quick_panel – Do you want the quick panel to display on execution?
* php_cs_fixer_executable_path – The path to the php-cs-fixer application.
* php_cs_fixer_additional_args – This is the extra information you want to pass to the php-cs-fixer command. For example which “fixers” you want to run


###PHP CodeSniffer Fixer

* phpcbf_on_save – Do you want to run the fixer on file save?
* phpcbf_show_quick_panel – Do you want the quick panel to display on execution?
* phpcbf_executable_path – The path to the phpcbf application.
* phpcbf_additional_args – This is the extra information you want to pass to the phpcbf command. For example which “standard” to use in order to fix the issues


##PHP Linter

* phpcs_linter_run – Do you want the PHP linter to run?
* phpcs_linter_command_on_save – Do you want the command to execute on save?
* phpcs_php_path – The path to the PHP executable. If empty string, use PATH to find it
* phpcs_linter_regex – The regex for the PHP linter output


###PHP Mess Detector

* phpmd_run – Do you want the PHPMD to run? Off by default
* phpmd_command_on_save – Do you want the command to execute on save?
* phpmd_executable_path – The path to the phpmd executable. If empty string, use PATH to find it
* phpmd_additional_args – This is the extra information you want to pass to the phpmd command. For example which “rulesets” you want to run


###Scheck

* scheck_run - Do you want the scheck application to run? Off by default
* scheck_command_on_save - Do you want the command to execute on save?
* scheck_executable_path - The path to the scheck executable. If empty string, use PATH to find it
* scheck_additional_args - This is the extra information you want to pass to the scheck command.

Examples of the settings files can be found [here](https://github.com/benmatselby/sublime-phpcs/tree/master/example-settings)

####Project Based Settings
Your .project file should look something like this:

```
{
    "folders":
    [
        {}
    ],
    "settings":
    {
        "phpcs":
        {
            "phpcs_additional_args":
            {
                "--standard": "/path/to/.composer/vendor/drupal/coder/coder_sniffer/Drupal"
            }
        }
    }
}
```

Of course this is a example to apply Drupal code sniffer. This could be anything. Whatever you can have on this package settings it can be overwritten under the settings -> phpcs


##Changelog
To track the changes more frequently, you can review the Changelog [here](https://github.com/benmatselby/sublime-phpcs/blob/master/Changelog.md)
