from ..base import BaseModel
from ..traffic_participant import TrafficParticipant


class TrajectoryBase(BaseModel):

    #: A reference to the traffic participant
    traffic_participant: TrafficParticipant


class GeoTrajectoryBase(TrajectoryBase): ...
