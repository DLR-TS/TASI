import logging
import os
from pathlib import Path
from unittest import TestCase

import numpy as np
import pandas as pd

pd.set_option("display.precision", 3, "display.width", 80)
np.set_printoptions(legacy="1.25", precision=3, suppress=True)

logging.getLogger().setLevel(logging.ERROR)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")


class DatasetTestCase(TestCase):

    @classmethod
    def setUpClass(cls):

        from tasi.dlr.dataset import DLRTrajectoryDataset
        from tasi.dlr.dataset import DLRUTDatasetManager as Manager
        from tasi.dlr.dataset import DLRUTVersion

        cls.manager = Manager(DLRUTVersion.v1_2_0, path=Path(DATA_PATH))
        cls.manager.load()

        cls.ds: DLRTrajectoryDataset = DLRTrajectoryDataset.from_csv(
            cls.manager.trajectory()[0]
        )
