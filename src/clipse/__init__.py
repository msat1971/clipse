"""Public package interface for clipse.

Examples:
    >>> from clipse import __version__, load_config  # doctest: +SKIP
    >>> isinstance(__version__, str)
    True
"""

from ._version import __version__
from .core import load_config

__all__ = ["__version__", "load_config"]
