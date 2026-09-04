from typing import Optional, Tuple, Union

import numpy as np

from tasi import Trajectory
from tasi.trajectory.geo import GeoTrajectory
from tasi.utils.geo import BasicGeometry, MultiGeometry, geometry_to_coords

#: A reference to a (possibly nested) position attribute, e.g. `"position"`
#: or `("boundingbox", "center")`.
PositionReference = Union[Tuple[str, ...], str]


def conflict_point(
    ego: Trajectory,
    challenger: Trajectory,
    position: Tuple[PositionReference, PositionReference] = (
        "position",
        "position",
    ),
    return_first: bool = True,
) -> Optional[Tuple[np.ndarray, int, int]]:
    """Find the geometric conflict point between two trajectories' paths.

    The conflict point is where the `ego`'s and `challenger`'s reference
    paths intersect, found via their `LineString` representations. This is
    the shared geometry step behind :class:`PET` and any metric that needs
    "when/where do these two paths cross" (e.g. TAdv, TTC2D, ACT).

    Args:
        ego (Trajectory): The ego's trajectory.
        challenger (Trajectory): The challenger's trajectory.
        position (Tuple[PositionReference, PositionReference], optional):
            The reference position attribute(s) to use for `ego` and
            `challenger`, respectively. Defaults to `("position", "position")`.
        return_first (bool, optional): If multiple intersection points
            exist, use the first (`True`) or last (`False`) one along the
            paths. Defaults to `True`.

    Returns:
        Optional[Tuple[np.ndarray, int, int]]: A 3-tuple
        `(point, ego_idx, challenger_idx)` of the 2D intersection point
        (easting, northing) and the index into `ego`/`challenger` closest to
        it, or `None` if the two paths do not intersect.
    """
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
    # is used by default
    point = geometry_to_coords(intersections, return_first=return_first)

    if point is None:
        return None

    # The intersection point is always 2D (easting, northing), but the
    # reference attribute may carry additional sub-columns (e.g.
    # `altitude`, which `Position` defaults to 0). Restrict to the same two
    # columns used to build the LineStrings above, so the distance below is
    # computed in the same 2D space as `point`.
    ego_positions = ego[ego_reference][["easting", "northing"]].to_numpy()
    challenger_positions = challenger[challenger_reference][
        ["easting", "northing"]
    ].to_numpy()

    # get the index of the position which is closest to the current trajectory
    ego_idx = int(np.nanargmin(np.linalg.norm(point - ego_positions, axis=1)))

    # get the index of the intersection point which is closest to other trajectory
    challenger_idx = int(
        np.nanargmin(np.linalg.norm(point - challenger_positions, axis=1))
    )

    return point, ego_idx, challenger_idx
