from typing import Any, Dict, Optional, Self, Union, overload

import pandas as pd

import tasi

from ...orm.trajectory.base import TrajectoryORM
from ..base import PublicEntityMixin
from ..pose.base import PosePublic
from ..traffic_participant import TrafficParticipant
from .core import TrajectoryBase

__all__ = ["TrajectoryPublic"]


class TrajectoryPublic(TrajectoryBase, PublicEntityMixin):

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

    def as_geo(self):
        """Convert to its GeoObject-based representation

        Returns:
            GeoTrajectory: The same trajectory but with GeoObjects
        """
        from tasi.io.public.trajectory.geo import GeoTrajectoryPublic

        return GeoTrajectoryPublic.from_trajectory(self)

    @classmethod
    def from_tasi(cls, obj: tasi.Trajectory, **kwargs) -> Self:

        tp = TrafficParticipant.from_tasi(obj)

        return cls(
            poses=[
                PosePublic.from_tasi(obj.iloc[idx], tp=tp) for idx in range(len(obj))
            ],
            traffic_participant=tp,
        )

    def as_orm(self, **kwargs):

        from tasi.io.orm.trajectory.base import TrajectoryORM

        tp = self.traffic_participant.as_orm()

        return TrajectoryORM(
            poses=list(map(lambda p: p.as_orm(traffic_participant=tp), self.poses)),
            traffic_participant=tp,
        )

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

        else:
            return super().model_validate(obj)
