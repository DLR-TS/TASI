from tasi.utils import has_extra

GEO_EXTRA = has_extra("geo")

if not GEO_EXTRA:
    raise ImportError(
        "geopandas is not avaliable but required for this module. Please install tasi[geo] to get access to it."
    )

from typing import List, Tuple, Union

import geopandas as gpd
import pandas as pd

from .base import Pose, PoseBase

__all__ = ["GeoPose"]


class GeoPose(PoseBase, gpd.GeoDataFrame):  # type: ignore
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
        return pose.as_geo(position=position)
