"""
Get details for all shares.
"""

from sqlalchemy import select

from src.core import Share, get_session


def get() -> list:
    """Get details for all shares, returns a JSON-formatted array of objects."""
    statement = select(Share)

    with get_session() as sess:
        result = sess.execute(statement)
        rows = result.fetchall()

    return [
        {key: row[0].__dict__[key] for key in row[0].__dataclass_fields__.keys()}
        for row in rows
    ]
