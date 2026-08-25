from tasi.utils import has_extra

EXTRA = has_extra("geo")

if not EXTRA:
    raise ImportError(
        "The geo extra is missing but required for this module. Please install tasi[geo] to get access to it."
    )

from .pose.geo import MODELS as POSE_MODELS
from .pose.geo import *
from .trajectory.geo import MODELS as TRAJECTORY_MODELS
from .trajectory.geo import *

MODELS = [*POSE_MODELS, *TRAJECTORY_MODELS]

__all__ = ["GeoPoseORM", "GeoTrajectoryORM"]
