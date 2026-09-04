import numpy as np
import pytest

from tasi.smos import TAdv


class TestTAdv:

    def test_crossing_paths(self, crossing_trajectories):
        # conflict point is (15, 0) - see conftest.py.
        # ego: position(t) = (5t, 0), constant speed 5 -> reaches the point
        # at t=3. Since motion is a straight line at constant speed through
        # the point, distance(t)/speed = |3 - t| for every sampled t.
        # challenger: position(t) = (15, -20 + 5t), constant speed 5 ->
        # reaches the point at t=4, so distance(t)/speed = |4 - t|.
        # TAdv(t) = | |3 - t| - |4 - t| |. For every integer t in 0..5,
        # this simplifies to exactly 1.0 (t and the two arrival times never
        # straddle each other strictly between samples here).
        ego, challenger = crossing_trajectories

        tadv = TAdv.estimate(ego, challenger, position=("position", "position"))

        expected = [1.0] * 6
        np.testing.assert_allclose(tadv.values, expected)
        assert list(tadv.timestamps) == list(ego.timestamps)

    def test_diverging_paths_raise(self, diverging_trajectories):
        ego, challenger = diverging_trajectories

        with pytest.raises(RuntimeError):
            TAdv.estimate(ego, challenger, position=("position", "position"))

    def test_mismatched_timestamps_raise(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        with pytest.raises(ValueError):
            TAdv.estimate(ego, challenger.iloc[:-1])
