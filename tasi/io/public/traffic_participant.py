from datetime import datetime
from typing import Self

from pandas.core.api import DataFrame as DataFrame

import tasi
from tasi.base import TASIBase
from tasi.io.orm import ClassificationsORM, DimensionORM, TrafficParticipantORM

from .base import BaseModel, Classifications, Dimension, PublicEntityMixin

__all__ = ["TrafficParticipant"]


class TrafficParticipant(BaseModel, PublicEntityMixin):

    #: The traffic participants dimension
    dimension: Dimension

    #: The traffic participants object type likelihoods
    classifications: Classifications

    #: The first time the traffic participant was within the measurement site
    start_time: datetime | None = None

    #: The last time the traffic participant was within the measurement site
    end_time: datetime | None = None

    #: A unique identifier
    id_object: int

    def as_orm(self, **kwargs) -> TrafficParticipantORM:

        return TrafficParticipantORM(
            dimension=DimensionORM(**self.dimension.model_dump()),
            classifications=ClassificationsORM(**self.classifications.model_dump()),
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

            tp = cls(
                id_object=obj.id.item(),
                classifications=Classifications.from_tasi(obj),
                dimension=Dimension.from_tasi(obj),
            )
        else:
            raise TypeError(f"Unsupported TASI entity {type(obj)}.")
        return tp

    def as_tasi(self, **kwargs) -> DataFrame | TASIBase:
        return self.as_dataframe()
