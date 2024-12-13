from . import _version
from .dataset import *

__version__ = _version.get_versions()["version"]

from .logging import init_logger

init_logger()
