# intercessions
A blessings polyfill for the windows command line

Attempts to implement the full [blessings](https://pypi.python.org/pypi/blessings/) API in a format that will work on windows. Makes use of [colorama](https://pypi.python.org/pypi/colorama) to help with styling.

# Known Issues
1. Terminal.fullscreen will work, but will crash CMD/Powershell after exit. See [tartley/colorama#139](https://github.com/tartley/colorama/pull/139#issuecomment-340211264)
2. The following will not work as they have no command codes entered
   * standout
   * no_standout
   * subscript
   * no_subscript
   * superscript
   * no_superscript
