from datetime import datetime

from tasi.io.public.base import (
    Acceleration,
    BaseModel,
    BoundingBox,
    Classifications,
    Dimension,
    Orientation,
    Velocity,
)
from tasi.io.public.traffic_participant import TrafficParticipant


class PoseBase(BaseModel):

    #: The time of the pose
    timestamp: datetime

    #: Orientation of the traffic participant
    orientation: Orientation

    #: The dimension of the traffic participant measurement for the pose's time
    dimension: Dimension

    #: A reference to the traffic participant this pose belongs to
    traffic_participant: TrafficParticipant

    #: The traffic participant's velocity
    velocity: Velocity

    #: The traffic participant's acceleration
    acceleration: Acceleration

    #: The traffic participant's boundingbox
    boundingbox: BoundingBox

    #: The traffic participant's object type probabilities
    classifications: Classifications


class GeoPoseBase(PoseBase):
    pass
