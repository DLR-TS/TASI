from typing import Self, Union

from sqlmodel import Field, Relationship, Session, select

from tasi import Pose as TASIPose
from tasi import Trajectory as TASITrajectory
from tasi.io.base import IdPrimaryKeyMixing
from tasi.io.base.traffic_participant import TrafficParticipantBase
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import ClassificationsORM, DimensionORM, ORMBase


class TrafficParticipantORM(
    TrafficParticipantBase, ORMBase, IdPrimaryKeyMixing, table=True
):

    trajectory: Union["TrajectoryORM", None] = Relationship(  # type: ignore
        back_populates="traffic_participant"
    )

    geotrajectory: Union["GeoTrajectoryORM", None] = Relationship(  # type: ignore
        back_populates="traffic_participant"
    )

    id_dimension: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.dimension.id"
    )

    dimension: DimensionORM | None = Relationship()

    id_classification: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.classifications.id",
    )

    classifications: ClassificationsORM | None = Relationship()

    @classmethod
    def by_id_object(cls, id_object: int, session: Session, **kwargs) -> Self:

        entry = session.exec(
            select(cls).where(cls.id_object == id_object)
        ).one_or_none()

        if entry is None:
            entry = cls(id_object=id_object, **kwargs)
            session.add(entry)
        elif kwargs:
            # update the traffic participant if already available but additional params are given
            for k, v in kwargs.items():
                setattr(entry, k, v)
        return entry


MODELS = [TrafficParticipantORM]
