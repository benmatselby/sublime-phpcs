Sublime PHP_CodeSniffer Changelog
=================================

3.2
---
* Added the ability to run the PHP linter alongside the PHP_CodeSniffer
* You can specify if you want the linter to run
* You can specify the regex of the linter output, as it seems to differ on different systems

3.1
---
* Updated the loading of settings to use static method
* Updated the debugging calls to prefix with "Phpcs"
* Added a counter of errors in the console log

3.0
---
* Enables the plugin to work on the Windows platform [GH-1](https://github.com/benmatselby/sublime-phpcs/issues/1)
* Removed some redundant code

2.0
---
* Changed the way the checkstyle report was parsed. due to [GH-2](https://github.com/benmatselby/sublime-phpcs/issues/2) which means it should now work on Linux machines

1.1
---
* Load the settings into memory if changed using _settings.add_on_change_. This only works on User settings rather than defaults, which is a limitation of the API from what I can see at the moment.
* Define the coding standard as PEAR by default.
* Introduced this Changelog.md file.
* Raised [this feature request](http://sublimetext.userecho.com/topic/96221-gutter-hint-bubles-when-hovered-over/) so I can show tool tips in the gutter for each checkstyle error/warning

1.0
---
* Initial release documented [here](http://soulbroken.co.uk/code/sublimephpcs)
* Right click on a php file and generate checkstyle report in the gutter and/or quick panel
* Settings to turn the reporting on/off for gutter and quick panel