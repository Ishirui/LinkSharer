"""Create links for easy file sharing."""

import logging

from flask import Flask

from .api import register_all_endpoints
from .core import init_db

app = Flask(__name__)
logging.getLogger().setLevel("DEBUG")
init_db()
register_all_endpoints(app)

# TODO: Clean this up
