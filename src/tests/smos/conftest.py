"""Shared synthetic trajectory fixtures for `tasi.smos` unit tests.

Each fixture returns an `(ego, challenger)` pair of `tasi.Trajectory` objects
with exact, hand-computable kinematics (constant velocity, zero
acceleration), so that SMoS unit tests can assert exact expected values
instead of relying on tolerances.
"""

from datetime import datetime, timedelta
from typing import Tuple

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

#: The timestep between two consecutive poses, in seconds
DT = 1.0

#: The number of poses per synthetic trajectory
N_STEPS = 6

#: Reference start time. Only relative timestamps matter for the fixtures.
T0 = datetime(2024, 1, 1, 12, 0, 0)

#: The dimension shared by all synthetic participants (a mid-size car)
_DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)

#: The classification shared by all synthetic participants
_CLASSIFICATIONS = Classifications(car=1.0)


def _make_trajectory(
    id_object: int,
    origin: Tuple[float, float],
    velocity: Tuple[float, float],
    n_steps: int = N_STEPS,
    dt: float = DT,
) -> Trajectory:
    """Build a synthetic constant-velocity `Trajectory`.

    Position at step `i` (`i = 0, ..., n_steps - 1`, `t = i * dt`) is::

        easting(t)  = origin[0] + velocity[0] * t
        northing(t) = origin[1] + velocity[1] * t

    with `velocity` constant (zero acceleration) at every step, so tests can
    assert exact expected values by plugging `t = i * dt` into the formula
    above.

    Args:
        id_object (int): The trajectory's participant id.
        origin (Tuple[float, float]): The (easting, northing) position at `t=0`.
        velocity (Tuple[float, float]): The constant (easting, northing) velocity.
        n_steps (int, optional): The number of poses to generate. Defaults to `N_STEPS`.
        dt (float, optional): The timestep between poses in seconds. Defaults to `DT`.

    Returns:
        Trajectory: The synthetic trajectory.
    """
    traffic_participant = TrafficParticipant(
        id_object=id_object,
        classifications=_CLASSIFICATIONS,
        dimension=_DIMENSION,
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
                dimension=_DIMENSION,
                velocity=Velocity(x=velocity[0], y=velocity[1]),
                acceleration=Acceleration(),
                classifications=_CLASSIFICATIONS,
                boundingbox=BoundingBox.from_dimension(
                    _DIMENSION, relative_to=position
                ),
            )
        )

    return TrajectoryPublic(
        poses=poses, traffic_participant=traffic_participant
    ).as_tasi()


@pytest.fixture
def car_following_trajectories() -> Tuple[Trajectory, Trajectory]:
    """Rear-end / car-following conflict geometry: collinear, closing speed.

    Both participants move along the easting axis at constant velocity:

    - ego (id=1): `easting(t) = 8 * t`, starting 30 m behind the challenger.
    - challenger (id=2): `easting(t) = 30 + 3 * t`.

    The ego is faster than the challenger, closing the gap at a constant
    `5 m/s`. The gap at time `t` is `30 - 5 * t` meters, always positive
    within the sampled window `t = 0..5 s`.
    """
    ego = _make_trajectory(id_object=1, origin=(0.0, 0.0), velocity=(8.0, 0.0))
    challenger = _make_trajectory(id_object=2, origin=(30.0, 0.0), velocity=(3.0, 0.0))
    return ego, challenger


@pytest.fixture
def crossing_trajectories() -> Tuple[Trajectory, Trajectory]:
    """Crossing/turning conflict geometry: paths intersect at a right angle.

    - ego (id=1): moves along the easting axis, `easting(t) = 5 * t`,
      `northing = 0`. It reaches the crossing point `(15, 0)` at `t = 3 s`.
    - challenger (id=2): moves along the northing axis, `easting = 15`,
      `northing(t) = -20 + 5 * t`. It reaches the crossing point `(15, 0)`
      at `t = 4 s`.

    The ego arrives at the conflict point one second before the challenger,
    so `PET = t_ego - t_challenger = -1 s`.
    """
    ego = _make_trajectory(id_object=1, origin=(0.0, 0.0), velocity=(5.0, 0.0))
    challenger = _make_trajectory(
        id_object=2, origin=(15.0, -20.0), velocity=(0.0, 5.0)
    )
    return ego, challenger


@pytest.fixture
def diverging_trajectories() -> Tuple[Trajectory, Trajectory]:
    """No-conflict geometry: parallel paths that never intersect.

    Both participants move along the easting axis with identical constant
    velocity, offset by 10 m in the northing direction:

    - ego (id=1): `easting(t) = 5 * t`, `northing = 0`.
    - challenger (id=2): `easting(t) = 5 * t`, `northing = 10`.

    The two lines are parallel and never cross, so no conflict point exists.
    """
    ego = _make_trajectory(id_object=1, origin=(0.0, 0.0), velocity=(5.0, 0.0))
    challenger = _make_trajectory(id_object=2, origin=(0.0, 10.0), velocity=(5.0, 0.0))
    return ego, challenger
