from datetime import datetime
from typing import Tuple, Union

import numpy as np

from tasi import Trajectory
from tasi.io import Position
from tasi.trajectory.geo import GeoTrajectory
from tasi.utils.geo import BasicGeometry, MultiGeometry, geometry_to_coords

from .base import SMOS


class PET(SMOS):

    #: The time the ego participant is at the intersection point
    ego: datetime

    #: The time the challenger participant is at the intersection point
    challenger: datetime

    #: The intersection point between the ego's and challenger's trajectory
    point: Position

    @classmethod
    def estimate(
        cls,
        ego: Trajectory,
        challenger: Trajectory,
        position: Tuple[Tuple[str, ...] | str, Tuple[str, ...] | str] = (
            "position",
            "position",
        ),
        return_first: bool = True,
    ):

        # get the reference positions
        ego_reference, challenger_reference = position

        # we use their geometric representation, while representing the trajectory with a LineString
        tj1: GeoTrajectory = ego.as_geo(aggregate=True, position=ego_reference)
        tj2: GeoTrajectory = challenger.as_geo(
            aggregate=True, position=challenger_reference
        )

        if not isinstance(ego_reference, str):
            # we a sequence of str. The last element will be the column name
            ego_ref = ego_reference[-1]
        else:
            ego_ref = ego_reference

        if not isinstance(challenger_reference, str):
            # we a sequence of str. The last element will be the column name
            challenger_ref = challenger_reference[-1]
        else:
            challenger_ref = challenger_reference

        # we use shapely to find the intersection points of both linestrings
        intersections: Union[BasicGeometry, MultiGeometry] = (
            tj1[ego_ref].intersection(tj2[challenger_ref], align=False).item()
        )

        # estimate the intersection point - note that the first intersection point
        # is used
        point = geometry_to_coords(intersections, return_first=return_first)

        # find the closest point for both traffic participants
        if point is None:
            raise RuntimeError(
                f"Failed to convert intersection {point} between trajectories into propery geometry"
            )

        # get the index of the position which is clostest to the current trajectory
        ego_idx = np.nanargmin(
            np.linalg.norm(point - ego[ego_reference].values, axis=1)
        )

        # get the index of the intersection point which is closest to other trajectory
        challenger_idx = np.nanargmin(
            np.linalg.norm(point - challenger[challenger_reference].values, axis=1)
        )

        return cls(
            value=(
                ego.timestamps[ego_idx] - challenger.timestamps[challenger_idx]
            ).total_seconds(),
            ego=ego.timestamps[ego_idx],
            challenger=challenger.timestamps[challenger_idx],
            point=Position(easting=point[0], northing=point[1]),
        )
