Changelog
=========

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