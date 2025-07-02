from typing import Any, Dict, Union

from sqlmodel import Field, Relationship
from sqlmodel.main import SQLModel

from tasi.io.base import (
    AccelerationBase,
    BoundingBoxBase,
    ClassificationsBase,
    DimensionBase,
    PositionBase,
    VelocityBase,
)
from tasi.io.env import DEFAULT_DATABASE_SETTINGS

__all__ = [
    "ClassificationsORM",
    "VelocityORM",
    "AccelerationORM",
    "DimensionORM",
    "PositionORM",
    "BoundingBoxORM",
    "ORMBase",
]


class ORMBase:

    @classmethod
    def model_validate(
        cls: Any,
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        update: Union[Dict[str, Any], None] = None,
    ) -> SQLModel: ...


from typing import TypeVar

_ORMBase = TypeVar("_ORMBase", bound=ORMBase)


class IdPrimaryKeyMixing:

    id: int | None = Field(default=None, primary_key=True)


class ClassificationsORM(
    ClassificationsBase, IdPrimaryKeyMixing, ORMBase, table=True
): ...


class VelocityORM(VelocityBase, IdPrimaryKeyMixing, ORMBase, table=True): ...


class AccelerationORM(AccelerationBase, IdPrimaryKeyMixing, ORMBase, table=True): ...


class DimensionORM(DimensionBase, IdPrimaryKeyMixing, ORMBase, table=True): ...


class PositionORM(PositionBase, IdPrimaryKeyMixing, ORMBase, table=True): ...


class BoundingBoxORM(BoundingBoxBase, IdPrimaryKeyMixing, ORMBase, table=True):

    id_front_left: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )

    front_left: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_front_left]"},
    )

    id_front: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    front: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_front]"},
    )

    id_front_right: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    front_right: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_front_right]"},
    )

    id_right: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    right: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_right]"},
    )

    id_rear_right: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    rear_right: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_rear_right]"},
    )

    id_rear: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )

    rear: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_rear]"},
    )

    id_rear_left: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    rear_left: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_rear_left]"},
    )

    id_left: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id"
    )
    left: PositionORM | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BoundingBoxORM.id_left]"},
    )


MODELS = [
    ClassificationsORM,
    VelocityORM,
    AccelerationORM,
    DimensionORM,
    PositionORM,
    BoundingBoxORM,
]
