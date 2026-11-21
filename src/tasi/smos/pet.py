from datetime import datetime
from typing import Tuple

from tasi import Trajectory
from tasi.io import Position

from .base import SMOS
from .geometry import conflict_point


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

        result = conflict_point(
            ego, challenger, position=position, return_first=return_first
        )

        if result is None:
            raise RuntimeError(
                "Failed to find an intersection point between the ego's and "
                "challenger's trajectories"
            )

        point, ego_idx, challenger_idx = result

        return cls(
            value=(
                ego.timestamps[ego_idx] - challenger.timestamps[challenger_idx]
            ).total_seconds(),
            ego=ego.timestamps[ego_idx],
            challenger=challenger.timestamps[challenger_idx],
            point=Position(easting=point[0], northing=point[1]),
        )
