"""Unit tests for `tasi.smos.TTC2D`.

Expected values are all hand-derived from the formula documented on
`TTC2D.estimate` (see `src/tasi/smos/ttc2d.py`), never from another SMoS
library.
"""

from datetime import datetime, timedelta
from typing import Tuple

import numpy as np
import pytest

from tasi import Trajectory
from tasi.io import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    PosePublic,
    Position,
    TrafficParticipant,
    TrajectoryPublic,
    Velocity,
)
from tasi.smos import TTC2D

T0 = datetime(2024, 1, 1, 12, 0, 0)
_CLASSIFICATIONS = Classifications(car=1.0)


def _make_trajectory(
    id_object: int,
    origin: Tuple[float, float],
    velocity: Tuple[float, float],
    length: float,
    n_steps: int = 2,
    dt: float = 1.0,
) -> Trajectory:
    """Build a synthetic constant-velocity `Trajectory` with a given
    (half-)length, so tests can use participants of different sizes -
    unlike `conftest.py`'s `_make_trajectory`, which shares one fixed
    dimension across every fixture.
    """
    dimension = Dimension(width=1.8, height=1.5, length=length)

    traffic_participant = TrafficParticipant(
        id_object=id_object,
        classifications=_CLASSIFICATIONS,
        dimension=dimension,
    )

    poses = []
    for i in range(n_steps):
        t = i * dt

        position = Position(
            easting=origin[0] + velocity[0] * t,
            northing=origin[1] + velocity[1] * t,
        )

        poses.append(
            PosePublic(
                timestamp=T0 + timedelta(seconds=t),
                position=position,
                orientation=0.0,
                traffic_participant=traffic_participant,
                dimension=dimension,
                velocity=Velocity(x=velocity[0], y=velocity[1]),
                acceleration=Acceleration(),
                classifications=_CLASSIFICATIONS,
                boundingbox=BoundingBox.from_dimension(dimension, relative_to=position),
            )
        )

    return TrajectoryPublic(
        poses=poses, traffic_participant=traffic_participant
    ).as_tasi()


class TestTTC2DPointTowardPoint:
    """A clean, exactly hand-solvable case: a stationary `ego` and a
    `challenger` approaching it head-on along a diagonal.

    ego: stationary at (0, 0), radius r_ego = length / 2 = 2.
    challenger: starts at (30, 40), velocity (-3, -4) (speed 5), radius
    r_challenger = length / 2 = 1. Combined radius R = 3.

    At t=0: dp = (30, 40), |dp| = 50; dv = (-3, -4), |dv| = 5 (pointing
    exactly along -dp, i.e. straight at ego). This reduces to 1D: the
    challenger closes the 50 m gap at 5 m/s and "collides" (reaches
    distance R=3, not 0) at tau = (50 - 3) / 5 = 9.4 s.

    Full quadratic check: dv.dv=25, dp.dv=30*-3+40*-4=-250, dp.dp=2500.
    25*tau^2 - 500*tau + (2500 - 9) = 0 -> discriminant = 500^2 - 4*25*2491
    = 250000 - 249100 = 900, sqrt=30. tau = (500 +/- 30) / 50 = 10.6 or 9.4.
    Smallest non-negative root = 9.4, matching the 1D shortcut above.
    """

    def test_head_on_approach(self):
        ego = _make_trajectory(
            id_object=1, origin=(0.0, 0.0), velocity=(0.0, 0.0), length=4.0
        )
        challenger = _make_trajectory(
            id_object=2, origin=(30.0, 40.0), velocity=(-3.0, -4.0), length=2.0
        )

        ttc2d = TTC2D.estimate(ego, challenger)

        np.testing.assert_allclose(ttc2d.values[0], 9.4)

    def test_never_within_radius_is_nan(self):
        # dv = (0, 0): no relative motion, and the gap (50) is already
        # outside the combined radius R=3 - the two never "collide".
        ego = _make_trajectory(
            id_object=1, origin=(0.0, 0.0), velocity=(0.0, 0.0), length=4.0
        )
        challenger = _make_trajectory(
            id_object=2, origin=(30.0, 40.0), velocity=(0.0, 0.0), length=2.0
        )

        ttc2d = TTC2D.estimate(ego, challenger)

        assert all(np.isnan(v) for v in ttc2d.values)


class TestTTC2DCrossingFixture:

    def test_crossing_at_t0(self, crossing_trajectories):
        # ego: position=(0,0), velocity=(5,0), length=4.5 -> r=2.25
        # challenger: position=(15,-20), velocity=(0,5), length=4.5 -> r=2.25
        # dp(0) = (15, -20), dv(0) = (-5, 5), R = 4.5
        # dv.dv = 50, dp.dv = 15*-5 + -20*5 = -175, dp.dp = 225 + 400 = 625
        # 50*tau^2 - 350*tau + (625 - 20.25) = 0
        # discriminant = 350^2 - 4*50*604.75 = 122500 - 120950 = 1550
        # tau = (350 +/- sqrt(1550)) / 100
        ego, challenger = crossing_trajectories

        ttc2d = TTC2D.estimate(ego, challenger)

        expected_t0 = (350 - np.sqrt(1550)) / 100
        np.testing.assert_allclose(ttc2d.values[0], expected_t0)
        # sanity: paths physically cross between the fixture's own t=3 and
        # t=4 (ego's and challenger's arrival times at (15, 0)), so the
        # circles (much sooner within reach given R=4.5) should register
        # a collision comfortably before then.
        assert 0 < expected_t0 < 4

    def test_mismatched_timestamps_raise(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        with pytest.raises(ValueError):
            TTC2D.estimate(ego, challenger.iloc[:-1])


class TestTTC2DDivergingFixture:

    def test_parallel_paths_never_collide(self, diverging_trajectories):
        # Both move at identical velocity (5, 0), offset by 10 m in
        # northing: dv = 0 everywhere, and |dp| = 10 > R = 4.5 always, so
        # they never come within the combined radius.
        ego, challenger = diverging_trajectories

        ttc2d = TTC2D.estimate(ego, challenger)

        assert all(np.isnan(v) for v in ttc2d.values)
