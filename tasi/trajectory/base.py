from typing import List, Tuple, Union

import numpy as np
import pandas as pd

from tasi.utils import requires_extra

from ..base import PoseCollectionBase


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
        from ..pose.base import Pose

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

    @requires_extra("geo")
    def as_geo(
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
            tasi.GeoTrajectory: The positions as GeoDataFrame

        """
        from .geo import GeoTrajectory

        return GeoTrajectory.from_trajectory(
            tj=self, position=position, aggregate=aggregate
        )
