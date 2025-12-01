from abc import ABC, abstractmethod
from typing import (
    Annotated,
    Dict,
    List,
    Literal,
    Self,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

import numpy as np
import pandas as pd
from pydantic import BaseModel as Base
from pydantic import ConfigDict, Field, model_validator

import tasi
from tasi.base import TASIBase
from tasi.io.orm.base import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    PositionORM,
    VelocityORM,
)
from tasi.io.util import FlatDict

__all__ = [
    "Acceleration",
    "BoundingBox",
    "Classifications",
    "Dimension",
    "Orientation",
    "Position",
    "Velocity",
]
T = TypeVar("T", bound="FromTASIMixin")


TASI_COLUMN_MAPPING_VECTOR = {"easting": "x", "northing": "y", "altitude": "z"}
TASI_COLUMN_MAPPING_VECTOR_INV = {v: k for k, v in TASI_COLUMN_MAPPING_VECTOR.items()}


def flatten_dataframe_columns(df: pd.DataFrame, max_levels=1):
    if df.columns.nlevels > max_levels:
        try:
            df = df.droplevel(level=1, axis=1)
        except:
            df = df.droplevel(level=1)

    return df


class DataFrameConversionMixin:

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)  # type: ignore

    def as_dict(self) -> dict:
        return self.model_dump()

    def as_flat_dict(
        self,
        drop: str | List[str] = "",
        replace: Dict[str, str] | None = None,
        **kwargs,
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


class FromTASIMixin:

    @overload
    @classmethod
    def from_tasi(cls: Type[T], obj: tasi.Pose, **kwargs) -> T:
        """Factory method to create instance from a `tasi.Pose`

        Args:
            obj (tasi.Pose): The :ref:`tasi.Pose`

        Returns:
            T: Instance of current class
        """
        ...

    @overload
    @classmethod
    def from_tasi(
        cls: Type[T], obj: tasi.Trajectory, **kwargs
    ) -> Union[Sequence[T], T]:
        """Factory method to create instance from a `tasi.Trajectory`

        Args:
            obj (tasi.Pose): The :ref:`tasi.Trajectory`

        Returns:
            T: Instance of current class
        """
        ...

    @classmethod
    def from_tasi(cls: Type[T], obj: Union[tasi.Pose, tasi.Trajectory], **kwargs):
        raise NotImplementedError("Implement the from_tasi() method")


class AsTASIMixin(ABC):

    @abstractmethod
    def as_tasi(
        self, as_record: bool = False, **kwargs
    ) -> pd.DataFrame | TASIBase | Dict: ...


class AsORMMixin(ABC):

    def as_orm(self, **kwargs):
        """Convert to its ORM representation

        Returns:
            _ORMBase: The ORM model that can be used for saving

        """
        import typing

        func = getattr(self, "as_orm")

        return typing.get_type_hints(func)["return"](**self.model_dump())


class PublicEntityMixin(AsORMMixin, AsTASIMixin, FromTASIMixin): ...


Orientation = Annotated[float, Field(ge=-np.pi, le=np.pi)]


class BaseModel(Base, DataFrameConversionMixin):

    model_config = ConfigDict(from_attributes=True)


class Classifications(BaseModel, PublicEntityMixin):

    unknown: float = 0

    pedestrian: float = 0

    bicycle: float = 0

    motorbike: float = 0

    car: float = 0

    van: float = 0

    truck: float = 0

    other: float = 0

    def as_orm(self, **kwargs) -> ClassificationsORM:
        """Convert to ORM representation

        Returns:
            ClassificationsORM: The orm model instance that can be used for saving
        """
        return super().as_orm()

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(
        cls, obj: Union[tasi.Pose, tasi.Trajectory], **kwargs
    ) -> Self | Sequence[Self]:

        df = flatten_dataframe_columns(obj.classifications).replace({float("nan"): None})  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.model_validate(df.iloc[0].to_dict())
        elif isinstance(obj, tasi.Trajectory):
            return [cls.model_validate(row) for i, row in df.iterrows()]
        return super().from_tasi(obj)

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        if as_record:
            default_kwargs = dict(prefix="classifications", nlevels=3)
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore

        return self.as_dataframe()


class Vector3DBase(BaseModel):

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


class Velocity(PublicEntityMixin, Vector3DBase):
    """The velocity as 3-dimensional vector"""

    def as_orm(self, **kwargs) -> VelocityORM:
        """Convert to its ORM representation

        Returns:
            VelocityORM: The ORM model instance that can be used for saving
        """
        return super().as_orm()

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(
        cls, obj: tasi.Pose | tasi.Trajectory, **kwargs
    ) -> Self | Sequence[Self]:

        df = flatten_dataframe_columns(obj.velocity.rename(columns=TASI_COLUMN_MAPPING_VECTOR)).replace({float("nan"): None})  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.model_validate(df.iloc[0].to_dict())
        elif isinstance(obj, tasi.Trajectory):
            return [cls.model_validate(row) for i, row in df.iterrows()]
        return super().from_tasi(obj)

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        if as_record:
            default_kwargs = dict(
                prefix="velocity", nlevels=3, replace=TASI_COLUMN_MAPPING_VECTOR_INV
            )
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore

        return self.as_dataframe()[["x", "y", "magnitude"]].rename(
            columns=TASI_COLUMN_MAPPING_VECTOR_INV
        )

    def __mul__(self, o: float) -> "Position":
        return Position(easting=self.x * o, northing=self.y * o)


class Acceleration(PublicEntityMixin, Vector3DBase):
    """The velocity as 3-dimensional vector"""

    def as_orm(self, **kwargs) -> AccelerationORM:
        """Convert to its ORM representation

        Returns:
            AccelerationORM: The ORM model instance that can be used for saving
        """
        return super().as_orm()

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(
        cls, obj: tasi.Pose | tasi.Trajectory, **kwargs
    ) -> Self | Sequence[Self]:

        df = flatten_dataframe_columns(obj.acceleration.rename(columns=TASI_COLUMN_MAPPING_VECTOR)).replace({float("nan"): None})  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.model_validate(df.iloc[0].to_dict())
        elif isinstance(obj, tasi.Trajectory):
            return [cls.model_validate(row) for i, row in df.iterrows()]
        return super().from_tasi(obj)

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        if as_record:
            default_kwargs = dict(
                prefix="acceleration", nlevels=3, replace=TASI_COLUMN_MAPPING_VECTOR_INV
            )
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore

        return self.as_dataframe()[["x", "y", "magnitude"]].rename(
            columns=TASI_COLUMN_MAPPING_VECTOR_INV
        )


class Dimension(BaseModel, PublicEntityMixin):
    """The dimension of a traffic participant"""

    width: float
    """float: The traffic participant's width in meter"""

    height: float
    """float: The traffic participant's height in meter"""

    length: float
    """float: The traffic participant's length in meter"""

    def as_orm(self, **kwargs) -> DimensionORM:
        """Convert to its ORM representation

        Returns:
            DimensionORM: The ORM model instance that can be used for saving
        """
        return super().as_orm()

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self:
        """Factory method to create an instance based on a `tasi.pose`_

        Returns:
            Self: A new instance
        """
        ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]:
        """Factory method to create an instance based on a `tasi.trajectory`_

        Returns:
            Self: A new instance
        """
        ...

    @classmethod
    def from_tasi(
        cls, obj: tasi.Pose | tasi.Trajectory, **kwargs
    ) -> Self | Sequence[Self]:

        df = flatten_dataframe_columns(obj.dimension).replace({float("nan"): None})  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.model_validate(df.iloc[0].to_dict())
        elif isinstance(obj, tasi.Trajectory):
            return [cls.model_validate(row) for i, row in df.iterrows()]
        return super().from_tasi(obj)

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        if as_record:
            default_kwargs = dict(prefix="dimension", nlevels=3)
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore

        return self.as_dataframe()


