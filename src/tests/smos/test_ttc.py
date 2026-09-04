import numpy as np

from tasi.smos import TTC


class TestTTC:

    def test_car_following(self, car_following_trajectories):
        # ego (follower): easting(t) = 8t -> 0, 8, 16, 24, 32, 40
        # challenger (leader): easting(t) = 30 + 3t -> 30, 33, 36, 39, 42, 45
        # both have dimension.length == 4.5, so:
        #   gap(t) = (challenger.easting - ego.easting) - (4.5 + 4.5) / 2
        #          = (30 - 5t) - 4.5 = 25.5 - 5t
        # closing_speed = ego.velocity.easting - challenger.velocity.easting
        #               = 8 - 3 = 5 (constant, > 0 -> always closing)
        # TTC(t) = gap(t) / closing_speed = (25.5 - 5t) / 5 = 5.1 - t
        ego, challenger = car_following_trajectories

        ttc = TTC.estimate(ego, challenger)

        expected = [5.1, 4.1, 3.1, 2.1, 1.1, 0.1]
        np.testing.assert_allclose(ttc.values, expected)
        assert list(ttc.timestamps) == list(ego.timestamps)

    def test_not_closing_is_nan(self, car_following_trajectories):
        # The fixture returns (follower, leader). Swap the roles passed to
        # estimate(): the (slower) leader now plays "ego" and the (faster)
        # follower now plays "challenger", so the new ego is not closing in
        # on the new challenger (closing_speed = 3 - 8 = -5 < 0), and TTC is
        # undefined at every timestep.
        follower, leader = car_following_trajectories

        ttc = TTC.estimate(ego=leader, challenger=follower)

        assert all(np.isnan(v) for v in ttc.values)

    def test_mismatched_timestamps_raise(self, car_following_trajectories):
        ego, challenger = car_following_trajectories

        with np.testing.assert_raises(ValueError):
            TTC.estimate(ego, challenger.iloc[:-1])
