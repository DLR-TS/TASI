import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock

from tasi.dlr.dataset import (
    DLRHTDatasetManager,
    DLRHTVersion,
    DLRUTDatasetManager,
    DLRUTVersion,
)
from tasi.tests import DATA_PATH


class DLRUTExtractTestCase(TestCase):

    def setUp(self):

        self.target = TemporaryDirectory()

        self.manager = DLRUTDatasetManager(DLRUTVersion.v1_2_0, path=Path(DATA_PATH))

        return super().setUp()

    def tearDown(self):

        self.target.cleanup()

        return super().tearDown()

    def test_extract(self):

        dst = Path(self.target.name)
        self.manager.extract(
            self.manager._path.joinpath(f"{self.manager.filename}"), dst
        )

        self.assertTrue(
            os.path.exists(dst.joinpath("DLR-Urban-Traffic-dataset_v1-2-0"))
        )


class DLRUHTExtractTestCase(TestCase):

    def setUp(self):

        self.target = TemporaryDirectory()

        self.manager = DLRHTDatasetManager(DLRHTVersion.v1_1_0, path=Path(DATA_PATH))

        return super().setUp()

    def tearDown(self):

        self.target.cleanup()

        return super().tearDown()

    def test_extract(self):

        dst = Path(self.target.name)

        self.manager.extract(
            self.manager._path.joinpath(f"{self.manager.filename}"), dst
        )

        self.assertTrue(
            os.path.exists(dst.joinpath("DLR-Highway-Traffic-dataset_v1-1-0"))
        )


class DLRUTLoadTestCase(TestCase):

    def setUp(self):

        self.target = TemporaryDirectory()

        self.manager = DLRUTDatasetManager(DLRUTVersion.v1_2_0, path=Path(DATA_PATH))

        return super().setUp()

    def tearDown(self):

        self.target.cleanup()

        return super().tearDown()

    def test_load_but_already_downloaded(self):

        # copy downloaded zip to the temporary directy
        shutil.copy(os.path.join(DATA_PATH, self.manager.filename), self.target.name)

        self.manager.download = Mock(
            side_effect=KeyError("download() was called although dataset should exist")
        )

        # call the load method. It should only extract it
        self.manager.load(Path(self.target.name))

        self.assertTrue(
            os.path.exists(
                Path(self.target.name).joinpath("DLR-Urban-Traffic-dataset_v1-2-0/")
            )
        )
