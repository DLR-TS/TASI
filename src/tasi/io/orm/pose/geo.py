from typing import Optional

from geoalchemy2 import Geometry

from ..utils import *
from .base import Base, IdPrimaryKeyMixin
from .core import PoseORMBase

__all__ = ["GeoPoseORM"]


class GeoPoseORM(Base, PoseORMBase, IdPrimaryKeyMixin):

    position = mapped_column(Geometry("POINT", srid=31467))

    id_trajectory: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.geotrajectory.id")
    )

    trajectory: Mapped[Optional["GeoTrajectoryORM"]] = relationship()


MODELS = [GeoPoseORM]
