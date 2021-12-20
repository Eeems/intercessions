*This is outdated and you should start using [blessed](https://pypi.python.org/pypi/blessed/) instead*

---

[![Known Vulnerabilities](https://snyk.io/test/github/eeems/intercessions/badge.svg)](https://snyk.io/test/github/eeems/intercessions)[![Requirements Status](https://requires.io/github/Eeems/intercessions/requirements.svg?branch=master)](https://requires.io/github/Eeems/intercessions/requirements/?branch=master)

# Intercessions

A blessings polyfill for the windows command line.

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

If [blessed](https://pypi.python.org/pypi/blessed/) is installed it will return the Terminal version of it instead. If [blessings](https://pypi.python.org/pypi/blessings/) is installed and you are not running the windows version of python it will attempt to return the [blessings](https://pypi.python.org/pypi/blessings/) instance of Terminal instead of the intercessions one.
