from pydantic import BaseSettings
import logging
import os


class Constants(BaseSettings):
    DEFAULT_DOWNLOAD_DIR: str = os.path.join(os.getcwd(), 'data')

    KEYRING_ID: str = "earth-extractor"
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


constants = Constants()
