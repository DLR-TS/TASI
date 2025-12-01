from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Literal, Self, Sequence, Union, overload

import pandas as pd

import tasi
from tasi.base import TASIBase
from tasi.io.orm import PoseORM, TrafficParticipantORM

from ..base import (
    Acceleration,
    BaseModel,
    BoundingBox,
    Classifications,
    Dimension,
    Position,
    PublicEntityMixin,
    Velocity,
)
from ..traffic_participant import TrafficParticipant
from .core import PoseBase

__all__ = [
    "PosePublic",
    "PoseCollectionPublic",
]

from tasi.io.util import FlatDict
from tasi.utils import requires_extra


class PosePublic(PublicEntityMixin, PoseBase):

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

    @overload
    def as_tasi(self, as_record: bool = False, **kwargs) -> tasi.Pose:
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

    @requires_extra("geo")
    def as_geo(self, position: str = "position"):
        from .geo import GeoPosePublic

        return GeoPosePublic.from_pose(self, position=position)


class PoseCollectionPublic(PublicEntityMixin, BaseModel):

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
