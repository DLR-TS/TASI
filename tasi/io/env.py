from pydantic_settings import BaseSettings, SettingsConfigDict


class ORMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TASI_ORM_")


class DatabaseSettings(ORMSettings):

    USER: str = ""
    PASSWORD: str = ""
    HOSTNAME: str = ""
    PORT: int = 0
    DATABASE: str = ""
    DRIVER: str = ""
    CONTEXT: str = ""

    def create_engine(self, **kwargs):
        connection_string = (
            "{driver}://{username}:{password}@{hostname}:{port}/{database}"
        )

        from sqlalchemy.engine import create_engine

        return create_engine(
            connection_string.format(
                driver=self.DRIVER,
                username=self.USER,
                password=self.PASSWORD,
                hostname=self.HOSTNAME,
                port=self.PORT,
                database=self.DATABASE,
            ),
            max_identifier_length=128,
            **kwargs,
        )


class TASIDatabaseSettings(DatabaseSettings):

    DRIVER: str = "postgresql+psycopg"


DEFAULT_DATABASE_SETTINGS = TASIDatabaseSettings()
