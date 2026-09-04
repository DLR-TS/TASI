import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS


class DRAC(TimeSeriesSMOS):
    """Deceleration Rate to Avoid Crash.

    DRAC(t) is the constant deceleration rate the following (`ego`) vehicle
    would need to apply, starting at `t`, to just avoid colliding with the
    leading (`challenger`) vehicle, assuming the challenger keeps its current
    speed.

    Definition (Cooper, P.J. (1984). "Experience with traffic conflicts in
    Canada with emphasis on 'post encroachment time' techniques." In
    International Calibration Study of Traffic Conflict Techniques, NATO ASI
    Series F5. Springer.)::

        DRAC(t) = closing_speed(t) ** 2 / (2 * gap(t))    if closing_speed(t) > 0
        DRAC(t) = NaN                                     otherwise

    where, following Cooper's original car-following (rear-end) setup:

    - `gap(t)` is the bumper-to-bumper distance between the vehicles::

          gap(t) = (challenger.position.easting(t) - ego.position.easting(t))
                   - (challenger.dimension.length + ego.dimension.length) / 2

    - `speed(t)` of a trajectory is its `velocity.easting` component. This
      assumes both trajectories travel (approximately) along the easting
      axis, as in a straight car-following segment; projecting speed onto a
      general direction of travel for curved paths / multi-lane geometries
      is out of scope here.

    - `closing_speed(t) = ego.speed(t) - challenger.speed(t)`. DRAC is only
      defined while the ego is actually closing in (`closing_speed(t) > 0`);
      otherwise there is no impending collision to avoid and the value is
      `NaN`.

    `ego` is assumed to be the following vehicle, `challenger` the leading
    vehicle.
    """

    @classmethod
    def estimate(cls, ego: Trajectory, challenger: Trajectory) -> "DRAC":

        if not ego.timestamps.equals(challenger.timestamps):
            raise ValueError(
                "'ego' and 'challenger' must share identical timestamps"
            )

        # Convert to numpy *before* combining ego/challenger: their `id` differs,
        # so pandas would otherwise align (challenger.position - ego.position) by
        # the full (timestamp, id) index and produce a union instead of an
        # elementwise, per-timestep difference.
        gap = (
            challenger.position.easting.to_numpy() - ego.position.easting.to_numpy()
        ) - (
            challenger.dimension.length.to_numpy() + ego.dimension.length.to_numpy()
        ) / 2

        closing_speed = (
            ego.velocity.easting.to_numpy() - challenger.velocity.easting.to_numpy()
        )

        drac = np.where(
            closing_speed > 0,
            closing_speed**2 / (2 * gap),
            np.nan,
        )

        return cls(
            timestamps=list(ego.timestamps.to_pydatetime()),
            values=drac.tolist(),
        )
