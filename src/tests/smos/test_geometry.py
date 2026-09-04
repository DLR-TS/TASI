import numpy as np

from tasi.smos.geometry import conflict_point


class TestConflictPoint:

    def test_crossing_paths(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        result = conflict_point(ego, challenger, position=("position", "position"))

        assert result is not None
        point, ego_idx, challenger_idx = result

        # crossing point is (15, 0); ego reaches it at t=3 (index 3),
        # challenger at t=4 (index 4) - see conftest.py
        np.testing.assert_allclose(point, [15.0, 0.0])
        assert ego_idx == 3
        assert challenger_idx == 4

    def test_diverging_paths_return_none(self, diverging_trajectories):
        ego, challenger = diverging_trajectories

        result = conflict_point(ego, challenger, position=("position", "position"))

        assert result is None
