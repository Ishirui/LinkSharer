"""
Main endpoint for downloading the contents of a share
"""

import logging
from uuid import UUID

from flask import Response, abort, send_file

from src.core import Share, get_session


def get(share_id: str) -> Response:
    """Download the file identified by the share ID"""

    try:
        share_uuid = UUID(share_id)
    except ValueError:
        logging.error("Tried to access invalid UUID '%s' !", share_id)
        abort(400)

    with get_session() as sess:
        share = sess.get(Share, share_uuid)

        if share is None:
            logging.error("Requested UUID '%s' not found !", share_uuid)
            abort(404)

        share_path = (
            share.path
        )  # Extract this before closing the session and share goes detached

    # TODO: SECURITY HOLE ! Need to use send_from_directory and use relative paths instead
    # This could make Flask send system/config files from the docker container
    return send_file(share_path, as_attachment=True)
