import os
from pathlib import Path
from unittest import TestCase
from tasi.dlr.dataset import DLRUTDatasetManager


class DLRUTLoadTestCase(TestCase):

    def test_load_v100_version(self):

        path = Path("/tmp")
        manager = DLRUTDatasetManager(DLRUTDatasetManager.VERSIONS.v1_0_0)
        manager.load(path=path)

        os.path.exists(path.joinpath('DLR-UT_v1-0-0'))

    def test_load_v101_version(self):

        path = Path("/tmp")
        manager = DLRUTDatasetManager(DLRUTDatasetManager.VERSIONS.v1_0_1)
        manager.load(path=path)

        os.path.exists(path.joinpath('DLR-UT_v1-0-0'))