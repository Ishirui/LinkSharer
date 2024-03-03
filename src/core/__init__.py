"""Core functionality for linksharer: database management, model definitions, app config..."""

from .db import get_session, init_db
from .share import Share
