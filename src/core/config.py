"""Parse and load config options for LinkSharer"""

import logging
import os

DEBUG = bool(os.environ.get("DEBUG", ""))


# Logging related
QUIET = False  # TODO: Set this from CLI args or otherwise

LOGLEVEL: int
if DEBUG:
    LOGLEVEL = logging.DEBUG
elif QUIET:
    LOGLEVEL = logging.WARNING
else:
    LOGLEVEL = logging.INFO

# Paths
CONFIG_PATH = os.environ.get("LINKSHARER_CONFIG_PATH", "app/config")
DATA_PATH = os.environ.get("LINKSHARER_DATA_PATH", "app/data")
