from typing import Any, Dict, Optional, Self, Union, overload

import pandas as pd

import tasi
from tasi.io.base import Base
from tasi.io.public.base import PublicEntityMixin
from tasi.io.public.pose.base import PosePublic
from tasi.io.public.traffic_participant import TrafficParticipant

__all__ = ["TrajectoryPublic"]


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

    def as_orm(self, **kwargs):

        from tasi.io.orm.trajectory import TrajectoryORM

        tp = self.traffic_participant.as_orm()

        return TrajectoryORM(
            poses=list(map(lambda p: p.as_orm(traffic_participant=tp), self.poses)),
            traffic_participant=tp,
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


try:
    from tasi.io.orm.trajectory import TrajectoryORM

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
            return super().from_orm(obj, update=update)

except ImportError:
    pass
