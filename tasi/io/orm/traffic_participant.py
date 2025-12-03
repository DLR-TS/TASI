from datetime import datetime
from typing import Optional, Self

from sqlalchemy import BIGINT

from .base import Base, ClassificationsORM, DimensionORM
from .utils import *

__all__ = ["TrafficParticipantORM"]


class TrafficParticipantORM(Base):

    #: A unique identifier
    id_object: Mapped[int] = mapped_column(BIGINT, primary_key=True)

    #: The first time the traffic participant was within the measurement site
    start_time: Mapped[Optional[datetime]]

    #: The last time the traffic participant was within the measurement site
    end_time: Mapped[Optional[datetime]]

    id_dimension: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{DimensionORM.__tablename__}.id")
    )

    id_classification: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{ClassificationsORM.__tablename__}.id")
    )

    trajectory: Mapped[Optional["TrajectoryORM"]] = relationship(
        back_populates="traffic_participant"
    )

    geotrajectory: Mapped[Optional["GeoTrajectoryORM"]] = relationship(
        back_populates="traffic_participant"
    )

    dimension: Mapped[Optional[DimensionORM]] = relationship()

    classifications: Mapped[Optional[ClassificationsORM]] = relationship()

    @classmethod
    def by_id_object(cls, id_object: int, session: Session, **kwargs) -> Self:

        entry: Optional[Self] = session.get(cls, id_object)

        if entry is None:
            entry = cls(id_object=id_object, **kwargs)
            session.add(entry)
        elif kwargs:
            # update the traffic participant if already available but additional params are given
            for k, v in kwargs.items():
                setattr(entry, k, v)
        return entry


MODELS = [TrafficParticipantORM]
