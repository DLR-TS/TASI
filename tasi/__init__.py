from . import _version
from .dataset import *
from .pose import PoseBase, Pose, GeoPose
from .trajectory import Trajectory, GeoTrajectory

__version__ = _version.get_versions()["version"]

from .logging import init_logger

init_logger()
