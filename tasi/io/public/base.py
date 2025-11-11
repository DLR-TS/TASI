from abc import ABC, abstractmethod
from typing import Dict, Literal, Self, Sequence, Type, TypeVar, Union, overload

import pandas as pd

import tasi
from tasi.base import TASIBase
from tasi.io.base import (
    AccelerationBase,
    BoundingBoxBase,
    ClassificationsBase,
    DimensionBase,
    Orientation,
    PositionBase,
    VelocityBase,
)
from tasi.io.orm.base import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    PositionORM,
    VelocityORM,
    _ORMBase,
)

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

    def as_orm(self, **kwargs) -> _ORMBase:
        """Convert to its ORM representation

        Returns:
            _ORMBase: The ORM model that can be used for saving

        """
        import typing

        func = getattr(self, "as_orm")

        return typing.get_type_hints(func)["return"].model_validate(self)


class PublicEntityMixin(AsORMMixin, AsTASIMixin, FromTASIMixin): ...


class Classifications(PublicEntityMixin, ClassificationsBase):

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


class Velocity(PublicEntityMixin, VelocityBase):
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


class Acceleration(PublicEntityMixin, AccelerationBase):
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


class Dimension(PublicEntityMixin, DimensionBase):
    """The dimension of a traffic participant"""

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


class Position(PublicEntityMixin, PositionBase):

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


class BoundingBox(PublicEntityMixin, BoundingBoxBase):

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
