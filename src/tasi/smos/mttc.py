import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS


class MTTC(TimeSeriesSMOS):
    """Modified Time-to-Collision (MTTC) for a longitudinal car-following pair.

    `ego` is assumed to be the follower (behind) and `challenger` the leader
    (ahead), both moving along the same direction of travel. Unlike the
    classic TTC, which assumes constant velocity, MTTC additionally accounts
    for a constant relative acceleration between the two participants during
    the prediction interval.

    Definition (Ozbay, K., Yang, H., & Bartin, B. (2008). Derivation and
    validation of new simulation-based surrogate safety measure.
    Transportation Research Record, 2083(1), 105-113):

    Let, at time `t`::

        gap(t) = (challenger.easting(t) - ego.easting(t))
                 - (challenger.length + ego.length) / 2

        dv(t) = ego.speed(t) - challenger.speed(t)     # positive = closing
        da(t) = ego.accel(t) - challenger.accel(t)

    where `speed`/`accel` are the `easting` component of `velocity` /
    `acceleration` (this implementation is 1D, along the easting axis;
    projecting onto a general direction of travel for curved/multi-lane
    paths is out of scope here).

    Projecting the gap forward by `tau` seconds under constant relative
    acceleration:

        gap(t + tau) = gap(t) - dv(t) * tau - 0.5 * da(t) * tau ** 2

    `MTTC(t)` is the smallest non-negative real root `tau` of::

        0.5 * da(t) * tau ** 2 + dv(t) * tau - gap(t) = 0

    A root of `tau = 0` is valid and means the pair is already at (or past)
    the point of `gap == 0` at time `t`. When `da(t)` is zero this reduces
    to the classic constant-velocity TTC, `tau = gap(t) / dv(t)`. If no
    non-negative real root exists (negative discriminant, or all real roots
    negative), `MTTC(t)` is `NaN`.
    """

    @classmethod
    def estimate(cls, ego: Trajectory, challenger: Trajectory) -> "MTTC":

        if not ego.timestamps.equals(challenger.timestamps):
            raise ValueError(
                "'ego' and 'challenger' must share identical timestamps"
            )

        # NOTE: 'ego' and 'challenger' carry different 'id' values on their
        # MultiIndex, so a pandas-level subtraction between their Series
        # would align on the full (timestamp, id) index and silently yield
        # all-NaN. Convert each side to a plain numpy array first (they are
        # already validated to share the same timestamps, in the same
        # order) and only then combine ego and challenger arithmetically.
        ego_easting = ego.position.easting.to_numpy()
        challenger_easting = challenger.position.easting.to_numpy()
        ego_length = ego.dimension.length.to_numpy()
        challenger_length = challenger.dimension.length.to_numpy()
        ego_speed = ego.velocity.easting.to_numpy()
        challenger_speed = challenger.velocity.easting.to_numpy()
        ego_accel = ego.acceleration.easting.to_numpy()
        challenger_accel = challenger.acceleration.easting.to_numpy()

        gap = (challenger_easting - ego_easting) - (
            challenger_length + ego_length
        ) / 2

        dv = ego_speed - challenger_speed
        da = ego_accel - challenger_accel

        values = np.full(gap.shape, np.nan)

        # constant relative velocity (da == 0): classic TTC, tau = gap / dv
        constant_velocity = np.isclose(da, 0)

        with np.errstate(divide="ignore", invalid="ignore"):
            linear_tau = gap / dv

        linear_valid = constant_velocity & (dv > 0) & np.isfinite(linear_tau)
        values[linear_valid] = linear_tau[linear_valid]

        # constant relative acceleration (da != 0): solve the quadratic
        # 0.5 * da * tau**2 + dv * tau - gap = 0 for its smallest
        # non-negative real root.
        quadratic = ~constant_velocity

        a = 0.5 * da[quadratic]
        b = dv[quadratic]
        c = -gap[quadratic]

        discriminant = b**2 - 4 * a * c

        with np.errstate(invalid="ignore"):
            sqrt_discriminant = np.sqrt(discriminant)

        root1 = (-b + sqrt_discriminant) / (2 * a)
        root2 = (-b - sqrt_discriminant) / (2 * a)

        roots = np.stack([root1, root2], axis=0)
        # non-negative roots only; invalidate the rest before taking the min
        roots = np.where(roots >= 0, roots, np.inf)

        has_real_root = discriminant >= 0
        smallest_root = np.min(roots, axis=0)
        smallest_root = np.where(
            has_real_root & np.isfinite(smallest_root), smallest_root, np.nan
        )

        values[quadratic] = smallest_root

        return cls(
            timestamps=list(ego.timestamps.to_pydatetime()),
            values=values.tolist(),
        )
