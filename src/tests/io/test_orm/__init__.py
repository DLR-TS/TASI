from unittest import TestCase
from uuid import uuid4

from tasi.io.orm import create_tables, drop_tables
from tasi.io.orm.db import DatabaseSettings


class DBTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.settings = DatabaseSettings(SCHEMA=str(uuid4()))

        self.engine = self.settings.create_engine()
        self.settings.init(self.engine)

    def tearDown(self) -> None:
        super().tearDown()

        self.settings.shutdown(self.engine, with_schema=True)
