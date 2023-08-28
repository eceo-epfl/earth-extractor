import logging
from earth_extractor import core
import os


def setup_file_logger(output_folder):
    # Add a file logger

    # Create folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    logfile_handler = logging.FileHandler(
        os.path.join(output_folder, core.constants.LOGFILE_NAME)
    )
    logfile_handler.setLevel(core.constants.LOGLEVEL_FILE)
    logfile_handler.setFormatter(core.constants.LOGFORMAT_FILE)
    logging.getLogger().addHandler(logfile_handler)


class ErrorFlagHandler(logging.Handler):
    """Catches ERRORs to allow app to know if an error occurred at exit"""

    def __init__(self):
        super().__init__()
        self.errors = 0

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors += 1

    def print_status(self):
        if self.errors > 0:
            print()
            print(
                f"There {'were' if self.errors > 1 else 'was'} {self.errors} "
                f"error{'s' if self.errors > 1 else ''} during the "
                "execution of the app. Please check the error log file "
                f"'{core.config.constants.LOGFILE_NAME}' for more details."
            )
