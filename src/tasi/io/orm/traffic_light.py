from datetime import datetime

from tasi.io.orm.base import Base, IdPrimaryKeyMixin

from .utils import *

__all__ = ["TrafficLightStateORM", "TrafficLightORM"]


class TrafficLightStateORM(Base, IdPrimaryKeyMixin):

    #: Red signal value
    red: Mapped[bool]

    #: Amber signal value
    amber: Mapped[bool]

    #: Green signal value
    green: Mapped[bool]

    #: The signal is unknown
    unknown: Mapped[bool]

    #: Any other state
    other: Mapped[int] = mapped_column(default=-1)


class TrafficLightORM(Base, IdPrimaryKeyMixin):

    #: The time of traffic light state
    timestamp: Mapped[datetime]

    #: Indicate if the traffic light is flashing
    flashing: Mapped[bool]

    id_state: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{TrafficLightStateORM.__tablename__}.id")
    )

    state: Mapped[TrafficLightStateORM] = relationship()


MODELS = [TrafficLightORM, TrafficLightStateORM]
