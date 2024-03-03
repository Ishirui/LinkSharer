"""Create links for easy file sharing."""

import logging
from pathlib import Path
from uuid import UUID

from flask import Flask, Response, abort, request, send_file

from core import Share, get_session, init_db

app = Flask(__name__)
init_db()


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


@app.route("/share/<share_id_str>", methods=["GET"])
def download_endpoint(share_id_str: str) -> Response:
    """Download the file identified by the share ID"""

    try:
        share_id = UUID(share_id_str)
    except ValueError:
        logging.error("Tried to access invalid UUID '%s' !", share_id_str)
        abort(400)

    with get_session() as sess:
        share = sess.get(Share, share_id)

        if share is None:
            logging.error("Requested UUID '%s' not found !", share_id)
            abort(404)

        share_path = (
            share.path
        )  # Extract this before closing the session and share goes detached

    # TODO: SECURITY HOLE ! Need to use send_from_directory and use relative paths instead
    # This could make Flask send system/config files from the docker container
    return send_file(share_path, as_attachment=True)


@app.route("/new", methods=["POST"])
def create_share_endpoint():
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


# TODO: Clean this up
logging.getLogger().setLevel("DEBUG")
