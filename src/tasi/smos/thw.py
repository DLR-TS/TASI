import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS


class THW(TimeSeriesSMOS):
    """Time Headway (THW) between a following and a leading traffic participant.

    THW is a longitudinal car-following safety indicator: the time it would
    take the follower (`ego`), at its *current* speed, to reach the leader's
    (`challenger`'s) current rear position. Unlike :class:`~tasi.smos.ttc.TTC`,
    it is defined regardless of whether the follower is currently closing the
    gap, and does not depend on the leader's speed at all.

    Definition (standard time-headway / traffic-flow safety indicator, see
    e.g. Vogel, K. (2003), "A comparison of headway and time to collision as
    safety indicators," Accident Analysis & Prevention, 35(3), 427-433)::

        THW(t) = gap(t) / v_ego(t)

    where `gap(t)` is the net (bumper-to-bumper) longitudinal distance
    between the leader's rear and the follower's front, and `v_ego(t)` is the
    follower's speed along the direction of travel.

    Notes:
        Headway is sometimes defined "gross" (front-bumper-to-front-bumper,
        i.e. simply the centre-to-centre distance) rather than "net"
        (bumper-to-bumper). This implementation deliberately uses the *net*
        convention - subtracting both participants' half-length from the
        centre-to-centre distance - for consistency with the sibling `TTC`
        and `DRAC` metrics, which also use bumper-to-bumper gaps.

        `estimate(...)` currently assumes both trajectories move along the
        `easting` axis (i.e. a straight, single-lane car-following scenario)
        and uses `velocity.easting` as the speed and `position.easting` for
        the gap. Projecting onto an arbitrary direction of travel (curved
        roads, multi-lane scenarios) is out of scope for this first version.

        `THW(t)` is `NaN` wherever the follower's speed is not strictly
        positive (stopped or moving backwards), since headway is undefined
        in that case.
    """

    @classmethod
    def estimate(cls, ego: Trajectory, challenger: Trajectory) -> "THW":
        """Estimate the Time Headway (THW) between `ego` (follower) and
        `challenger` (leader).

        Args:
            ego (Trajectory): The following participant's trajectory.
            challenger (Trajectory): The leading participant's trajectory.

        Returns:
            THW: The Time Headway, one value per shared timestep.

        Raises:
            ValueError: If `ego` and `challenger` do not share identical
                timestamps.
        """
        if not np.array_equal(
            ego.timestamps.to_numpy(), challenger.timestamps.to_numpy()
        ):
            raise ValueError(
                "'ego' and 'challenger' must share identical timestamps to "
                "estimate THW"
            )

        # net (bumper-to-bumper) longitudinal gap between leader and follower
        gap = (
            challenger.position.easting.to_numpy() - ego.position.easting.to_numpy()
        ) - (
            challenger.dimension.length.to_numpy() + ego.dimension.length.to_numpy()
        ) / 2.0

        ego_speed = ego.velocity.easting.to_numpy()

        with np.errstate(divide="ignore", invalid="ignore"):
            values = np.where(ego_speed > 0, gap / ego_speed, np.nan)

        return cls(
            timestamps=list(ego.timestamps),
            values=[float(v) for v in values],
        )
