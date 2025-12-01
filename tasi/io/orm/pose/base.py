from typing import Optional

from tasi.io.orm.base import Base, PositionORM

from ..base import IdPrimaryKeyMixin
from ..utils import *
from .core import PoseORMBase


class PoseORM(Base, PoseORMBase, IdPrimaryKeyMixin):

    # The position in local UTM coordinates
    id_position: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    position: Mapped[Optional[PositionORM]] = relationship()

    id_trajectory: Mapped[Optional[int]] = mapped_column(
        ForeignKey("schema.trajectory.id")
    )

    trajectory: Mapped[Optional["TrajectoryORM"]] = relationship()


MODELS = [PoseORM]
