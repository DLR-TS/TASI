"""TASI - Traffic Situation Analysis and Interpretation.

This package exposes core traffic data structures and analysis tools for
trajectories, poses, and datasets. It initializes the default logger on import.
"""

from . import _version
from .dataset import *
from .pose import *
from .trajectory import *

__version__ = _version.get_versions()["version"]

from .logging import init_logger

init_logger()