class Position(BaseModel, PublicEntityMixin):

    easting: float

    northing: float

    altitude: float | None = 0

    @overload
    def __add__(self, o: VelocityBase): ...

    @overload
    def __add__(self, o: "Position"): ...

    def __add__(self, o: Union["Position", VelocityBase]):

        if isinstance(o, VelocityBase):
            self.easting += o.x
            self.northing += o.y

            if o.z is not None and self.altitude is not None:
                self.altitude += o.z

        elif isinstance(o, Position):

            self.easting += o.easting
            self.northing += o.northing

            if self.altitude is not None and o.altitude is not None:
                self.altitude += o.altitude

        return self

    @overload
    def __sub__(self, o: VelocityBase): ...

    @overload
    def __sub__(self, o: "Position"): ...

    def __sub__(self, o: Union["Position", VelocityBase]):

        if isinstance(o, VelocityBase):
            self.easting -= o.x
            self.northing -= o.y

            if o.z is not None and self.altitude is not None:
                self.altitude -= o.z

        elif isinstance(o, Position):

            self.easting -= o.easting
            self.northing -= o.northing

            if self.altitude is not None and o.altitude is not None:
                self.altitude -= o.altitude

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

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(
        cls, obj: Union[tasi.Pose, tasi.Trajectory], **kwargs
    ) -> Union[Self, Sequence[Self]]:

        df = flatten_dataframe_columns(obj.position).replace({float("nan"): None})  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.model_validate(df.iloc[0].to_dict())
        elif isinstance(obj, tasi.Trajectory):
            return [cls.model_validate(row) for i, row in df.iterrows()]
        return super().from_tasi(obj)

    def as_orm(self, **kwargs) -> PositionORM:
        """Convert to its ORM representation

        Returns:
            PositionORM: The ORM model instance that can be used for saving
        """
        return super().as_orm()

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:  # type: ignore

        if as_record:
            default_kwargs = dict(prefix="position", nlevels=3)
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore
        else:
            return self.as_dataframe()[["easting", "northing"]]

    @classmethod
    def from_wkt(cls, wkt: str) -> Self:
        """Initialize a :class:`Position` from a geometric object defined using
        the Well-Known-Text (WKT) format

        Args:
            wkt (str): The geometry in the Well-Known-Text format

        Returns:
            Self: A new instance
        """
        from shapely import from_wkt

        coordinates = from_wkt(wkt).coords[0]

        return cls(easting=coordinates[0], northing=coordinates[1])


