from tasi.utils import has_extra

GEO_EXTRA = has_extra("geo")

if not GEO_EXTRA:
    raise ImportError(
        "geopandas is not avaliable but required for this module. Please install tasi[geo] to get access to it."
    )

from functools import partial
from typing import List, Tuple, Union

import geopandas as gpd
import pandas as pd

from tasi.utils import add_attributes, position_to_linestring

from .base import TrajectoryBase

__all__ = ["GeoTrajectory"]

from .base import Trajectory


class GeoTrajectory(TrajectoryBase, gpd.GeoDataFrame):  # type: ignore
    """Representation of a traffic participant's trajectory with geospatial encoded position"""

    @property
    def _constructor(self):
        return GeoTrajectory

    @property
    def _constructor_sliced(self):
        return pd.Series

    @classmethod
    def from_trajectory(
        cls,
        tj: Trajectory,
        position: Union[str, List[str | Tuple[str, ...]], Tuple[str, ...]] = "position",
        aggregate: bool = True,
    ):

        if aggregate:

            if not isinstance(position, list):
                position = [position]
            index = [i[-1] if isinstance(i, tuple) else i for i in position]

            # convert all positions to points
            positions = (
                gpd.GeoSeries(
                    list(map(partial(position_to_linestring, tj), position)),
                    index=index,
                )
                .to_frame()
                .T
            )
            positions.index = pd.Index([tj.id], name="id")

            metadata = pd.DataFrame(
                {
                    ("dimension", "width"): [tj.dimension.width.mean()],
                    ("dimension", "length"): [tj.dimension.length.mean()],
                    ("dimension", "height"): [tj.dimension.height.mean()],
                    ("existance", "start"): [tj.timestamps[0]],
                    ("existance", "end"): [tj.timestamps[-1]],
                    ("classification", ""): [tj.most_likely_class],
                },
                index=positions.index,
            )

            return GeoTrajectory(add_attributes(metadata, positions))
        else:

            return GeoTrajectory(
                pd.concat(
                    [
                        tj.iloc[idx].as_geopose(position=position)
                        for idx in range(len(tj))
                    ]
                )
            )
