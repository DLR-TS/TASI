from sqlmodel import Field, Relationship

from tasi.io.base import Base, IdPrimaryKeyMixing
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import ORMBase
from tasi.io.orm.pose import PoseORM, TrafficParticipantORM

__all__ = ["TrajectoryORM"]


class TrajectoryORMBase(Base, ORMBase, IdPrimaryKeyMixing):

    __abstract__ = True

    id_traffic_participant: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trafficparticipant.id",
        unique=True,
    )


class TrajectoryORM(TrajectoryORMBase, table=True):

    poses: list[PoseORM] = Relationship(back_populates="trajectory")

    traffic_participant: TrafficParticipantORM = Relationship(  # type: ignore
        back_populates="trajectory",
    )


MODELS = [TrajectoryORM]
