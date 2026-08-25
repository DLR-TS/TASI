import logging
from typing import Any, List, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.sql.schema import Table

from . import MODELS
from .base import Base


class TASIORMBase:
    pass


class DatabaseSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="TASI_ORM_", env_file=".tasiorm")

    USER: str = ""
    PASSWORD: str = ""
    HOSTNAME: str = ""
    PORT: int = 0
    DATABASE: str = ""
    SCHEMA: str = ""

    def create_engine(self, **kwargs) -> Engine:
        connection_string = (
            "postgresql+psycopg://{username}:{password}@{hostname}:{port}/{database}"
        )

        from sqlalchemy.engine import create_engine

        return create_engine(
            connection_string.format(
                username=self.USER,
                password=self.PASSWORD,
                hostname=self.HOSTNAME,
                port=self.PORT,
                database=self.DATABASE,
            ),
            max_identifier_length=128,
            execution_options={
                "schema_translate_map": {
                    "schema": self.SCHEMA,
                }
            },
            **kwargs,
        )

    def init_schema(self, engine: Engine | None):

        logging.info("Initialize schema %s if not exits.", self.SCHEMA)

        if engine is None:
            engine = self.create_engine(**kwargs)

        # initialize the schema
        with engine.connect() as conn, conn.begin():
            conn.execute(CreateSchema(self.SCHEMA, if_not_exists=True))

    def init(self, engine: Engine | None = None, **kwargs):
        """Initialize the database environment"""

        if engine is None:
            engine = self.create_engine(**kwargs)

        self.init_schema(engine=engine)

        from tasi.io.orm.base import MODELS as BASE_MODELS
        from tasi.io.orm.pose.base import MODELS as POSE_MODELS
        from tasi.io.orm.traffic_light import MODELS as TL_MODELS
        from tasi.io.orm.traffic_participant import MODELS as TP_MODELS
        from tasi.io.orm.trajectory.base import MODELS as TJ_MODELS
        from tasi.utils import has_extra

        create_tables(engine, BASE_MODELS)

        create_tables(engine, TP_MODELS)

        create_tables(engine, TL_MODELS)

        if has_extra("geo"):
            from .geo import POSE_MODELS as GEO_POSE_MODELS
            from .geo import TRAJECTORY_MODELS as GEO_TL_MODELS

            create_tables(engine, GEO_TL_MODELS)
            create_tables(engine, GEO_POSE_MODELS)

        create_tables(engine, TJ_MODELS)

        create_tables(engine, POSE_MODELS)

        return engine

    def shutdown(
        self, engine: Engine | None = None, with_schema: bool = False, **kwargs
    ):
        """Cleanup the database environment"""

        if engine is None:
            engine = self.create_engine(**kwargs)

        if with_schema:
            with engine.connect() as conn, conn.begin():
                conn.execute(DropSchema(self.SCHEMA, cascade=True, if_exists=True))
        else:

            from tasi.io.orm.base import MODELS as BASE_MODELS
            from tasi.io.orm.pose.base import MODELS as POSE_MODELS
            from tasi.io.orm.traffic_light import MODELS as TL_MODELS
            from tasi.io.orm.traffic_participant import MODELS as TP_MODELS
            from tasi.io.orm.trajectory.base import MODELS as TJ_MODELS
            from tasi.utils import has_extra

            drop_tables(engine, POSE_MODELS)

            drop_tables(engine, TJ_MODELS)

            if has_extra("geo"):
                from .geo import POSE_MODELS as GEO_POSE_MODELS
                from .geo import TRAJECTORY_MODELS as GEO_TL_MODELS

                drop_tables(engine, GEO_POSE_MODELS)

                drop_tables(engine, GEO_TL_MODELS)

            drop_tables(engine, TL_MODELS)

            drop_tables(engine, TP_MODELS)

            drop_tables(engine, BASE_MODELS)


def create_tables(engine, tables: List[Union[Table, Any]] = MODELS):

    Base.metadata.create_all(
        engine,
        tables=[t.__table__ if not isinstance(t, Table) else t for t in tables],
        checkfirst=True,
    )


def drop_tables(engine, tables: List[Union[Table, Any]] = MODELS):

    Base.metadata.drop_all(
        engine,
        tables=[t.__table__ if not isinstance(t, Table) else t for t in tables],
    )
