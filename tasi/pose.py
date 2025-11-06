from datetime import datetime
from functools import partial
from typing import List, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd

from tasi.utils import add_attributes, position_to_point

from .base import CollectionBase

GeoPose = gpd.GeoDataFrame  # type: ignore

__all__ = ["Pose", "GeoPose", "PoseBase", "TrafficLightPose"]


class PoseBase(CollectionBase):

    @property
    def timestamp(self) -> pd.Timestamp:
        """Returns the datetime of the pose

        Returns:
            pd.Timestamp: The time
        """
        return self.timestamps[0]

    @property
    def id(self) -> np.int64:
        """Returns the id in the pose

        Returns:
            np.int64: The id
        """
        return self.ids[0]

    def _ensure_correct_type(self, df, key):
        return df


class Pose(PoseBase):
    """Representation of a traffic participant's pose"""

    @property
    def _constructor(self):
        return Pose

    @property
    def _constructor_sliced(self):
        return pd.Series

    @classmethod
    def from_attributes(
        cls,
        index: int,
        timestamp: datetime,
        position: pd.DataFrame,
        velocity: pd.DataFrame,
        acceleration: pd.DataFrame,
        heading: Union[pd.Series, pd.DataFrame],
        classifications: pd.DataFrame,
        yaw_rate: Union[pd.Series, pd.DataFrame] | None = None,
        dimension: pd.DataFrame | None = None,
        boundingbox: pd.DataFrame | None = None,
    ):
        attributes = {
            "position": position,
            "velocity": velocity,
            "acceleration": acceleration,
            "heading": heading,
            "classifications": classifications,
        }

        assert not (
            dimension is None and boundingbox is None
        ), "either dimension or boundingbox needs to be specified"

        if dimension is not None:
            attributes["dimension"] = dimension

        if (boundingbox is None or boundingbox.empty) and dimension is not None:
            from tasi.calculus import boundingbox_from_dimension

            boundingbox = boundingbox_from_dimension(
                dimension, heading, relative_to=position
            )

        attributes["boundingbox"] = boundingbox

        if yaw_rate is not None:
            attributes["yaw_rate"] = yaw_rate

        from tasi.utils import add_attributes

        df = add_attributes(
            *list(attributes.values()),
            keys=list(attributes.keys()),
        )
        df.index = pd.MultiIndex.from_arrays(
            [[timestamp], [index]],
            names=cls.INDEX_COLUMNS,
        )

        return cls(df)

    def as_geopandas(
        self,
        position: Union[str, List[str], Tuple[str]] = "position",
        active="position",
    ) -> GeoPose:
        """Convert the pose to a geometric representation


        Args:
            position (Union[str, List[str], Tuple[str]], optional): The position information to encode. Defaults to "position".
            active: (Optional[str]): The active geometry. Defaults to "position".

        Returns:
            GeoPose: Geospatial representation of the pose.
        """

        if not isinstance(position, list):
            position = [position]

        index = [i[-1] if isinstance(i, tuple) else i for i in position]

        # convert all positions to points
        positions = (
            gpd.GeoSeries(
                list(map(partial(position_to_point, self), position)),
                index=index,
            )
            .to_frame()
            .T
        )
        positions.index = self.index

        pose = GeoPose(add_attributes(self.drop(columns=position), positions))
        pose.set_geometry(active, inplace=True)

        return pose


class GeoPose(PoseBase, gpd.GeoDataFrame):
    """Representation of a traffic participant's pose with geospatial encoded position"""

    @property
    def _constructor(self):
        return GeoPose

    @property
    def _constructor_sliced(self):
        return pd.Series

    @classmethod
    def from_pose(
        cls, pose: Pose, position: Union[str, List[str], Tuple[str]] = "position"
    ):
        return pose.as_geopandas(position=position)


class TrafficLightPose(PoseBase):

    @property
    def _constructor(self):
        return TrafficLightPose

    @property
    def _constructor_sliced(self):
        return pd.Series
