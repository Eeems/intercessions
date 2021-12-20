from platform import system

if system() == "windows":
    from .terminal import Terminal

else:
    try:
        from blessed import Terminal

    except ImportError:
        from .terminal import Terminal

__all__ = [
    'Terminal'
]
