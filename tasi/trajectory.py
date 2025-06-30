from functools import partial
from typing import List, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd

from tasi.utils import add_attributes, position_to_linestring

from .base import PoseCollectionBase

__all__ = ["Trajectory", "GeoTrajectory"]

GeoTrajectory = gpd.GeoDataFrame


class TrajectoryBase(PoseCollectionBase):

    @property
    def id(self) -> np.int64:
        """Returns the id in the pose

        Returns:
            np.int64: The id
        """
        return self.ids[0]

    @property
    def most_likely_class(self) -> Union[int, str]:
        return self["classifications"].mean().idxmax()[0]


class Trajectory(TrajectoryBase):
    """Representation of a traffic participant's trajectory"""

    @property
    def _constructor(self):
        return Trajectory

    @property
    def _pose_constructor(self):
        from .pose import Pose

        return Pose

    @property
    def _trajectory_constructor(self):
        return self._constructor

    def _ensure_correct_type(self, df, key):
        df = super()._ensure_correct_type(df, key)

        if key is not None:
            if (
                isinstance(df, pd.DataFrame)
                and not isinstance(df, self._pose_constructor)
                and len(df) == 1
            ):
                # this is just a simple series
                return df.iloc[0]
        return df

    def as_geopandas(
        self,
        position: Union[str, List[str], Tuple[str]] = "position",
        aggregate: bool = True,
    ):
        """
        Convert the trajectory to a geometric representation

        Args:
            position (Union[str, List[str], Tuple[str]], optional): Objects' reference(s) to be converted into a
            geoDataFrame
            aggregate: (bool): If the positions should be aggregated to LineString objects

        Returns:
            tasi.trajectory.GeoTrajectory: The positions as GeoDataFrame

        """

        if aggregate:

            if not isinstance(position, list):
                position = [position]
            index = [i[-1] if isinstance(i, tuple) else i for i in position]

            # convert all positions to points
            positions = (
                gpd.GeoSeries(
                    list(map(partial(position_to_linestring, self), position)),
                    index=index,
                )
                .to_frame()
                .T
            )
            positions.index = pd.Index([self.id], name="id")

            metadata = pd.DataFrame(
                {
                    ("dimension", "width"): [self.dimension.width.mean()],
                    ("dimension", "length"): [self.dimension.length.mean()],
                    ("dimension", "height"): [self.dimension.height.mean()],
                    ("existance", "start"): [self.timestamps[0]],
                    ("existance", "end"): [self.timestamps[-1]],
                    ("classification", ""): [self.most_likely_class],
                },
                index=positions.index,
            )

            return GeoTrajectory(add_attributes(metadata, positions))
        else:

            return GeoTrajectory(
                pd.concat(
                    [
                        self.iloc[idx].as_geopose(position=position)
                        for idx in range(len(self))
                    ]
                )
            )


class GeoTrajectory(TrajectoryBase, gpd.GeoDataFrame):
    """Representation of a traffic participant's trajectory with geospatial encoded position"""

    @property
    def _constructor(self):
        return GeoTrajectory

    @property
    def _constructor_sliced(self):
        return pd.Series
