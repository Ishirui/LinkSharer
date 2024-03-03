"""Helper function for interfacing with the database"""

# Imports
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from .config import DATA_PATH, DEBUG
from .share import Base

# Globals
DB_ENGINE: Engine


# Helper functions
def init_db():
    engine = create_engine(f"sqlite+pysqlite:///{DATA_PATH}/linksharer.db", echo=DEBUG)
    Base.metadata.create_all(engine)

    global DB_ENGINE  # pylint: disable=global-statement
    DB_ENGINE = engine


def get_session() -> Session:
    if not DB_ENGINE:
        init_db()

    return Session(DB_ENGINE)
