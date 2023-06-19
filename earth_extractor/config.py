from pydantic import BaseSettings
import logging


class Constants(BaseSettings):
    # Logging
    LOGFILE_NAME: str = "helikite.log"
    LOGLEVEL_CONSOLE: str = "INFO"
    LOGLEVEL_FILE: str = "DEBUG"
    LOGFORMAT_CONSOLE: logging.Formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-7.7s] %(message)s"
    )
    LOGFORMAT_FILE = logging.Formatter(
        "%(asctime)s [%(levelname)-7.7s] (%(name)25.25s) %(message)s"
    )


class Credentials(BaseSettings):
    # User tokens
    SCIHUB_USERNAME: str | None = None
    SCIHUB_PASSWORD: str | None = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


constants = Constants()
credentials = Credentials()
