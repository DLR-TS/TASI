from typing import Optional

from ..base import Base, IdPrimaryKeyMixin
from ..traffic_participant import TrafficParticipantORM
from ..utils import *
from .core import TrajectoryORMBase

__all__ = ["TrajectoryORM"]


class TrajectoryORM(Base, TrajectoryORMBase, IdPrimaryKeyMixin):

    poses: Mapped[list["PoseORM"]] = relationship(back_populates="trajectory")

    @declared_attr
    def traffic_participant(self) -> Mapped[Optional[TrafficParticipantORM]]:
        return relationship(
            TrafficParticipantORM,
            back_populates="trajectory",
        )


MODELS = [TrajectoryORM]