class BoundingBox(BaseModel, PublicEntityMixin):

    #: The front left position
    front_left: Position

    #: The front center position
    front: Position

    #: The front right position
    front_right: Position

    #: The center right position
    right: Position

    #: The rear right position
    rear_right: Position

    #: The rear center position
    rear: Position

    #: The rear left position
    rear_left: Position

    #: The center left position
    left: Position

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

    @classmethod
    def from_series(cls, se: pd.Series) -> Self:
        return cls(
            front_left=Position.from_series(se.front_left),
            front=Position.from_series(se.front),
            front_right=Position.from_series(se.front_right),
            right=Position.from_series(se.right),
            rear_right=Position.from_series(se.rear_right),
            rear=Position.from_series(se.rear),
            rear_left=Position.from_series(se.rear_left),
            left=Position.from_series(se.left),
        )

    @classmethod
    def from_dimension(
        cls,
        dimension: Dimension,
        relative_to: Position,
        orientation: Orientation = 0,
    ) -> Self:
        """Create an instance based on a traffic participant's dimension, a
        reference position and orientation.

        Args:
            dimension (:class:`tasi.io.Dimension`): The dimension of the boundingbox
            relative_to (:class:`tasi.io.Position`): The reference position
            orientation (:class:`tasi.io.Orientation`): The orientation in radians. Defaults to 0.

        Returns:
            Self: A new instance
        """
        return cls(
            front_left=Position(
                easting=dimension.length / 2, northing=dimension.width / 2
            ).rotate2d(orientation)
            + relative_to,
            front=Position(easting=dimension.length / 2, northing=0).rotate2d(
                orientation
            )
            + relative_to,
            front_right=Position(
                easting=dimension.length / 2, northing=-dimension.width / 2
            ).rotate2d(orientation)
            + relative_to,
            right=Position(easting=0, northing=-dimension.width / 2).rotate2d(
                orientation
            )
            + relative_to,
            rear_right=Position(
                easting=-dimension.length / 2, northing=-dimension.width / 2
            ).rotate2d(orientation)
            + relative_to,
            rear=Position(easting=-dimension.length / 2, northing=0).rotate2d(
                orientation
            )
            + relative_to,
            rear_left=Position(
                easting=-dimension.length / 2, northing=dimension.width / 2
            ).rotate2d(orientation)
            + relative_to,
            left=Position(easting=0, northing=dimension.width / 2).rotate2d(orientation)
            + relative_to,
        )

    def as_orm(self, **kwargs) -> BoundingBoxORM:
        """Convert to its ORM representation

        Returns:
            BoundingBoxORM: The ORM model instance that can be used for saving
        """
        return BoundingBoxORM(
            front_left=self.front_left.as_orm(),
            front=self.front.as_orm(),
            front_right=self.front_right.as_orm(),
            right=self.right.as_orm(),
            rear_right=self.rear_right.as_orm(),
            rear=self.rear.as_orm(),
            rear_left=self.rear_left.as_orm(),
            left=self.left.as_orm(),
        )

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:

        sides = [
            "front_left",
            "front",
            "front_right",
            "right",
            "rear_right",
            "rear",
            "rear_left",
            "left",
        ]
        if as_record:
            attr = {}
            for side in sides:
                attr.update(
                    getattr(self, side).as_tasi(
                        as_record=as_record, prefix=("boundingbox", side)
                    )
                )

            return attr
        else:
            attr = {}
            for side in sides:
                p: Position = getattr(self, side)

                attr[side] = p.as_tasi(as_record=False)

            return pd.concat(attr).droplevel(axis=0, level=1).stack().to_frame().T  # type: ignore

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(  # type: ignore
        cls, obj: tasi.Pose | tasi.Trajectory, **kwargs
    ) -> Self | Sequence[Self]:

        bbox: pd.DataFrame = obj.boundingbox  # type: ignore

        if isinstance(obj, tasi.Pose):
            return cls.from_series(bbox.iloc[0])
        elif isinstance(obj, tasi.Trajectory):
            return cls.from_dataframe(bbox.rename(columns=TASI_COLUMN_MAPPING_VECTOR))  # type: ignore
        else:
            raise ValueError(f"Unsupported type {type(obj)}")
