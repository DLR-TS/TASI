from typing import Tuple

import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS
from .geometry import conflict_point


class TAdv(TimeSeriesSMOS):
    """Time Advantage (TAdv).

    Definition (commonly attributed to Hansson, K.G. (1975), and used
    throughout the Swedish Traffic Conflict Technique tradition, e.g.
    Hydén, C. (1987), "The development of a method for traffic safety
    evaluation: The Swedish traffic conflict technique," Lund University
    doctoral thesis): TAdv is computed like PET, except *predictively* and
    *continuously* rather than from a single pair of actual arrival times.
    At every timestep `t`, assuming both participants keep their current
    position, speed and direction unchanged, TAdv(t) is the absolute
    difference between the time each of them would still need to reach
    the (static) conflict point:

        TAdv(t) = |d_ego(t) / v_ego(t) - d_challenger(t) / v_challenger(t)|

    where `d_ego(t)` / `d_challenger(t)` is each participant's straight-line
    distance from its position at `t` to the conflict point (found once via
    `conflict_point()`, the same helper `PET` uses - the conflict point
    itself doesn't move), and `v_ego(t)` / `v_challenger(t)` is each
    participant's instantaneous speed (the magnitude of its `velocity`
    vector, i.e. `sqrt(easting**2 + northing**2)` - unlike the Phase 1
    longitudinal metrics, this is not restricted to a single travel axis,
    since a geometric conflict point can be approached from any direction).

    `TAdv(t)` is `NaN` wherever a participant isn't moving (`v(t) == 0`),
    since "time to reach the point" is undefined for a stationary
    participant. Unlike PET, no vehicle-length correction is applied to the
    distance (mirroring PET's own precedent of using raw, uncorrected
    reference-point positions) - TAdv is measured to the exact conflict
    point, not to a bumper.

    Note on the citation: PLAN.md's task description points to "Hydén,
    1987" for TAdv, but the concept itself is more precisely attributed in
    the surrogate-safety-measure literature to Hansson (1975); Hydén's 1987
    Swedish Traffic Conflict Technique thesis is the context TAdv is
    commonly used and cited within, not TAdv's original source. Both are
    referenced above since the underlying primary source was not directly
    accessible to verify further.
    """

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
    ) -> "TAdv":
        """Estimate the TAdv time series between `ego` and `challenger`.

        Args:
            ego (Trajectory): One participant's trajectory.
            challenger (Trajectory): The other participant's trajectory.
            position: The reference position attribute(s) used to find the
                conflict point, forwarded to `conflict_point()`.
            return_first (bool, optional): If multiple intersection points
                exist, use the first (`True`) or last (`False`). Defaults
                to `True`.

        Returns:
            TAdv: The TAdv value at every shared timestamp.

        Raises:
            ValueError: If `ego` and `challenger` do not share the same
                timestamps.
            RuntimeError: If `ego`'s and `challenger`'s paths do not
                intersect (no conflict point exists).
        """
        if not ego.timestamps.equals(challenger.timestamps):
            raise ValueError(
                "'ego' and 'challenger' must share identical timestamps"
            )

        result = conflict_point(
            ego, challenger, position=position, return_first=return_first
        )

        if result is None:
            raise RuntimeError(
                "Failed to find an intersection point between the ego's and "
                "challenger's trajectories"
            )

        point, _, _ = result

        ego_reference, challenger_reference = position

        ego_positions = ego[ego_reference][["easting", "northing"]].to_numpy()
        challenger_positions = challenger[challenger_reference][
            ["easting", "northing"]
        ].to_numpy()

        d_ego = np.linalg.norm(point - ego_positions, axis=1)
        d_challenger = np.linalg.norm(point - challenger_positions, axis=1)

        v_ego = np.linalg.norm(
            ego.velocity[["easting", "northing"]].to_numpy(), axis=1
        )
        v_challenger = np.linalg.norm(
            challenger.velocity[["easting", "northing"]].to_numpy(), axis=1
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            t_ego = d_ego / v_ego
            t_challenger = d_challenger / v_challenger
            tadv = np.abs(t_ego - t_challenger)

        tadv = np.where((v_ego > 0) & (v_challenger > 0), tadv, np.nan)

        return cls(timestamps=list(ego.timestamps), values=tadv.tolist())
