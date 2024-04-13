"""
Endpoint for creating a new share.
TODO: Secure this !!!
"""

import logging
from pathlib import Path
from uuid import UUID

from flask import abort, request

from src.core import Share, get_session


def create_share(share_path: Path) -> UUID:
    """
    Create a new share pointing to this path with a randomly-assigned UUID.
    Currently only file shares are supported.
    """
    if not share_path.exists():
        raise FileNotFoundError(share_path)

    if not share_path.is_file():
        raise ValueError(
            f"Only single-file shares are supported. {share_path!s} is not a file !"
        )

    # TODO: Add methods for setting name and expiry
    share = Share(_path_str=str(share_path.resolve()), expiry=None, name=None)
    share_id = share.id

    with get_session() as sess:
        sess.add(share)
        sess.commit()

    logging.info(
        "Successfully created share '%s', pointing to '%s'",
        share_id,
        share_path.absolute(),
    )
    return share_id


def post():
    """Create a new share pointing to the path specified in the HTTP form."""
    try:
        share_path = request.form["share_path"]
    except KeyError:
        logging.error("'share_path' field not present in request.")
        abort(400)

    path = Path(share_path)

    try:
        share_id = create_share(path)
    except (FileNotFoundError, ValueError) as exc:
        logging.error("Could not create share: %s", exc)
        abort(400)

    return f"""
        <h1>Success !</h1>
        <p>The share was created successfully.</p>
        <p>Path: {path.absolute()!s}<br>ID: {share_id}</p>
    """
