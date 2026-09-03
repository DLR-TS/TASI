import numpy as np
import pytest

from tasi.smos import THW

from .conftest import _make_trajectory


class TestTHW:

    def test_car_following(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        thw = THW.estimate(ego, challenger)

        # net gap(t) = (challenger.easting(t) - ego.easting(t)) - (4.5 + 4.5) / 2
        #            = (30 - 5 * t) - 4.5 = 25.5 - 5 * t
        # ego speed is constant at 8 m/s (ego is the follower)
        # THW(t) = gap(t) / 8
        #   t=0: 25.5 / 8 = 3.1875
        #   t=1: 20.5 / 8 = 2.5625
        #   t=2: 15.5 / 8 = 1.9375
        #   t=3: 10.5 / 8 = 1.3125
        #   t=4:  5.5 / 8 = 0.6875
        #   t=5:  0.5 / 8 = 0.0625
        expected = [3.1875, 2.5625, 1.9375, 1.3125, 0.6875, 0.0625]

        np.testing.assert_allclose(thw.values, expected)
        assert list(thw.timestamps) == list(ego.timestamps)

    def test_stopped_ego_is_nan(self):
        # ego (follower) is stationary -> headway is undefined at every step
        ego = _make_trajectory(id_object=1, origin=(0.0, 0.0), velocity=(0.0, 0.0))
        challenger = _make_trajectory(
            id_object=2, origin=(30.0, 0.0), velocity=(3.0, 0.0)
        )

        thw = THW.estimate(ego, challenger)

        assert all(np.isnan(v) for v in thw.values)

    def test_mismatched_timestamps_raise(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        # drop the last pose from challenger so timestamps no longer align
        challenger = challenger.iloc[:-1]

        with pytest.raises(ValueError):
            THW.estimate(ego, challenger)
