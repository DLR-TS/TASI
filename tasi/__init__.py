from . import _version
from .dataset import *
from .pose import GeoPose, Pose, PoseBase
from .trajectory import GeoTrajectory, Trajectory

__version__ = _version.get_versions()["version"]

from .logging import init_logger

init_logger()
