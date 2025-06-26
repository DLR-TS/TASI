import logging

from tasi.dlr.dataset import DLRTrajectoryDataset, ObjectClass

from .. import DatasetTestCase

logging.getLogger().setLevel(logging.ERROR)


class TrajectoryRoadUserTypeAccess(DatasetTestCase):

    def test_object_classes(self):

        ds = DLRTrajectoryDataset(self.ds)

        for obj in ObjectClass:
            getattr(ds, obj.name + "s")

        self.assertTrue(hasattr(ds, "mru"))
        self.assertTrue(hasattr(ds, "vru"))
