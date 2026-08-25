from typing import Optional, Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    mapped_column,
    relationship,
)

__all__ = [
    "ClassificationsORM",
    "VelocityORM",
    "AccelerationORM",
    "DimensionORM",
    "PositionORM",
    "BoundingBoxORM",
    "Base",
]


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        name: str = cls.__name__.lower()

        if name.endswith("orm"):
            name = name[:-3]

        return name

    @declared_attr
    def __table_args__(cls):
        return {"schema": "schema"}

    def get(self, session: Session, **kwargs) -> Self:
        """Get the entry from the database of this entity based on the given keyword-arguments.

        Args:
            session (Session): The SQLAlchemy session

        Returns:
            Self: Either the entity that is available in the database matching
            the keyword-arguments as WHERE claus or a new instance.

        """
        entry = session.query(type(self)).filter_by(**kwargs).one_or_none()

        if entry is None:
            entry = type(self)(**kwargs)

        return entry


class IdPrimaryKeyMixin:

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class ClassificationsORM(Base, IdPrimaryKeyMixin):

    unknown: Mapped[float]

    pedestrian: Mapped[float]

    bicycle: Mapped[float]

    motorbike: Mapped[float]

    car: Mapped[float]

    van: Mapped[float]

    truck: Mapped[float]

    other: Mapped[float]


class Vector3DMixin:

    __abstract__ = True

    x: Mapped[float]

    y: Mapped[float]

    z: Mapped[float]

    magnitude: Mapped[Optional[float]]


class VelocityORM(Base, Vector3DMixin, IdPrimaryKeyMixin): ...


class AccelerationORM(Base, Vector3DMixin, IdPrimaryKeyMixin): ...


class DimensionORM(Base, IdPrimaryKeyMixin):

    width: Mapped[float]
    """float: The traffic participant's width in meter"""

    height: Mapped[float]
    """float: The traffic participant's height in meter"""

    length: Mapped[float]
    """float: The traffic participant's length in meter"""


class PositionORM(Base, IdPrimaryKeyMixin):

    easting: Mapped[float]

    northing: Mapped[float]

    altitude: Mapped[Optional[float]]


class BoundingBoxORM(Base, IdPrimaryKeyMixin):

    id_front_left: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_front: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_front_right: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_right: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_rear_right: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_rear: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_rear_left: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    id_left: Mapped[int] = mapped_column(
        ForeignKey(f"schema.{PositionORM.__tablename__}.id")
    )

    front_left: Mapped[PositionORM] = relationship(
        PositionORM, foreign_keys=[id_front_left]
    )

    front: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_front]
    )

    front_right: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_front_right]
    )

    right: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_right]
    )

    rear_right: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_rear_right]
    )

    rear: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_rear]
    )

    rear_left: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_rear_left]
    )

    left: Mapped[Optional[PositionORM]] = relationship(
        PositionORM, foreign_keys=[id_left]
    )


MODELS = [
    ClassificationsORM,
    VelocityORM,
    AccelerationORM,
    DimensionORM,
    PositionORM,
    BoundingBoxORM,
]
