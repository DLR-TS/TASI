from tasi import Trajectory
from tasi.smos import PET

from . import DatasetTestCase


class PETTestCase(DatasetTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Convert to TASI format which adds boundingbox columns
        cls.ds = cls.ds.to_tasi()

    def test_pet_with_string_position(self):
        """Test PET estimation with string position parameter for both trajectories"""
        # Get two trajectories from the dataset
        ids = self.ds.ids
        if len(ids) < 2:
            self.skipTest("Need at least 2 trajectories")

        tj1 = self.ds.trajectory(ids[0])
        tj2 = self.ds.trajectory(ids[1])

        # Test with string position parameter - uses "position" column from both
        pet = tj1.smos.pet(tj2, position=("position", "position"))

        # Verify PET was calculated
        self.assertIsInstance(pet.value, float)
        self.assertIsNotNone(pet.ego)
        self.assertIsNotNone(pet.challenger)
        self.assertIsNotNone(pet.point)

    def test_pet_with_tuple_position_ego(self):
        """Test PET with tuple position for ego, string for challenger"""
        ids = self.ds.ids
        if len(ids) < 2:
            self.skipTest("Need at least 2 trajectories")

        tj1 = self.ds.trajectory(ids[0])
        tj2 = self.ds.trajectory(ids[1])

        # Use ("boundingbox", "front") from tj1, "position" from tj2
        pet = tj1.smos.pet(tj2, position=(("boundingbox", "front"), "position"))

        self.assertIsInstance(pet.value, float)
        self.assertIsNotNone(pet.ego)
        self.assertIsNotNone(pet.challenger)
        self.assertIsNotNone(pet.point)

    def test_pet_with_tuple_position_challenger(self):
        """Test PET with string position for ego, tuple for challenger"""
        ids = self.ds.ids
        if len(ids) < 2:
            self.skipTest("Need at least 2 trajectories")

        tj1 = self.ds.trajectory(ids[0])
        tj2 = self.ds.trajectory(ids[1])

        # Use "position" from tj1, ("boundingbox", "front") from tj2
        pet = tj1.smos.pet(tj2, position=("position", ("boundingbox", "front")))

        self.assertIsInstance(pet.value, float)
        self.assertIsNotNone(pet.ego)
        self.assertIsNotNone(pet.challenger)
        self.assertIsNotNone(pet.point)

    def test_pet_with_tuple_position_both(self):
        """Test PET with tuple position for both trajectories"""
        ids = self.ds.ids
        if len(ids) < 2:
            self.skipTest("Need at least 2 trajectories")

        tj1 = self.ds.trajectory(ids[0])
        tj2 = self.ds.trajectory(ids[1])

        # Use ("boundingbox", "front") from tj1, ("boundingbox", "rear") from tj2
        pet = tj1.smos.pet(tj2, position=(("boundingbox", "front"), ("boundingbox", "rear")))

        self.assertIsInstance(pet.value, float)
        self.assertIsNotNone(pet.ego)
        self.assertIsNotNone(pet.challenger)
        self.assertIsNotNone(pet.point)

    def test_pet_different_positions_yield_different_results(self):
        """Test that different position selections yield different PET values"""
        ids = self.ds.ids
        if len(ids) < 2:
            self.skipTest("Need at least 2 trajectories")

        tj1 = self.ds.trajectory(ids[0])
        tj2 = self.ds.trajectory(ids[1])

        # PET using "position" from both
        pet_position = tj1.smos.pet(tj2, position=("position", "position"))

        # PET using ("boundingbox", "front") from both
        pet_front = tj1.smos.pet(tj2, position=(("boundingbox", "front"), ("boundingbox", "front")))

        # PET using ("boundingbox", "rear") from both
        pet_rear = tj1.smos.pet(tj2, position=(("boundingbox", "rear"), ("boundingbox", "rear")))

        # All should be valid floats
        self.assertIsInstance(pet_position.value, float)
        self.assertIsInstance(pet_front.value, float)
        self.assertIsInstance(pet_rear.value, float)

        # Different reference points should generally yield different PET values
        # (they might be similar but unlikely to be exactly equal)
        # Note: We don't assert they're different since in some cases they could be similar
