"""Sanity checks for the shared synthetic fixtures in `conftest.py`.

These are not SMoS unit tests themselves - they verify that the fixtures
expose the exact, hand-computable kinematics documented in their docstrings.
"""

import numpy as np
from shapely.geometry import LineString


class TestCarFollowingFixture:

    def test_positions(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        np.testing.assert_allclose(
            ego.position.easting.to_numpy(), [0, 8, 16, 24, 32, 40]
        )
        np.testing.assert_allclose(
            challenger.position.easting.to_numpy(), [30, 33, 36, 39, 42, 45]
        )

    def test_closing_gap(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        gap = challenger.position.easting.to_numpy() - ego.position.easting.to_numpy()

        # gap(t) = 30 - 5 * t, always positive and strictly decreasing
        np.testing.assert_allclose(gap, [30, 25, 20, 15, 10, 5])
        assert np.all(np.diff(gap) < 0)


class TestCrossingFixture:

    def test_positions_at_crossing(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        # ego reaches the crossing point (15, 0) at t=3 (index 3)
        np.testing.assert_allclose(
            ego.position.iloc[3][["easting", "northing"]].to_numpy(),
            [15.0, 0.0],
        )

        # challenger reaches the crossing point (15, 0) at t=4 (index 4)
        np.testing.assert_allclose(
            challenger.position.iloc[4][["easting", "northing"]].to_numpy(),
            [15.0, 0.0],
        )

    def test_paths_intersect_at_conflict_point(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        ego_line = LineString(ego.position[["easting", "northing"]].to_numpy())
        challenger_line = LineString(
            challenger.position[["easting", "northing"]].to_numpy()
        )

        intersection = ego_line.intersection(challenger_line)

        np.testing.assert_allclose(list(intersection.coords)[0], [15.0, 0.0])


class TestDivergingFixture:

    def test_parallel_no_intersection(self, diverging_trajectories):
        ego, challenger = diverging_trajectories

        # constant 10 m offset in northing at every timestep
        offset = (
            challenger.position.northing.to_numpy() - ego.position.northing.to_numpy()
        )
        np.testing.assert_allclose(offset, 10.0)

    def test_paths_do_not_intersect(self, diverging_trajectories):
        ego, challenger = diverging_trajectories

        ego_line = LineString(ego.position[["easting", "northing"]].to_numpy())
        challenger_line = LineString(
            challenger.position[["easting", "northing"]].to_numpy()
        )

        assert not ego_line.intersects(challenger_line)
