from tasi.utils import has_extra

GEO_EXTRA = has_extra("geo")

if not GEO_EXTRA:
    raise ImportError(
        "geopandas is not avaliable but required for this module. Please install tasi[geo] to get access to it."
    )

from typing import List

import geopandas as gpd
import pandas as pd
from typing_extensions import Self

from ..trajectory import GeoTrajectory
from ..utils import requires_extra
from .base import Dataset, PoseCollectionBase

__all__ = [
    "GeoTrajectoryDataset",
]


class GeoPoseCollectionBase(PoseCollectionBase, gpd.GeoDataFrame):  # type: ignore
    pass


class GeoTrajectoryDataset(Dataset, GeoPoseCollectionBase):  # type: ignore
    """Representation of a dataset of trajectory information using ``GeoPandas``"""

    @classmethod
    def from_trajectories(cls, tjs: List[GeoTrajectory]) -> Self:
        """Create a dataset based on trajectories

        Args:
            tjs (List[GeoTrajectory]): The trajectories

        Returns:
            GeoTrajectoryDataset: A dataset with the given trajectories
        """
        return cls(pd.concat(tjs, axis=0))

    @requires_extra("visualization")
    def explore(self, crs: str = "EPSG:32632", *args, **kwargs):

        if self.crs is None:
            self = self.set_crs(crs)

        # a quick hack for now since we dont want to update the orignal columns
        self = gpd.GeoDataFrame(self)

        # we need to flatten index for visualization purpose
        self.columns = [
            "_".join(l) if l[1] else l[0] for l in self.columns.to_flat_index()
        ]

        return self.explore(*args, **kwargs)
