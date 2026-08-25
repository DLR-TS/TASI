from tasi.io.orm.base import MODELS as BASE_MODELS
from tasi.io.orm.base import *
from tasi.io.orm.pose.base import MODELS as POSE_MODELS
from tasi.io.orm.pose.base import *
from tasi.io.orm.traffic_light import MODELS as TL_MODELS
from tasi.io.orm.traffic_light import *
from tasi.io.orm.traffic_participant import MODELS as TP_MODELS
from tasi.io.orm.traffic_participant import TrafficParticipantORM
from tasi.io.orm.trajectory.base import MODELS as TJ_MODELS
from tasi.io.orm.trajectory.base import *

from .db import DatabaseSettings, create_tables, drop_tables

MODELS = [*BASE_MODELS, *TP_MODELS, *TJ_MODELS, *POSE_MODELS, *TL_MODELS]

__all__ = [
    "ClassificationsORM",
    "VelocityORM",
    "AccelerationORM",
    "DimensionORM",
    "PositionORM",
    "BoundingBoxORM",
    "PoseORM",
    "TrafficParticipantORM",
    "TrajectoryORM",
    "TrafficLightStateORM",
    "TrafficLightORM",
    "DatabaseSettings",
    "create_tables",
    "drop_tables",
]
from tasi.utils import has_extra

# add geo models if geo module is active
EXTRA = has_extra("geo")

if EXTRA:
    from .geo import MODELS as GEO_MODELS
    from .geo import *

    __all__.extend(["GeoPoseORM", "GeoTrajectoryORM"])

    MODELS.extend(GEO_MODELS)
