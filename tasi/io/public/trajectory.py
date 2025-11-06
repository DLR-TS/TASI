import json
from typing import Any, Dict, Optional, Self, Union, overload

import pandas as pd
from geojson_pydantic import LineString
from shapely import LineString as ShapelyLineString
from shapely import to_geojson, wkt

import tasi
from tasi.io.base import Base
from tasi.io.orm.trajectory import GeoTrajectoryORM, TrajectoryORM
from tasi.io.public.base import PublicEntityMixin
from tasi.io.public.pose import GeoPosePublic, PosePublic
from tasi.io.public.traffic_participant import TrafficParticipant

__all__ = ["TrajectoryPublic", "GeoTrajectoryPublic"]


class TrajectoryPublic(Base, PublicEntityMixin):

    #: A reference to the traffic participant
    traffic_participant: TrafficParticipant

    #: The poses of the trajectory
    poses: list[PosePublic]

    def as_tasi(self, as_record: bool = True, **kwargs) -> tasi.Trajectory:
        """Convert to a ``TASI`` internal representation

        Returns:
            tasi.Trajectory: The internal representation format
        """

        if as_record:
            record = self.poses[0].as_tasi(as_record=as_record)

            for p in self.poses[1:]:
                for k2, v2 in p.as_tasi(as_record=as_record).items():
                    record[k2].update(v2)

            tj = tasi.Trajectory.from_dict(record)
            tj.index.names = tasi.Trajectory.INDEX_COLUMNS

            return tj

        return tasi.Trajectory(
            pd.concat([p.as_tasi(as_record=as_record) for p in self.poses])
        )

    def as_orm(self, **kwargs) -> TrajectoryORM:

        tp = self.traffic_participant.as_orm()

        return TrajectoryORM(
            poses=list(map(lambda p: p.as_orm(traffic_participant=tp), self.poses)),
            traffic_participant=tp,
        )

    def as_geo(self) -> "GeoTrajectoryPublic":
        """Convert to its GeoObject-based representation

        Returns:
            GeoTrajectory: The same trajectory but with GeoObjects
        """
        return GeoTrajectoryPublic.from_trajectory(self)

    @overload
    @classmethod
    def from_orm(cls, obj: TrajectoryORM) -> Self: ...

    @overload
    @classmethod
    def from_orm(cls, obj: Any, update: Dict[str, Any] | None = None) -> Self: ...

    @classmethod
    def from_orm(
        cls,
        obj: Union[TrajectoryORM, Any],
        update: Optional[Dict[str, Any]] = None,
    ) -> Self:

        if isinstance(obj, TrajectoryORM):
            return cls.model_validate(obj)

            # attr = obj.model_dump()

            # poses = list(
            #     map(
            #         GeoPose.from_orm,
            #         sorted(obj.poses, key=lambda gp: gp.timestamp),
            #     )
            # )

            # attr["geometry"] = LineString(
            #     **json.loads(
            #         to_geojson(
            #             ShapelyLineString(
            #                 list(
            #                     map(
            #                         lambda p: p.position.wkt,
            #                         poses,
            #                     )
            #                 )  # type: ignore
            #             )
            #         )
            #     )
            # )

            # obj = cls.model_validate(attr)
            # obj.poses = poses

            # return obj

        else:
            return super().from_orm(obj, update=update)

    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Self:

        tp = TrafficParticipant.from_tasi(obj)

        return cls(
            poses=[
                PosePublic.from_tasi(obj.iloc[idx], tp=tp) for idx in range(len(obj))
            ],
            traffic_participant=tp,
        )


class GeoTrajectoryPublic(Base, PublicEntityMixin):

    #: A reference to the traffic participant
    traffic_participant: TrafficParticipant

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

            obj2 = obj.model_copy()  # type: ignore

            # convert obj poses to geoposes
            poses = list(
                map(
                    GeoPosePublic.from_orm,
                    sorted(obj.poses, key=lambda gp: gp.timestamp),
                )
            )  # type: ignore

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

            obj2.geometry = geometry  # type: ignore

            return cls.model_validate(
                dict(
                    geometry=geometry,
                    poses=poses,
                    traffic_participant=obj.traffic_participant,
                )
            )

        else:
            return super().from_orm(obj, update=update)

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
        return self.as_trajectory().as_tasi().as_geopandas(**kwargs)
