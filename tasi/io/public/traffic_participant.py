from typing import Self

from pandas.core.api import DataFrame as DataFrame

import tasi
from tasi.base import TASIBase
from tasi.io.base.traffic_participant import TrafficParticipantBase
from tasi.io.orm.base import ClassificationsORM, DimensionORM
from tasi.io.orm.traffic_participant import TrafficParticipantORM
from tasi.io.public.base import Classifications, Dimension, PublicEntityMixin

__all__ = ["TrafficParticipant"]


class TrafficParticipant(PublicEntityMixin, TrafficParticipantBase):

    #: The traffic participants dimension
    dimension: Dimension | None = None

    #: The traffic participants object type likelihoods
    classifications: Classifications | None = None

    def as_orm(self, **kwargs) -> TrafficParticipantORM:

        return TrafficParticipantORM(
            dimension=DimensionORM.model_validate(self.dimension),
            classifications=ClassificationsORM.model_validate(self.classifications),
            start_time=self.start_time,
            end_time=self.end_time,
            id_object=self.id_object,
        )

    @classmethod
    def from_tasi(cls, obj: tasi.Pose | tasi.Trajectory, **kwargs) -> Self:

        if isinstance(obj, tasi.Trajectory):

            classifications = Classifications.from_tasi(obj.iloc[0])
            dimension = Dimension.from_tasi(obj.iloc[0])

            # and the start and end time
            tp = cls(
                id_object=obj.id.item(),
                classifications=classifications,
                dimension=dimension,
                start_time=obj.interval.left.to_pydatetime(),
                end_time=obj.interval.right.to_pydatetime(),
            )

        elif isinstance(obj, tasi.Pose):
            tp = cls(id_object=obj.id.item())
        else:
            raise TypeError(f"Unsupported TASI entity {type(obj)}.")
        return tp

    def as_tasi(self, **kwargs) -> DataFrame | TASIBase:
        return self.as_dataframe()
