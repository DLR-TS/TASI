import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS


class TTC(TimeSeriesSMOS):
    """Time-to-Collision (TTC).

    Definition (Hayward, J.C. (1972), "Near miss determination through use
    of a scale of danger," Highway Research Record, 384, 24-34): the time
    remaining until a following vehicle's front bumper reaches a leading
    vehicle's rear bumper, if both continue at their current instantaneous
    velocity.

    This implementation assumes a car-following (longitudinal, same
    direction of travel) conflict geometry between `ego` (the follower) and
    `challenger` (the leader), both moving along the easting axis:

    - `gap(t) = (challenger.position.easting(t) - ego.position.easting(t))
      - (challenger.dimension.length + ego.dimension.length) / 2`, i.e. the
      bumper-to-bumper distance rather than the center-to-center distance.
    - `speed(t)` is each trajectory's `velocity.easting` component.
    - `closing_speed(t) = ego.speed(t) - challenger.speed(t)`.
    - `TTC(t) = gap(t) / closing_speed(t)` where `closing_speed(t) > 0`
      (the follower is closing in on the leader); `NaN` otherwise, since a
      non-closing pair is not on a collision course and TTC is undefined.

    Projecting onto a single travel axis (easting) is only valid for
    straight, same-direction car-following interactions such as the
    synthetic `car_following_trajectories` fixture. Generalizing to
    multi-lane or curved paths requires projecting the relative
    position/velocity onto each participant's actual direction of travel,
    which is out of scope for this implementation.
    """

    @classmethod
    def estimate(cls, ego: Trajectory, challenger: Trajectory) -> "TTC":
        """Estimate the TTC time series between `ego` and `challenger`.

        Args:
            ego (Trajectory): The following participant's trajectory.
            challenger (Trajectory): The leading participant's trajectory.

        Returns:
            TTC: The TTC value at every shared timestamp.

        Raises:
            ValueError: If `ego` and `challenger` do not share the same
                timestamps.
        """
        if not np.array_equal(ego.timestamps.values, challenger.timestamps.values):
            raise ValueError(
                "'ego' and 'challenger' must share the same timestamps to "
                "estimate TTC"
            )

        # `ego` and `challenger` carry different `id`s on their index, so a
        # pandas-aligned subtraction of the two Series would align on
        # (timestamp, id) and produce an all-NaN result; convert to numpy
        # first to subtract element-wise by position instead.
        gap = (
            challenger.position.easting.to_numpy() - ego.position.easting.to_numpy()
        ) - (
            challenger.dimension.length.to_numpy() + ego.dimension.length.to_numpy()
        ) / 2

        closing_speed = (
            ego.velocity.easting.to_numpy() - challenger.velocity.easting.to_numpy()
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            ttc = np.where(closing_speed > 0, gap / closing_speed, np.nan)

        return cls(timestamps=list(ego.timestamps), values=ttc.tolist())
