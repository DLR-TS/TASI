import numpy as np
import pandas as pd
import logging
import logging
from unittest import TestCase

pd.set_option("display.precision", 3, "display.width", 80)
np.set_printoptions(legacy="1.25", precision=3, suppress=True)

logging.getLogger().setLevel(logging.ERROR)


class DatasetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        from tasi.dlr.dataset import DLRTrajectoryDataset
        from tasi.dlr.dataset import DLRUTDatasetManager as Manager

        manager = Manager("latest")
        manager.load()

        cls.ds: DLRTrajectoryDataset = DLRTrajectoryDataset.from_csv(
            manager.trajectory()[0]
        )
