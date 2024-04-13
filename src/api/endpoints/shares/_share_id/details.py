"""
Get details for selected share.
"""

from src.api import get_share_by_id


def get(share_id: str) -> dict:
    """Get details for selected share. Returns a JSON object."""
    share = get_share_by_id(share_id)

    return {key: share.__dict__[key] for key in share.__dataclass_fields__.keys()}
