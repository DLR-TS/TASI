from typing import Optional

from geoalchemy2 import Geometry, WKBElement

from tasi.io.orm.base import Base

from ..base import Base, IdPrimaryKeyMixin
from ..traffic_participant import TrafficParticipantORM
from ..utils import *
from .core import TrajectoryORMBase

__all__ = ["GeoTrajectoryORM"]


class GeoTrajectoryORM(Base, TrajectoryORMBase, IdPrimaryKeyMixin):

    poses: Mapped[list["GeoPoseORM"]] = relationship(back_populates="trajectory")

    geometry: Mapped[WKBElement] = mapped_column(Geometry("LINESTRING", srid=32632))

    @declared_attr
    def traffic_participant(self) -> Mapped[Optional[TrafficParticipantORM]]:
        return relationship(
            TrafficParticipantORM,
            back_populates="geotrajectory",
        )


MODELS = [GeoTrajectoryORM]
