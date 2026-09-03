import numpy as np
import pytest

from tasi.smos import DRAC


class TestDRAC:

    def test_car_following(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        drac = DRAC.estimate(ego, challenger)

        # Hand-derived from the fixture's kinematics (see conftest.py):
        #   ego.easting(t)        = 8 * t
        #   challenger.easting(t) = 30 + 3 * t
        #   both dimension.length = 4.5
        #
        # center gap(t) = challenger.easting(t) - ego.easting(t) = 30 - 5 * t
        # bumper gap(t) = center gap(t) - (4.5 + 4.5) / 2 = 25.5 - 5 * t
        # closing_speed  = 8 - 3 = 5 (constant)
        # DRAC(t) = closing_speed ** 2 / (2 * gap(t)) = 25 / (2 * (25.5 - 5 * t))
        #         = 12.5 / (25.5 - 5 * t)
        t = np.arange(6)
        expected = 12.5 / (25.5 - 5 * t)

        np.testing.assert_allclose(drac.values, expected)
        assert list(drac.timestamps) == list(ego.timestamps.to_pydatetime())

    def test_not_closing_is_nan(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        # Swap ego/challenger: the (previously) leading, slower vehicle is
        # now "ego" and is moving away from the (previously following,
        # faster) "challenger" behind it -> closing_speed = 3 - 8 = -5 < 0
        # for every timestep, so DRAC is undefined (NaN) everywhere.
        drac = DRAC.estimate(ego=challenger, challenger=ego)

        assert np.all(np.isnan(drac.values))

    def test_mismatched_timestamps_raise(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        with pytest.raises(ValueError):
            DRAC.estimate(ego, challenger.iloc[:-1])
