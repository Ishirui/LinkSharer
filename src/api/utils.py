"""Various utility functions used in different endpoints"""

from uuid import UUID

from sqlalchemy import select

from src.core import Share, get_session


def get_share_by_id(share_id: str | UUID) -> Share:
    """Get a share object based on its UUID in the database"""
    statement = select(Share).where(Share.id == UUID(share_id))  # type: ignore

    with get_session() as sess:
        result = sess.execute(statement)
        row = result.fetchone()

    assert row
    share: Share = row[0]

    return share
