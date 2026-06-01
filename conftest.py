"""Test bootstrap.

Run tests against the pure-Python source tree when the package is *not*
installed, but defer to the installed package (which carries the compiled
``typosquat._core`` Rust kernel) when it *is*. This lets the same suite exercise
both the pure-Python fallback and the accelerated path with no config changes.
"""

import importlib.util
import sys
from pathlib import Path

if importlib.util.find_spec("typosquat") is None:
    sys.path.insert(0, str(Path(__file__).parent / "python"))
