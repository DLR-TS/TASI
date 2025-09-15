import json
from collections import defaultdict
from typing import Any, Dict, Literal, Self, Sequence, Union, overload, List

import pandas as pd
from geojson_pydantic import Point
from shapely import Point as ShapelyPoint
from shapely import to_geojson
from datetime import datetime

import tasi
from tasi.base import TASIBase
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
from tasi.io.base import Base
from tasi.io.public.traffic_participant import TrafficParticipant
from tasi.io.util import as_geojson

__all__ = [
    "PosePublic",
    "GeoPosePublic",
    "PoseCollectionPublic",
    "GeoPoseCollectionPublic",
]

from tasi.io.util import FlatDict


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

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> tasi.Pose:
        """Convert to a ``TASI`` internal representation

        Returns:
            tasi.Pose: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> tasi.Pose | Dict:

        if as_record:

            record = defaultdict(dict)

            attributes = [
                self.position.as_tasi(as_record=True),
                FlatDict.from_dict({"heading": self.orientation}, nlevels=3),
                self.dimension.as_tasi(as_record=True),
                self.velocity.as_tasi(as_record=True),
                self.acceleration.as_tasi(as_record=True),
                self.classifications.as_tasi(as_record=True),
                self.boundingbox.as_tasi(as_record=True),
            ]

            idx = idx = (self.timestamp, self.traffic_participant.id_object)

            for d in attributes:
                for key, value in d.items():
                    record[key] = {idx: value}

            return record
        else:
            return tasi.Pose.from_attributes(
                timestamp=self.timestamp,
                index=self.traffic_participant.id_object,
                position=self.position.as_tasi(as_record=False),
                heading=pd.Series([self.orientation]),
                dimension=self.dimension.as_tasi(as_record=False),
                velocity=self.velocity.as_tasi(as_record=False),
                acceleration=self.acceleration.as_tasi(as_record=False),
                classifications=self.classifications.as_tasi(as_record=False),
                boundingbox=self.boundingbox.as_tasi(as_record=False),
            )

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
        attr.position = Position.from_wkt(attr.position.wkt)  # type: ignore

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
            return pose.as_geopandas()


class PoseCollectionPublic(PublicEntityMixin, Base):

    #: The time of the poses
    timestamp: datetime

    # the poses at the given time
    poses: List[PosePublic]

    def as_orm(self, **kwargs) -> Any:
        raise NotImplementedError(
            "There is currently no direct representation in internal TASI format."
        )

    def as_tasi(
        self, as_record: bool = False, **kwargs
    ) -> pd.DataFrame | TASIBase | Dict:
        raise NotImplementedError(
            "There is currently no direct representation in internal TASI format."
        )


class GeoPoseCollectionPublic(PublicEntityMixin, Base):

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


MODELS = [PosePublic, GeoPosePublic]
