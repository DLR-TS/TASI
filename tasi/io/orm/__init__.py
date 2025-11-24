from sqlalchemy import Engine

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

MODELS = [*BASE_MODELS, *POSE_MODELS, *TP_MODELS, *TJ_MODELS, *TL_MODELS]

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
]
from tasi.utils import has_extra

# add geo models if geo module is active
EXTRA = has_extra("geo")

if EXTRA:
    from .geo import MODELS as GEO_MODELS

    MODELS.extend(GEO_MODELS)


def create_tables(engine: Engine):
    from ..base import Base

    Base.metadata.create_all(tables=[m.__table__ for m in MODELS], bind=engine)


def drop_tables(engine: Engine):
    from ..base import Base

    Base.metadata.drop_all(tables=[m.__table__ for m in MODELS], bind=engine)
