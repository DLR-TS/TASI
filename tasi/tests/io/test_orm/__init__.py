from unittest import TestCase

from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm import create_tables, drop_tables


class DBTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.engine = DEFAULT_DATABASE_SETTINGS.create_engine()

        create_tables(self.engine)

    def tearDown(self) -> None:
        super().tearDown()

        drop_tables(self.engine)
