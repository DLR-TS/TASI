import json
from datetime import datetime
from typing import Any, Dict, List, Literal, Self, Union, overload

import pandas as pd
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from geojson_pydantic import Point
from pydantic import field_validator
from shapely import Point as ShapelyPoint
from shapely import to_geojson

import tasi
from tasi.base import TASIBase
from tasi.io.orm import PoseORM, PositionORM, TrafficParticipantORM
from tasi.io.orm.pose.geo import GeoPoseORM

from .base import BaseModel, PosePublic, Position, PublicEntityMixin
from .core import GeoPoseBase

__all__ = [
    "as_geojson",
    "GeoPosePublic",
    "GeoPoseCollectionPublic",
]


def as_geojson(obj: WKBElement | str) -> str:

    if isinstance(obj, WKBElement):
        # e.g. session.get results in a `WKBElement`
        result = to_geojson(to_shape(obj))  # type: ignore
    else:
        raise TypeError(f"Unsupported type {type(obj)}")

    return result


class GeoPosePublic(GeoPoseBase):

    #: The traffic participant's position represent as *GeoObject*
    position: Point

    @field_validator("position", mode="before")
    def position_validator(
        cls,
        value: Union[Point, WKBElement],
    ):
        if isinstance(value, WKBElement):
            return Point(**json.loads(as_geojson(value)))
        elif isinstance(value, (Position, PositionORM)):
            return Point.create(coordinates=[value.easting, value.northing])

        return value

    @classmethod
    def from_pose(cls, pose: PosePublic, position: str = "position"):

        attr = pose.model_dump()

        if not isinstance(position, str):
            attr["position"] = reduce(lambda a, b: getattr(a, b), position, pose)
        else:
            attr["position"] = getattr(pose, position)

        return cls.model_validate(attr)

    def as_pose(self) -> PosePublic:
        """Convert to a :class:`Pose`

        Returns:
            Pose: The converted pose
        """
        attr = self.model_copy()

        # overwrite position
        attr.position = Position.from_wkt(attr.position.akt)  # type: ignore

        return PosePublic.model_validate(attr)

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> tasi.GeoPose:
        """Convert to a ``TASI`` internal representation

        Returns:
            tasi.Pose: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> Union[Dict, tasi.GeoPose]:

        pose = self.as_pose().as_tasi(as_record=as_record)

        if isinstance(pose, Dict):
            return pose
        else:
            return pose.as_geo()

    @overload
    @classmethod
    def from_orm(cls, obj: GeoPoseORM) -> Self: ...

    @overload
    @classmethod
    def from_orm(cls, obj: PoseORM) -> Self: ...

    @classmethod
    def from_orm(cls, obj: Union[GeoPoseORM, Any]) -> Self:

        if isinstance(obj, GeoPoseORM):

            return cls.model_validate(obj)

            obj.position = Point(**json.loads(as_geojson(obj.position)))  # type: ignore

            return cls.model_validate(
                dict(position=Point(**json.loads(as_geojson(obj.position))))
            )
        else:
            return super().model_validate(obj)

    def as_orm(
        self, traffic_participant: TrafficParticipantORM | None = None, **kwargs
    ):
        from ...orm.pose.geo import GeoPoseORM

        return GeoPoseORM(
            timestamp=self.timestamp,
            orientation=self.orientation,
            traffic_participant=(
                self.traffic_participant.as_orm()
                if traffic_participant is None
                else traffic_participant
            ),
            dimension=self.dimension.as_orm(),
            classifications=self.classifications.as_orm(),
            position=self.position.wkt,
            velocity=self.velocity.as_orm(),
            acceleration=self.acceleration.as_orm(),
            boundingbox=self.boundingbox.as_orm(),
        )


class GeoPoseCollectionPublic(BaseModel, PublicEntityMixin):

    #: The time of the poses
    timestamp: datetime

    # the geo-poses at the given time
    poses: List[PosePublic]

    def as_orm(self, **kwargs) -> Any:
        raise NotImplementedError(
            "There is currently no direct representation in the internal TASI format."
        )

    def as_tasi(
        self, as_record: bool = False, **kwargs
    ) -> pd.DataFrame | TASIBase | Dict:
        raise NotImplementedError(
            "There is currently no direct representation in the internal TASI format."
        )
