from datetime import datetime

from sqlalchemy import BigInteger
from sqlmodel import Field

from tasi.io.base import Base


class TrafficParticipantBase(Base):

    #: The first time the traffic participant was within the measurement site
    start_time: datetime | None = None

    #: The last time the traffic participant was within the measurement site
    end_time: datetime | None = None

    #: A unique identifier
    id_object: int = Field(sa_type=BigInteger, index=True, unique=True)
