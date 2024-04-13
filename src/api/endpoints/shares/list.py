"""
List all existing shares. Returns a JSON array of share UUIDs.
"""

from typing import List
from uuid import UUID

from sqlalchemy import select

from src.core import Share, get_session


def get() -> List[UUID]:
    """List all existing shares, returns a JSON array."""

    statement = select(Share.id)

    with get_session() as sess:
        result = sess.execute(statement)

    return [row[0] for row in result.fetchall()]
