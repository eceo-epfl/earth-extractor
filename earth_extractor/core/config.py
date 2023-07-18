from pydantic import BaseSettings
import logging
import os
import datetime


class Constants(BaseSettings):
    COMMON_TIMESTAMP: str = f"{datetime.datetime.utcnow().isoformat()}"
    DEFAULT_DOWNLOAD_DIR: str = os.path.join(os.getcwd(), 'data')
    GEOJSON_EXPORT_FILENAME: str = f"{COMMON_TIMESTAMP}.geojson"
    MAX_DOWNLOAD_ATTEMPTS: int = 50
    HIDE_PASSWORD_PROMPT: bool = True

    PARRALLEL_PROCESSES_DEFAULT: int = 4

    KEYRING_ID: str = "earth-extractor"

    # Logging
    LOGLEVEL_MODULE_DEFAULT: int = logging.DEBUG
    LOGFILE_NAME: str = f"{COMMON_TIMESTAMP}.log"
    LOGLEVEL_FILE: int = logging.DEBUG
    LOGLEVEL_CONSOLE: int = logging.INFO
    LOGFORMAT_CONSOLE: logging.Formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-7.7s] %(message)s"
    )
    LOGFORMAT_FILE = logging.Formatter(
        "%(asctime)s [%(levelname)-7.7s] (%(name)25.25s) %(message)s"
    )


constants = Constants()
