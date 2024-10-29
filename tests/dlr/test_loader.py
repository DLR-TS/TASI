import os
from pathlib import Path
from unittest import TestCase
import tempfile
from tasi.dlr.dataset import download


class DLRUTLoadTestCase(TestCase):

    def test_load_version(self):
        with tempfile.TemporaryDirectory() as path:
            
            path = Path(path)
            download(name="urban", version="1.0.1", path=path)

            os.path.exists(path.joinpath('DLR-UT_v1-0-1'))
