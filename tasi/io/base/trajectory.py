from sqlmodel import Field

from tasi.io.base import Base, IdPrimaryKeyMixing
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import ORMBase


class TrajectoryORMBase(Base, ORMBase, IdPrimaryKeyMixing):

    __abstract__ = True

    id_traffic_participant: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trafficparticipant.id",
        unique=True,
    )
