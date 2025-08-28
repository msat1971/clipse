"""
Public package interface for clipse.
"""

from ._version import __version__
from .core import load_config

__all__ = ["__version__", "load_config"]
