from __future__ import absolute_import

import atexit
import re
import sys
import time
import msvcrt
import colorama

from . import win32
from contextlib import contextmanager
from .terminalsize import get_terminal_size


try:
    unicode

except NameError:
    unicode = str

_atexit_registered = False
_enabled_vt_processing = False

def enable_vt_processing():
    global _enabled_vt_processing, _atexit_registered
    if win32.windll is None or not win32.winapi_test():
        return False

    mode = win32.GetConsoleMode(win32.STDOUT)
    if mode & win32.ENABLE_VIRTUAL_TERMINAL_PROCESSING:
        return True

    if not win32.SetConsoleMode(
        win32.STDOUT,
        mode | win32.ENABLE_VIRTUAL_TERMINAL_PROCESSING
    ):
        return False  # Unsupported

    _enabled_vt_processing = True
    if not _atexit_registered:
        atexit.register(lambda: restore_vt_processing(True))
        _atexit_registered = True

    return True


def restore_vt_processing(atexit=False):
    global _enabled_vt_processing, _atexit_registered
    if atexit:
        _atexit_registered = False

    if win32.windll is None or not win32.winapi_test():
        return

    if _enabled_vt_processing:
        win32.SetConsoleMode(
            win32.STDOUT,
            win32.GetConsoleMode(
                win32.STDOUT) & ~win32.ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )
        _enabled_vt_processing = False


class Styler(unicode):
    def __new__(cls, style):
        new = unicode.__new__(cls, style)
        new._style = style
        return new

    def __call__(self, text):
        return self + text + colorama.Style.RESET_ALL

class MoveY():
    def __init__(self, term):
        self.term = term

    def __call__(self, y):
        pos = self.term.get_location()
        return '\x1b[%s;%sH' % (y, pos[0])


class MoveX():
    def __init__(self, term):
        self.term = term

    def __call__(self, x):
        pos = self.term.get_location()
        return '\x1b[%s;%sH' % (pos[1], x)


class Move():
    def __call__(self, x, y):
        return '\x1b[%s;%sH' % (y, x)



class Terminal():
    def __init__(self, kind=None, stream=None, force_styling=False):
        vt = enable_vt_processing()
        colorama.init(convert=vt, strip=bool(not vt))
        if stream is None:
            stream = sys.__stdout__

        instream = stream
        if stream == sys.__stdout__:
            instream = sys.__stdin__

        else:
            stream = colorama.AnsiToWin32(stream).stream

        try:
            if hasattr(stream, 'fileno') and callable(stream.fileno):
                stream_descriptor = stream.fileno()
        except IOUnsupportedOperation:
            stream_descriptor = None

        # @todo check stream_descriptor
        self.stream = stream
        self.instream = instream
        self._styles = {
            # Control
            'reset': '\x1b[0m',
            'bold': '\x1b[1m',
            'dim': '\x1b[2m',
            'italic': '\x1b[3m',
            'underline': '\x1b[4m',
            'blink': '\x1b[5m',
            'fast_blink': '\x1b[6m',
            'reverse': '\x1b[7m',
            'shadow': '\x1b[8m',
            'strikethrough': '\x1b[9m',
            'normal': '\x1b[22m',
            'no_italic': '\x1b[23m',
            'no_underline': '\x1b[24m',
            'no_blink': '\x1b[25m',
            'no_reverse': '\x1b[27m',
            'no_shadow': '\x1b[28m',
            'no_strikethrough': '\x1b[29m',
            'move_left': '\x1b[1C',
            'move_right': '\x1b[1D',
            'move_up': '\x1b[1A',
            'move_down': '\x1b[1B',
            'clear': '\x1b[2J',
            'clear_eol': '\x1b[0K',
            'clear_bol': '\x1b[1K',
            'clear_eos': '\x1b[0J',
            'save': '\x1b[s',
            'restore': '\x1b[u',
            'enter_fullscreen': '\x1b[?1049h',
            'exit_fullscreen': '\x1b[?1049l',
            'hide_cursor': '\x1b[?25l',
            'normal_cursor': '\x1b[?25h',
            'standout': '\x1b[7m',
            'no_standout': '\x1b[m',
            'subscript': '\x1b[74m',
            'no_subscript': '\x1b[75m',
            'superscript': '\x1b[73m',
            'no_superscript': '\x1b[75m',
            # Colors
            'black': colorama.Fore.BLACK,
            'red': colorama.Fore.RED,
            'green': colorama.Fore.GREEN,
            'yellow': colorama.Fore.YELLOW,
            'blue': colorama.Fore.BLUE,
            'magenta': colorama.Fore.MAGENTA,
            'cyan': colorama.Fore.CYAN,
            'white': colorama.Fore.WHITE
        }
        self._backgrounds = {
            'black': colorama.Back.BLACK,
            'red': colorama.Back.RED,
            'green': colorama.Back.GREEN,
            'yellow': colorama.Back.YELLOW,
            'blue': colorama.Back.BLUE,
            'magenta': colorama.Back.MAGENTA,
            'cyan': colorama.Back.CYAN,
            'white': colorama.Back.WHITE
        }

    def __getattr__(self, names):
        if names in self._styles:
            return Styler(self._styles[names])

        styles = []
        back = 0
        for name in names.split('_'):
            if name == 'on':
                back = 1

            else:
                if back:
                    if name not in self._backgrounds:
                        raise ValueError('Style %s not valid' % (name))

                    styles.append(self._backgrounds[name])

                else:
                    if name not in self._styles:
                        raise ValueError('Style %s not valid' % (name))

                    styles.append(self._styles[name])

        return Styler(''.join(styles))

    @property
    def flash(self):
        return ''  # Not supported

    @property
    def move_y(self):
        return MoveY(self)

    @property
    def move_x(self):
        return MoveX(self)

    @property
    def move(self):
        return Move()

    @property
    def width(self):
        size = get_terminal_size()
        if size:
            size = size[0]

        return size

    @property
    def height(self):
        size = get_terminal_size()
        if size:
            size = size[1]

        return size

    @contextmanager
    def location(self, x=None, y=None):
        self.write(self.save)
        if x is not None and y is not None:
            self.write(self.move(x, y))

        elif x is not None:
            self.write(self.move_x(x))

        elif y is not None:
            self.write(self.move_y(y))

        try:
            yield
        finally:
            self.write(self.restore)

    @contextmanager
    def fullscreen(self):
        self.write(self.enter_fullscreen)
        try:
            yield
        finally:
            self.write(self.exit_fullscreen)

    @contextmanager
    def hidden_cursor(self):
        self.write(self.hide_cursor)
        try:
            yield
        finally:
            self.write(self.normal_cursor)

    def get_location(self):
        self.write('\x1b[6n')
        self.stream.flush()

        data = self.read(10, 1)
        match = re.search(r'\[(\d+);(\d+)R', data)

        if match:
            row, col = match.groups()
            return int(row), int(col)

        # Couldn't get location
        return -1, -1

    def title(self, title):
        self.write('\x1b]0;%s\a' % (title))

    def write(self, text):
        self.stream.write(text)

    def read(self, length=None, timeout=5):
        start_time = time.time()
        input = ''
        while True:
            if msvcrt.kbhit():
                chr = msvcrt.getwch()
                if ord(chr) == 13:  # enter_key
                    break

                elif ord(chr) >= 32:  # space_char
                    input += chr

            if (
                time.time() - start_time > timeout
            ) or (
                length is not None and len(input) >= length
            ):
                break

        return input
