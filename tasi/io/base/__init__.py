from typing import Annotated, Dict, List, Self, Sequence, Union, overload

import numpy as np
import pandas as pd
from pydantic import model_validator
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel

from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.util import FlatDict


class SchemaByEnvironmentVariableMixin:

    @declared_attr  # type: ignore
    def __table_args__(cls):
        # pylint: disable=no-member
        return {"schema": DEFAULT_DATABASE_SETTINGS.CONTEXT}


class DataFrameConversionMixin:

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)  # type: ignore

    def as_dict(self) -> dict:
        return self.model_dump()

    def as_flat_dict(
        self,
        drop: str | List[str] = "",
        replace: Dict[str, str] | None = None,
        **kwargs
    ) -> FlatDict:

        attr = self.model_dump()

        if drop:
            if isinstance(drop, str):
                del attr[drop]
            elif isinstance(drop, list):
                list(map(attr.pop, drop))

        if replace is not None:
            for k, v in replace.items():
                attr[v] = attr.pop(k)

        return FlatDict.from_dict(attr, **kwargs)

    def as_series(self, name=None) -> pd.Series:
        return pd.Series(self.as_flat_dict(), name=name)  # type: ignore

    def as_dataframe(self) -> pd.DataFrame:
        return self.as_series().to_frame().T

    @classmethod
    def from_series(cls, se: pd.Series) -> Self:
        return cls(**se.to_dict())

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, **kwargs) -> Sequence[Self]:
        return [cls.from_series(row) for i, row in df.iterrows()]


class Base(DataFrameConversionMixin, SQLModel, SchemaByEnvironmentVariableMixin):

    @declared_attr  # type: ignore
    def __tablename__(cls):  # type: ignore
        name: str = cls.__name__.lower()  # type: ignore

        if name.endswith("orm"):
            name = name[:-3]

        return name


class IdPrimaryKeyMixing:

    id: int | None = Field(default=None, primary_key=True)


Orientation = Annotated[float, Field(ge=-np.pi, le=np.pi)]


class ClassificationsBase(Base):
    """Object classification probabilities"""

    unknown: float = 0

    pedestrian: float = 0

    bicycle: float = 0

    motorbike: float = 0

    car: float = 0

    van: float = 0

    truck: float = 0

    other: float = 0


class Vector3DBase(Base):

    x: float = 0

    y: float = 0

    z: float = 0

    magnitude: float | None = None

    def __add__(self, o: Self):
        self.x += o.x
        self.y += o.y
        self.z += o.z

        return self

    @model_validator(mode="after")  # type: ignore
    def _either_attr_or_magnitude(cls, m: Self) -> Self:

        has_magnitude = m.magnitude is not None

        # x and y are the mandatory fields if magnitude is not given
        attrs = [getattr(m, f) is not None for f in ["x", "y"]]

        has_all_attributes = all(attrs)
        has_any_attributes = any(attrs)

        if has_any_attributes and not has_all_attributes:
            raise ValueError("Supply **both** attributes.")

        if has_magnitude or has_all_attributes:
            return m

        raise ValueError(
            "Supply **either** magnitude (and leave the attributes empty) "
            "**or** the attributes together (x,y) with magnitude (optional)."
        )

    @classmethod
    def from_magnitude(cls, magnitude: float, orientation: Orientation) -> Self:

        return cls(
            x=np.cos(orientation) * magnitude,
            y=np.sin(orientation) * magnitude,
            magnitude=magnitude,
        )


class VelocityBase(Vector3DBase): ...


class AccelerationBase(Vector3DBase): ...


class DimensionBase(Base):

    width: float
    """float: The traffic participant's width in meter"""

    height: float
    """float: The traffic participant's height in meter"""

    length: float
    """float: The traffic participant's length in meter"""


class PositionBase(Base):

    easting: float

    northing: float

    altitude: float | None = 0

    @overload
    def __add__(self, o: VelocityBase): ...

    @overload
    def __add__(self, o: "PositionBase"): ...

    def __add__(self, o: Union["PositionBase", VelocityBase]):

        if isinstance(o, VelocityBase):
            self.easting += o.x
            self.northing += o.y

            if o.z is not None and self.altitude is not None:
                self.altitude += o.z

        elif isinstance(o, PositionBase):

            self.easting += o.easting
            self.northing += o.northing

            if self.altitude is not None and o.altitude is not None:
                self.altitude += o.altitude

        return self

    @classmethod
    def from_3dvector(cls, vec: Vector3DBase) -> Self:
        return cls(easting=vec.x, northing=vec.y, altitude=vec.z)

    def rotate2d(self, orientation: Orientation) -> Self:
        """Rotate the location by orientation assumed as 'yaw'."""

        from tasi.calculus import rotate_points

        x, y = rotate_points(
            np.asarray([self.easting, self.northing]), orientation, degree=False
        )

        return type(self)(
            easting=x,
            northing=y,
            altitude=self.altitude,
        )


class BoundingBoxBase(Base):

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, **kwargs) -> Sequence[Self]:
        return [cls.from_series(row) for i, row in df.iterrows()]

    def as_dataframe(self):
        index = self.model_dump().keys()

        return (
            pd.concat(
                [getattr(self, a).as_dataframe() for a in self.model_dump()], keys=index
            )
            .reset_index(level=1, drop=True)
            .stack()
            .to_frame()
            .T
        )
