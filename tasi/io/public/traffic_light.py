from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Literal, Self, overload

import pandas as pd
from pandas.core.api import DataFrame as DataFrame

from tasi.io.base.traffic_light import Base, TrafficLightBase, TrafficLightStateBase
from tasi.io.public.base import PublicEntityMixin
from tasi.io.util import as_nested_dict
from tasi.pose import TrafficLightPose

__all__ = ["TrafficLightState", "TrafficLight", "TrafficLightCollection"]


class TrafficLightState(TrafficLightStateBase, PublicEntityMixin):

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> pd.DataFrame:
        """Convert to a ``TASI`` internal representation

        Returns:
            pd.DataFrame | TASIBase: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        if as_record:
            default_kwargs = dict(prefix="state", nlevels=2)
            default_kwargs.update(kwargs)

            return self.as_flat_dict(**default_kwargs)  # type: ignore

        return self.as_dataframe()


class TrafficLight(TrafficLightBase, PublicEntityMixin):

    #: The state of the traffic light
    state: TrafficLightState

    #: A unique identifier of the traffic light
    index: int

    @overload
    def as_tasi(self, as_record: Literal[True], **kwargs) -> Dict:
        """Convert to a ``TASI`` internal representation

        Returns:
            Dict: A flat dictionary that can be used with `pd.DataFrame.from_dict`
        """
        ...

    @overload
    def as_tasi(self, as_record: Literal[False], **kwargs) -> TrafficLightPose:
        """Convert to a ``TASI`` internal representation

        Returns:
            TrafficLightDataset: The internal representation format
        """
        ...

    def as_tasi(self, as_record: bool = True, **kwargs) -> TrafficLightPose | Dict:
        """Convert to a ``TASI`` internal representation.

        Returns:
            TrafficLightPose | Dict: Either a `TrafficLightPose` or a
            nested dictionary
        """
        record = defaultdict(dict)

        attr = self.state.as_tasi(as_record=True)

        idx = (self.timestamp, self.index)

        for key, value in attr.items():
            record[key] = {idx: value}

        record[("flashing", "")] = {idx: self.flashing}

        if as_record:
            return record

        ds = TrafficLightPose.from_dict(record)
        ds.index.names = TrafficLightPose.INDEX_COLUMNS

        return ds

    @classmethod
    def from_tasi(cls, obj: TrafficLightPose, **kwargs) -> Self:  # type: ignore

        return cls.model_validate(
            as_nested_dict(obj.reset_index().iloc[0], {"id": "index"})
        )


class TrafficLightCollection(PublicEntityMixin, Base):

    #: The time of the poses
    timestamp: datetime

    # the poses at the given time
    traffic_lights: List[TrafficLight]

    def as_orm(self, **kwargs) -> Any:
        raise NotImplementedError(
            "There is currently no direct representation in internal TASI format."
        )

    def as_tasi(self, as_record: bool = False, **kwargs) -> pd.DataFrame | Dict:
        raise NotImplementedError(
            "There is currently no direct representation in internal TASI format."
        )
