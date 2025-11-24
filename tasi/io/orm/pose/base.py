from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from tasi.io.base.pose import PoseBase
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    IdPrimaryKeyMixing,
    ORMBase,
    PositionORM,
    VelocityORM,
)
from tasi.io.orm.traffic_participant import TrafficParticipantORM


class PoseORMBase(PoseBase, ORMBase, IdPrimaryKeyMixing):

    @declared_attr  # type: ignore
    def __table_args__(cls):
        return (
            UniqueConstraint(
                "timestamp",
                "id_traffic_participant",
                name="uniq_pose_per_trajectory_scene" + cls.__tablename__,
            ),
            {"schema": DEFAULT_DATABASE_SETTINGS.CONTEXT},
        )

    # The dimension of the traffic participant at that time
    id_dimension: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.dimension.id"
    )

    id_traffic_participant: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trafficparticipant.id",
    )

    id_velocity: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.velocity.id"
    )

    id_acceleration: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.acceleration.id",
    )

    id_boundingbox: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.boundingbox.id",
    )

    id_classification: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.classifications.id",
    )


class PoseORM(PoseORMBase, table=True):

    dimension: DimensionORM = Relationship()

    # The position in local UTM coordinates
    id_position: int | None = Field(
        default=None,
        description="The position in local UTM coordinates",
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id",
    )
    position: PositionORM = Relationship()

    id_trajectory: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trajectory.id"
    )

    trajectory: Optional["TrajectoryORM"] = Relationship(  # type: ignore
        back_populates="poses",
        sa_relationship_kwargs={"foreign_keys": "[PoseORM.id_trajectory]"},
    )  # type: ignore

    traffic_participant: TrafficParticipantORM = Relationship()

    velocity: VelocityORM = Relationship()

    acceleration: AccelerationORM = Relationship()

    boundingbox: BoundingBoxORM = Relationship()

    classifications: ClassificationsORM = Relationship()


MODELS = [PoseORM]
