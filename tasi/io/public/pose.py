import json
from typing import Any, Dict, Self, Sequence, Union, overload

import pandas as pd
from geojson_pydantic import Point
from shapely import Point as ShapelyPoint
from shapely import to_geojson

import tasi
from tasi.io.base.pose import PoseBase
from tasi.io.orm.pose import GeoPoseORM, PoseORM
from tasi.io.orm.traffic_participant import TrafficParticipantORM
from tasi.io.public.base import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    Position,
    PublicEntityMixin,
    Velocity,
)
from tasi.io.public.traffic_participant import TrafficParticipant
from tasi.io.util import as_geojson

__all__ = ["PosePublic", "GeoPosePublic"]


class PublicPoseBase(PoseBase):

    #: The dimension of the traffic participant measurement for the pose's time
    dimension: Dimension

    #: A reference to the traffic participant this pose belongs to
    traffic_participant: TrafficParticipant

    #: The traffic participant's velocity
    velocity: Velocity

    #: The traffic participant's acceleration
    acceleration: Acceleration

    #: The traffic participant's boundingbox
    boundingbox: BoundingBox

    #: The traffic participant's object type probabilities
    classifications: Classifications


class PosePublic(PublicEntityMixin, PublicPoseBase):

    #: The traffic participant's position
    position: Position

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Pose, **kwargs) -> Self: ...

    @overload
    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Sequence[Self]: ...

    @classmethod
    def from_tasi(
        cls, obj: tasi.Pose | tasi.Trajectory, tp: TrafficParticipant, **kwargs
    ) -> Self | Sequence[Self]:

        def as_pose(o: tasi.Pose) -> Self:

            if "position" in o:
                position = Position.from_tasi(o)
            else:
                raise ValueError("Need a *position* attribute")

            return cls(
                timestamp=o.timestamp.to_pydatetime(),
                position=position,
                orientation=o.heading.item(),
                traffic_participant=TrafficParticipant.model_validate(tp),
                dimension=Dimension.from_tasi(o),
                velocity=Velocity.from_tasi(o),
                acceleration=Acceleration.from_tasi(o),
                classifications=Classifications.from_tasi(o),
                boundingbox=BoundingBox.from_tasi(o),
            )

        if isinstance(obj, tasi.Pose):
            return as_pose(obj)
        elif isinstance(obj, tasi.Trajectory):
            return [as_pose(obj.iloc[idx]) for idx in range(len(obj))]
        else:
            raise TypeError

    def as_tasi(self, **kwargs) -> tasi.Pose:

        p = tasi.Pose.from_attributes(
            timestamp=self.timestamp,
            index=self.traffic_participant.id_object,
            position=self.position.as_tasi(),
            heading=pd.Series([self.orientation]),
            dimension=self.dimension.as_tasi(),
            velocity=self.velocity.as_tasi(),
            acceleration=self.acceleration.as_tasi(),
            classifications=self.classifications.as_tasi(),
            boundingbox=self.boundingbox.as_tasi(),
        )

        return p

    @overload
    @classmethod
    def from_orm(cls, obj: PoseORM) -> Self: ...

    @overload
    @classmethod
    def from_orm(cls, obj: Any, update: Dict[str, Any] | None = None) -> Self: ...

    @classmethod
    def from_orm(
        cls, obj: Union[PoseORM, Any], update: Dict[str, Any] | None = None
    ) -> Self:

        if isinstance(obj, PoseORM):
            return cls.model_validate(obj)
        else:
            return super().from_orm(obj, update=update)

    def as_orm(
        self, traffic_participant: TrafficParticipantORM | None = None, **kwargs
    ) -> PoseORM:

        return PoseORM(
            timestamp=self.timestamp,
            orientation=self.orientation,
            position=self.position.as_orm(),
            dimension=self.dimension.as_orm(),
            velocity=self.velocity.as_orm(),
            acceleration=self.acceleration.as_orm(),
            boundingbox=self.boundingbox.as_orm(),
            traffic_participant=(
                self.traffic_participant.as_orm()
                if traffic_participant is None
                else traffic_participant
            ),
            classifications=self.classifications.as_orm(),
        )

    def as_geo(self) -> "GeoPosePublic":
        return GeoPosePublic.from_pose(self)


class GeoPosePublic(PublicEntityMixin, PublicPoseBase):

    #: The traffic participant's position represent as *GeoObject*
    position: Point

    @overload
    @classmethod
    def from_orm(cls, obj: GeoPoseORM) -> Self: ...

    @overload
    @classmethod
    def from_orm(cls, obj: PoseORM) -> Self: ...

    @classmethod
    def from_orm(
        cls, obj: Union[GeoPoseORM, Any], update: Dict[str, Any] | None = None
    ) -> Self:

        if isinstance(obj, GeoPoseORM):

            p2 = obj.model_copy()  # type: ignore
            p2.position = Point(**json.loads(as_geojson(obj.position)))  # type: ignore

            return cls.model_validate(p2)
        else:
            return super().from_orm(obj, update=update)

    @classmethod
    def from_pose(cls, pose: PosePublic):

        attr = pose.model_dump()

        attr["position"] = Point(
            **json.loads(
                to_geojson(
                    ShapelyPoint([pose.position.easting, pose.position.northing])
                )
            )
        )

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

    def as_orm(
        self, traffic_participant: TrafficParticipantORM | None = None, **kwargs
    ) -> GeoPoseORM:

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

    def as_tasi(self, **kwargs) -> tasi.GeoPose:
        return self.as_pose().as_tasi().as_geopandas()


MODELS = [PosePublic, GeoPosePublic]
