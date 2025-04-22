import logging

from .. import DatasetTestCase
from tasi.dlr.dataset import ObjectClass, DLRTrajectoryDataset

logging.getLogger().setLevel(logging.ERROR)


class TrajectoryRoadUserTypeAccess(DatasetTestCase):

    def test_object_classes(self):

        ds = DLRTrajectoryDataset(self.ds)

        for obj in ObjectClass:
            getattr(ds, obj.name + "s")

        self.assertTrue(hasattr(ds, "mru"))
        self.assertTrue(hasattr(ds, "vru"))
