import json
from typing import Any, Dict, Optional, Self, Union, overload

from geojson_pydantic import LineString
from shapely import LineString as ShapelyLineString
from shapely import to_geojson, wkt

import tasi

from ...orm.trajectory.base import TrajectoryORM
from ...orm.trajectory.geo import GeoTrajectoryORM
from ..base import PublicEntityMixin
from ..pose.geo import GeoPosePublic
from .base import TrajectoryPublic
from .core import TrajectoryBase

__all__ = ["GeoTrajectoryPublic"]


class GeoTrajectoryPublic(TrajectoryBase, PublicEntityMixin):

    #: The poses of the trajectory
    poses: list["GeoPosePublic"] = []

    #: Representation of the trajectory using a *GeoObject*
    geometry: LineString

    @overload
    @classmethod
    def from_orm(cls, obj: GeoTrajectoryORM) -> Self: ...

    @overload
    @classmethod
    def from_orm(cls, obj: Any, update: Dict[str, Any] | None = None) -> Self: ...

    @classmethod
    def from_orm(
        cls,
        obj: Union[TrajectoryORM, GeoTrajectoryORM, Any],
        update: Optional[Dict[str, Any]] = None,
    ) -> Self:

        if isinstance(obj, GeoTrajectoryORM):

            # convert obj poses to geoposes
            poses = list(
                map(
                    GeoPosePublic.from_orm,
                    sorted(obj.poses, key=lambda gp: gp.timestamp),
                )
            )

            # get shapely coordinates of all points
            coordinates = list(
                map(
                    lambda p: wkt.loads(p.position.wkt),
                    poses,
                )
            )

            # build linestring of geoposes by shapely -> geojson -> geojson-pydantic
            geometry = LineString(
                **json.loads(to_geojson(ShapelyLineString(coordinates)))
            )

            return cls.model_validate(
                dict(
                    geometry=geometry,
                    poses=poses,
                    traffic_participant=obj.traffic_participant,
                )
            )

        else:
            return super().model_validate(obj)

    def as_orm(self, **kwargs) -> GeoTrajectoryORM:

        tp = self.traffic_participant.as_orm()

        return GeoTrajectoryORM(
            poses=list(map(lambda p: p.as_orm(traffic_participant=tp), self.poses)),
            traffic_participant=tp,
            geometry=self.geometry.wkt,
        )

    @classmethod
    def from_trajectory(cls, trajectory: TrajectoryPublic) -> Self:

        # convert trajectory poses to geoposes
        poses = list(
            map(
                lambda p: p.as_geo(),
                sorted(trajectory.poses, key=lambda gp: gp.timestamp),
            )
        )  # type: ignore

        coords = list(
            map(
                lambda p: wkt.loads(p.position.wkt),
                poses,
            )
        )

        # build linestring of geoposes
        geometry = LineString(**json.loads(to_geojson(ShapelyLineString(coords))))

        return cls.model_validate(
            dict(
                geometry=geometry,
                poses=poses,
                traffic_participant=trajectory.traffic_participant,
            )
        )

    def as_trajectory(self) -> TrajectoryPublic:

        # convert trajectory poses to geoposes
        poses = list(
            map(
                lambda p: p.as_pose(),
                sorted(self.poses, key=lambda gp: gp.timestamp),
            )
        )  # type: ignore

        return TrajectoryPublic.model_validate(
            dict(
                poses=poses,
                traffic_participant=self.traffic_participant,
            )
        )

    def as_tasi(self, **kwargs) -> tasi.GeoTrajectory:
        """Convert to a `GeoPandas` based representation

        Returns:
            tasi.GeoTrajectory: Representation based on `GeoPandas`
        """
        return self.as_trajectory().as_tasi().as_geo(**kwargs)


MODELS = [GeoTrajectoryPublic]
