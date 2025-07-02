from datetime import datetime

from tasi.io.base import Base, Orientation


class PoseBase(Base):

    timestamp: datetime
    #: The time of the pose

    orientation: Orientation
    #: Orientation of the traffic participant


class GeoPoseBase(PoseBase):
    pass
