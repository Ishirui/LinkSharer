"""
Dynamically register endpoints based on filenames in api/
"""

import importlib.util
import logging
from inspect import _empty, signature
from pathlib import Path
from typing import Callable, Set, TypedDict

from flask import Flask

# Globals
ALLOWED_ENDPOINT_FUNCTION_NAMES = {"post", "get"}


# Classes
class InvalidEndpointMethodException(Exception):
    def __init__(self, endpoint_method: Callable, message: str):
        msg = f"Method '{endpoint_method.__qualname__}' is not a valid endpoint method:\n {message}"
        super().__init__(msg)


class EndpointDetails(TypedDict):
    url: str
    id: str
    params: Set[str]


# Helper functions
def parse_endpoint_path(path: Path) -> EndpointDetails:
    """
    Get a slash-separated endpoint URL segment from a file path. Also return some extra parameters.
    Any folders whose names start with an underscore will be considered as parameters.

    For example, a file path of 'src/api/share/_share_id/get.py' will yield the following endpoint URL segment:
        > '/api/share/<share_id>/get'

    Parameters
    ----------
    path : Path
        File path of the endpoint file for which to get the URL segment.

    Returns
    ----------
    endpoint_details : EndpointDetails
        TypedDict containing:
            - "url": URL segment for the endpoint as defined above.
            - "id": Unique endpoint ID for this endpoint
            - "params": Parameters used in this endpoint
    """

    endpoints_dir_path = Path(__file__).parent.joinpath("endpoints")

    # Convert to absolute just to be sure and remove suffix (.py)
    path_abs = path.absolute().with_suffix("")

    # Get the path as a subdir of the src/api directory
    try:
        api_rel_path = path_abs.relative_to(endpoints_dir_path)
    except ValueError:
        logging.warning(
            "Could not get path relative to 'src/api/endpoints/' for file '%s' ! Using path '%s'",
            str(path_abs),
            str(path),
        )
        api_rel_path = path

    # Construct URL and ID, storing all endpoint parameters along the way
    endpoint_url_segment = "/api/"
    endpoint_parameters = set()
    endpoint_id = ""

    for part in api_rel_path.parts:
        if part.startswith("_"):
            # Handle parameter-like segments
            part = part[1:]
            endpoint_url_segment += f"<{part}>/"
            endpoint_parameters.add(part)
        else:
            endpoint_url_segment += f"{part}/"

        endpoint_id += f"{part}_"

    logging.info(
        "Endpoint URL segment '%s' obtained from file '%s'. Detected the following parameters: %s",
        endpoint_url_segment,
        path,
        endpoint_parameters,
    )

    return EndpointDetails(
        url=endpoint_url_segment, id=endpoint_id, params=endpoint_parameters
    )


def verify_method_sig(method: Callable, endpoint_params: Set[str]) -> None:
    """Verify that a method's signature is valid for use in the corresponding endpoint"""

    sig = signature(method)

    # Get method's parameters
    method_args = sig.parameters

    # Check all parameters defined by the endpoint are accepted by the method
    if not endpoint_params.issubset(method_args):
        extra_params = endpoint_params.difference(method_args)
        raise InvalidEndpointMethodException(
            method,
            f"Endpoint defines the following params which the method does not accept: {extra_params}",
        )

    # Check all method arguments not passed by the endpoint have a default value
    nondefault_method_args = {
        param_name for param_name, param in method_args.items() if not param.default
    }
    missing_endpoint_params = nondefault_method_args.difference(endpoint_params)
    if missing_endpoint_params:
        raise InvalidEndpointMethodException(
            method,
            f"Method defines the following required args not specified by the endpoint URL: {missing_endpoint_params}",
        )

    # Check all arguments passed by the endpoint have a type hint of 'str' or no type hint
    for param_name in endpoint_params:
        method_arg = method_args[param_name]
        annotation = method_arg.annotation
        if annotation in (_empty, str):
            continue

        raise InvalidEndpointMethodException(
            method,
            f"Wrong type hint ('{annotation}') defined by method argument '{param_name}' ! Should be 'str'.",
        )


def register_endpoint(
    app: Flask, method: Callable, endpoint_details: EndpointDetails
) -> None:
    """Register `method` as the function called by the endpoint `endpoint_url`"""

    endpoint_url = endpoint_details["url"]
    endpoint_id = endpoint_details["id"] + method.__name__
    endpoint_params = endpoint_details["params"]

    verify_method_sig(method, endpoint_params)

    # Get allowed methods based on the method name
    match method.__name__:
        case "post":
            allowed_methods = ["POST"]

        case "get":
            allowed_methods = ["GET"]

        case _:
            logging.warning(
                "No HTTP method defined for endpoint method named %s. Registering as 'GET'-only.",
                method.__name__,
            )

    logging.info(
        "Registering endpoint '%s' with methods %s at URL %s.",
        endpoint_id,
        allowed_methods,
        endpoint_url,
    )
    app.add_url_rule(
        endpoint_url, view_func=method, endpoint=endpoint_id, methods=allowed_methods
    )


# Main method
def register_all_endpoints(app: Flask) -> None:
    """Register all endpoints defined in .py files under src/api/endpoints"""

    logging.info("Starting endpoint registration.")
    endpoints_dir_path = Path(__file__).parent.joinpath("endpoints")
    for directory, _, files in endpoints_dir_path.walk():
        for file_str in files:
            file = directory.joinpath(file_str)

            logging.debug("Inspecting file %s", file)

            if file.suffix != ".py":
                continue

            endpoint_details = parse_endpoint_path(file)

            # Dynamically load each endpoint module and extract the endpoint functions
            module_spec = importlib.util.spec_from_file_location(
                "endpoint_module", file
            )
            assert module_spec

            endpoint_module = importlib.util.module_from_spec(module_spec)
            loader = module_spec.loader
            assert loader

            loader.exec_module(endpoint_module)
            for function_name in ALLOWED_ENDPOINT_FUNCTION_NAMES:
                try:
                    endpoint_function = getattr(endpoint_module, function_name)
                except AttributeError:
                    continue

                try:
                    register_endpoint(app, endpoint_function, endpoint_details)
                except InvalidEndpointMethodException as exc:
                    logging.error(
                        "Failed to register endpoint '%s' in file '%s'. Skipping. %s",
                        endpoint_details["id"],
                        file,
                        exc,
                    )

    logging.info("Endpoint registration finished.")
