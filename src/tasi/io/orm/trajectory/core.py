from typing import Optional

from ..base import IdPrimaryKeyMixin
from ..traffic_participant import TrafficParticipantORM
from ..utils import *


class TrajectoryORMBase:

    __abstract__ = True

    id_traffic_participant: Mapped[Optional[int]] = mapped_column(
        ForeignKey(f"schema.{TrafficParticipantORM.__tablename__}.id_object")
    )
