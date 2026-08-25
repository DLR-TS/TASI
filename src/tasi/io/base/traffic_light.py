from datetime import datetime

from tasi.io.base import Base


class TrafficLightStateBase(Base):
    """Traffic light states according to Vienna Convention, Article 23"""

    #: Red signal value
    red: bool = False

    #: Amber signal value
    amber: bool = False

    #: Green signal value
    green: bool = False

    #: The signal is unknown
    unknown: bool = False

    #: Any other state
    other: int = -1


class TrafficLightBase(Base):

    #: The time of traffic light state
    timestamp: datetime

    #: Indicate if the traffic light is flashing
    flashing: bool
