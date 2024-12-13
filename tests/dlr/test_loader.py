import os
from pathlib import Path
from unittest import TestCase
from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion, DLRHTDatasetManager, DLRHTVersion


class DLRUTLoadTestCase(TestCase):

    def test_load_v100_version(self):

        path = Path("/tmp")
        manager = DLRUTDatasetManager(DLRUTVersion.v1_0_0)
        manager.load(path=path)

        self.assertTrue(os.path.exists(path.joinpath('DLR-UT_v1-0-0')))

    def test_load_v101_version(self):

        path = Path("/tmp")
        manager = DLRUTDatasetManager(DLRUTVersion.v1_0_1)
        manager.load(path=path)

        self.assertTrue(os.path.exists(path.joinpath('DLR-UT_v1-0-0')))

    
    def test_load_v110_version(self):
        path = Path("/tmp")
        manager = DLRUTDatasetManager(DLRUTVersion.v1_1_0)
        manager.load(path=path)

        self.assertTrue(os.path.exists(path.joinpath('DLR-Urban-Traffic-dataset_v1-1-0/')))


class DLRHTLoadTestCase(TestCase):

    def test_load_v100_version(self):

        path = Path("/tmp")
        manager = DLRHTDatasetManager(DLRHTVersion.v1_0_0)
        manager.load(path=path)

        self.assertTrue(os.path.exists(path.joinpath('DLR-Highway-Traffic-dataset_v1-0-0/')))
