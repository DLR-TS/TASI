from sqlmodel import Field, Relationship
from tasi.io.base.traffic_light import TrafficLightBase, TrafficLightStateBase
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import IdPrimaryKeyMixing, ORMBase


class TrafficLightStateORM(
    TrafficLightStateBase, ORMBase, IdPrimaryKeyMixing, table=True
):
    pass


class TrafficLightORM(ORMBase, TrafficLightBase, IdPrimaryKeyMixing, table=True):

    id_state: int | None = Field(
        default=None,
        description="The state of the traffic light",
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.{TrafficLightStateORM.__tablename__}.id",
    )

    state: TrafficLightStateORM = Relationship()


MODELS = [TrafficLightStateORM, TrafficLightORM]
