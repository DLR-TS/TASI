import pytest

from tasi.smos import PET


class TestPET:

    def test_crossing_paths(self, crossing_trajectories):
        ego, challenger = crossing_trajectories

        # ego reaches the crossing point at t=3, challenger at t=4 (see
        # conftest.py), so PET = t_ego - t_challenger = -1s
        pet = PET.estimate(ego, challenger, position=("position", "position"))

        assert pet.value == pytest.approx(-1.0)

    def test_diverging_paths_raise(self, diverging_trajectories):
        ego, challenger = diverging_trajectories

        with pytest.raises(RuntimeError):
            PET.estimate(ego, challenger, position=("position", "position"))
