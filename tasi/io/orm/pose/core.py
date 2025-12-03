from datetime import datetime
from typing import Optional

from tasi.io.orm.base import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    VelocityORM,
)
from tasi.io.orm.traffic_participant import TrafficParticipantORM

from ..utils import *


class PoseORMBase:

    __abstract__ = True

    #: The time of the pose
    timestamp: Mapped[datetime]

    #: Orientation of the traffic participant
    orientation: Mapped[float]

    @declared_attr  # type: ignore
    def __table_args__(cls):
        return (
            UniqueConstraint(
                "timestamp",
                "id_traffic_participant",
                name="schema.uniq_pose_per_trajectory_scene" + cls.__tablename__,
            ),
            {"schema": "schema"},
        )

    # The dimension of the traffic participant at that time
    id_dimension: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{DimensionORM.__tablename__}.id")
    )

    id_traffic_participant: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{TrafficParticipantORM.__tablename__}.id_object")
    )

    id_velocity: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{VelocityORM.__tablename__}.id")
    )

    id_acceleration: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{AccelerationORM.__tablename__}.id")
    )

    id_boundingbox: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{BoundingBoxORM.__tablename__}.id")
    )

    id_classification: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{ClassificationsORM.__tablename__}.id")
    )

    @declared_attr
    def dimension(self) -> Mapped[Optional[DimensionORM]]:
        return relationship(DimensionORM)

    @declared_attr
    def classifications(self) -> Mapped[Optional[ClassificationsORM]]:
        return relationship(ClassificationsORM)

    @declared_attr
    def traffic_participant(self) -> Mapped[Optional[TrafficParticipantORM]]:
        return relationship(TrafficParticipantORM)

    @declared_attr
    def velocity(self) -> Mapped[Optional[VelocityORM]]:
        return relationship(VelocityORM)

    @declared_attr
    def acceleration(self) -> Mapped[Optional[AccelerationORM]]:
        return relationship(AccelerationORM)

    @declared_attr
    def boundingbox(self) -> Mapped[Optional[BoundingBoxORM]]:
        return relationship(BoundingBoxORM)
