from sqlalchemy.engine import Engine

from tasi.io.orm.base import MODELS as BASE_MODELS
from tasi.io.orm.base import *
from tasi.io.orm.pose import MODELS as POSE_MODELS
from tasi.io.orm.pose import *
from tasi.io.orm.traffic_light import MODELS as TL_MODELS
from tasi.io.orm.traffic_light import *
from tasi.io.orm.traffic_participant import MODELS as TP_MODELS
from tasi.io.orm.traffic_participant import TrafficParticipantORM
from tasi.io.orm.trajectory import MODELS as TJ_MODELS
from tasi.io.orm.trajectory import *

MODELS = [*BASE_MODELS, *POSE_MODELS, *TP_MODELS, *TJ_MODELS, *TL_MODELS]

__all__ = [
    "ClassificationsORM",
    "VelocityORM",
    "AccelerationORM",
    "DimensionORM",
    "PositionORM",
    "BoundingBoxORM",
    "PoseORM",
    "GeoPoseORM",
    "TrafficParticipantORM",
    "TrajectoryORM",
    "GeoTrajectoryORM",
    "TrafficLightStateORM",
    "TrafficLightORM",
]


def create_tables(engine: Engine):
    from ..base import Base

    Base.metadata.create_all(tables=[m.__table__ for m in MODELS], bind=engine)


def drop_tables(engine: Engine):
    from ..base import Base

    Base.metadata.drop_all(tables=[m.__table__ for m in MODELS], bind=engine)
