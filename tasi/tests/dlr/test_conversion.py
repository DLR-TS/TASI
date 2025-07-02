import logging
from unittest import TestCase

from tasi.dlr.dataset import DLRTrajectoryDataset
from tasi.dlr.dataset import DLRUTDatasetManager as Manager

logging.getLogger().setLevel(logging.ERROR)


class DatasetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        manager = Manager("latest")
        manager.load()

        cls.ds: DLRTrajectoryDataset = DLRTrajectoryDataset.from_csv(
            manager.trajectory()[0]
        )

    def test_convert_to_tasi_manually(self):
        import pandas as pd

        DLRTrajectoryDataset.from_attributes(
            position=self.ds.position,
            velocity=pd.DataFrame(),
            acceleration=pd.DataFrame(),
            heading=self.ds.yaw,
            classifications=self.ds.classifications,
            dimension=self.ds.dimension,
        )

    def test_convert_to_tasi(self):

        from tasi.dataset import TrajectoryDataset as TD

        obj = self.ds.to_tasi()

        self.assertIsInstance(obj, TD)

        self.assertTrue("position" in obj.attributes)
        self.assertTrue("velocity" in obj.attributes)
        self.assertTrue("acceleration" in obj.attributes)
        self.assertTrue("boundingbox" in obj.attributes)
