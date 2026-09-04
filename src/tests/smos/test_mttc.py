"""Unit tests for `tasi.smos.MTTC`.

Expected values are all hand-derived from the formula documented on
`MTTC.estimate` (see `src/tasi/smos/mttc.py`), never from another SMoS
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
from tasi.smos import MTTC

T0 = datetime(2024, 1, 1, 12, 0, 0)
_DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)
_CLASSIFICATIONS = Classifications(car=1.0)


def _make_accelerating_trajectory(
    id_object: int,
    origin: float,
    v0: float,
    accel: float,
    n_steps: int,
    dt: float = 1.0,
) -> Trajectory:
    """Build a synthetic 1D (easting-only) `Trajectory` with constant
    acceleration, i.e. `speed(t) = v0 + accel * t` and
    `easting(t) = origin + v0 * t + 0.5 * accel * t ** 2`.

    Unlike `conftest.py`'s `_make_trajectory` (constant velocity only), this
    varies velocity per pose so tests can exercise MTTC's quadratic branch.
    """
    traffic_participant = TrafficParticipant(
        id_object=id_object,
        classifications=_CLASSIFICATIONS,
        dimension=_DIMENSION,
    )

    poses = []
    for i in range(n_steps):
        t = i * dt
        easting = origin + v0 * t + 0.5 * accel * t**2
        speed = v0 + accel * t

        position = Position(easting=easting, northing=0.0)

        poses.append(
            PosePublic(
                timestamp=T0 + timedelta(seconds=t),
                position=position,
                orientation=0.0,
                traffic_participant=traffic_participant,
                dimension=_DIMENSION,
                velocity=Velocity(x=speed, y=0.0),
                acceleration=Acceleration(x=accel, y=0.0),
                classifications=_CLASSIFICATIONS,
                boundingbox=BoundingBox.from_dimension(
                    _DIMENSION, relative_to=position
                ),
            )
        )

    return TrajectoryPublic(
        poses=poses, traffic_participant=traffic_participant
    ).as_tasi()


class TestMTTCZeroAcceleration:
    """With zero relative acceleration, MTTC must equal the classic TTC."""

    def test_matches_classic_ttc(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        mttc = MTTC.estimate(ego, challenger)

        # ego (follower) closes at dv = 8 - 3 = 5 m/s (constant); bumper
        # gap(t) = (challenger.easting - ego.easting) - dimension.length
        #        = (30 - 5t) - 4.5 = 25.5 - 5t
        # classic TTC(t) = gap(t) / dv = (25.5 - 5t) / 5 = 5.1 - t
        expected = [5.1 - t for t in range(6)]

        np.testing.assert_allclose(mttc.values, expected)


class TestMTTCConstantAcceleration:
    """Non-zero relative acceleration exercises the quadratic branch.

    ego (follower) accelerates at 4 m/s^2 from the same initial speed as
    challenger (leader, constant 5 m/s); both start with a bumper gap of
    8 m (ego at easting=0, challenger at easting=12.5, length=4.5 each ->
    gap = 12.5 - 4.5 = 8):

        ego.easting(t)        = 5t + 2t^2      (v0=5, a=4)
        challenger.easting(t) = 12.5 + 5t       (v0=5, a=0)
        gap(t) = (12.5 + 5t) - (5t + 2t^2) - 4.5 = 8 - 2t^2

    At t=0: dv=0, da=4, gap=8.
        0.5*4*tau^2 + 0*tau - 8 = 0  =>  2*tau^2 = 8  =>  tau = 2 (>=0 root)
    At t=1: dv = ego.speed(1) - challenger.speed(1) = 9 - 5 = 4, da=4, gap=6.
        2*tau^2 + 4*tau - 6 = 0  =>  tau^2 + 2*tau - 3 = 0
        => (tau + 3)(tau - 1) = 0  =>  tau = 1 (the >=0 root)
    """

    @pytest.fixture
    def accelerating_pair(self) -> Tuple[Trajectory, Trajectory]:
        ego = _make_accelerating_trajectory(
            id_object=1, origin=0.0, v0=5.0, accel=4.0, n_steps=2
        )
        challenger = _make_accelerating_trajectory(
            id_object=2, origin=12.5, v0=5.0, accel=0.0, n_steps=2
        )
        return ego, challenger

    def test_quadratic_branch(self, accelerating_pair):
        ego, challenger = accelerating_pair

        mttc = MTTC.estimate(ego, challenger)

        np.testing.assert_allclose(mttc.values, [2.0, 1.0])


class TestMTTCNotClosing:
    """No positive/non-negative real root -> MTTC is NaN."""

    @pytest.fixture
    def diverging_pair(self) -> Tuple[Trajectory, Trajectory]:
        # ego (follower) slower than challenger (leader) with zero relative
        # acceleration: dv = 3 - 8 = -5 (< 0, not closing), da = 0 -> the
        # linear branch requires dv > 0, so this must be NaN at every step.
        ego = _make_accelerating_trajectory(
            id_object=1, origin=0.0, v0=3.0, accel=0.0, n_steps=4
        )
        challenger = _make_accelerating_trajectory(
            id_object=2, origin=30.0, v0=8.0, accel=0.0, n_steps=4
        )
        return ego, challenger

    def test_not_closing_is_nan(self, diverging_pair):
        ego, challenger = diverging_pair

        mttc = MTTC.estimate(ego, challenger)

        assert all(np.isnan(v) for v in mttc.values)


class TestMTTCValidation:

    def test_mismatched_timestamps_raise(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        with pytest.raises(ValueError):
            MTTC.estimate(ego, challenger.iloc[:-1])
