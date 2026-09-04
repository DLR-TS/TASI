import numpy as np

from tasi import Trajectory

from .base import TimeSeriesSMOS


class TTC2D(TimeSeriesSMOS):
    """Generalized Time-to-Collision for non-collinear (crossing/turning) paths.

    Unlike `TTC` (which only handles straight-line, same-direction
    car-following), `TTC2D` treats `ego` and `challenger` as circles moving
    freely in the 2D plane and predicts, at every sampled timestep, when
    (if ever) they would first come within a combined safety radius of each
    other, assuming each continues at its *current, instantaneous* velocity
    from that timestep onward.

    Definition, adapted from Li, S., Anis, M., Lord, D., Zhang, H., Zhou,
    Y., & Ye, X. (2024), "Beyond 1D and oversimplified kinematics: A
    generic analytical framework for surrogate safety measures," Accident
    Analysis & Prevention, 199, 107531 - which formulates exactly this
    circle-based, 2D generalization of TTC and solves it as a quadratic in
    time. (PLAN.md pointed at "Allen et al. / Sultan-style generalization";
    checked both - Allen, Shin & Cooper (1978) introduce PET for 1D
    longitudinal conflicts only, and Sultan, Brackstone & McDonald (2004)
    is a 1D car-following acceleration model. Neither actually contains
    this 2D formula, so it is cited to the paper that does.)

    Model each participant as a circle of radius `r = dimension.length / 2`
    (a simplification - the vehicle's half-length, not its true footprint;
    documented here rather than silently assumed) and let, at time `t`::

        dp(t) = challenger.position(t) - ego.position(t)   # 2D: easting, northing
        dv(t) = challenger.velocity(t) - ego.velocity(t)    # 2D
        R = r_ego + r_challenger

    Projecting both participants' positions forward by `tau` seconds under
    constant velocity, a collision (the two circles touching) happens when::

        |dp(t) + dv(t) * tau| ** 2 = R ** 2

    which expands to the quadratic (dot products of the 2D vectors)::

        (dv . dv) * tau ** 2 + 2 * (dp . dv) * tau + (dp . dp - R ** 2) = 0

    `TTC2D(t)` is the smallest non-negative real root `tau`. If `dv . dv`
    is (numerically) zero - no relative motion - `TTC2D(t)` is `0` when
    already within `R` (`|dp(t)| <= R`), else `NaN` (the gap never
    changes). Otherwise `NaN` if the discriminant is negative or every
    real root is negative (paths never come within `R` of each other,
    looking forward from `t`).

    This is a `TimeSeriesSMOS` (one predicted value per sampled timestep),
    not a scalar `SMOS` like `PET`: the cited framework evaluates the
    circle-collision condition from each participant's *current* state at
    every timestep, exactly generalizing the per-timestep predictive
    structure of `TTC` rather than reducing the interaction to a single
    static conflict point. It does not use `conflict_point()` from
    `tasi.smos.geometry` - the geometric paths' possible intersection point
    is not needed for this per-timestep, constant-velocity-projection
    formulation.
    """

    @classmethod
    def estimate(cls, ego: Trajectory, challenger: Trajectory) -> "TTC2D":
        """Estimate the TTC2D time series between `ego` and `challenger`.

        Args:
            ego (Trajectory): One participant's trajectory.
            challenger (Trajectory): The other participant's trajectory.

        Returns:
            TTC2D: The TTC2D value at every shared timestamp.

        Raises:
            ValueError: If `ego` and `challenger` do not share the same
                timestamps.
        """
        if not np.array_equal(ego.timestamps.values, challenger.timestamps.values):
            raise ValueError(
                "'ego' and 'challenger' must share the same timestamps to "
                "estimate TTC2D"
            )

        # `ego` and `challenger` carry different `id`s on their index, so a
        # pandas-aligned subtraction of the two Series would align on
        # (timestamp, id) and produce an all-NaN result; convert to numpy
        # first to subtract element-wise by position instead.
        ego_position = ego.position[["easting", "northing"]].to_numpy()
        challenger_position = challenger.position[["easting", "northing"]].to_numpy()
        ego_velocity = ego.velocity[["easting", "northing"]].to_numpy()
        challenger_velocity = challenger.velocity[["easting", "northing"]].to_numpy()

        dp = challenger_position - ego_position
        dv = challenger_velocity - ego_velocity

        R = (ego.dimension.length.to_numpy() + challenger.dimension.length.to_numpy()) / 2

        dp_dp = np.sum(dp * dp, axis=1)
        dp_dv = np.sum(dp * dv, axis=1)
        dv_dv = np.sum(dv * dv, axis=1)

        values = np.full(dp_dp.shape, np.nan)

        no_relative_motion = np.isclose(dv_dv, 0)
        already_within_radius = dp_dp <= R**2
        values[no_relative_motion & already_within_radius] = 0.0
        # no_relative_motion & ~already_within_radius stays NaN: the gap
        # never changes and is already outside the collision radius.

        quadratic = ~no_relative_motion

        a = dv_dv[quadratic]
        b = 2 * dp_dv[quadratic]
        c = dp_dp[quadratic] - R[quadratic] ** 2

        discriminant = b**2 - 4 * a * c

        with np.errstate(invalid="ignore"):
            sqrt_discriminant = np.sqrt(discriminant)

        root1 = (-b + sqrt_discriminant) / (2 * a)
        root2 = (-b - sqrt_discriminant) / (2 * a)

        roots = np.stack([root1, root2], axis=0)
        roots = np.where(roots >= 0, roots, np.inf)

        smallest_root = np.min(roots, axis=0)
        has_real_root = discriminant >= 0
        smallest_root = np.where(
            has_real_root & np.isfinite(smallest_root), smallest_root, np.nan
        )

        values[quadratic] = smallest_root

        return cls(timestamps=list(ego.timestamps), values=values.tolist())
