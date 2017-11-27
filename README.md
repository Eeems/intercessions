[![Known Vulnerabilities](https://snyk.io/test/github/eeems/intercessions/badge.svg)](https://snyk.io/test/github/eeems/intercessions)
# Intercessions
A blessings polyfill for the windows command line

Attempts to implement the full [blessings](https://pypi.python.org/pypi/blessings/) API in a format that will work on windows. Makes use of [colorama](https://pypi.python.org/pypi/colorama) to help with styling.

# Installation
``pip install intercessions``

# Usage
```python
from intercessions import Terminal

t = Terminal()
with t.location(0,0), t.hidden_cursor():
    print(t.bold_red('Hello World!') + t.clear_eol)
    raw_input('Press Enter' + t.clear_eol)

```

# Known Issues
1. Terminal.fullscreen will work, but will crash CMD/Powershell after exit. See [tartley/colorama#139](https://github.com/tartley/colorama/pull/139#issuecomment-340211264)
2. The following will not work as they have no command codes entered
   * standout
   * no_standout
   * subscript
   * no_subscript
   * superscript
   * no_superscript
