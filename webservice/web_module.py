# -*- coding: utf-8 -*-
"""
Most of the functions needed by the web service are here.
In run_app.py we just keep the main web logic.
"""
import datetime
import json
import os

import yaml
from conf import ConfigurationError, __version__, config_file_path, directory


def get_secret_key():
    """Attempt to read secret key from file
    SECRET_KEY"""
    try:
        with open(os.path.join(directory, "SECRET_KEY")) as f:
            secret_key = f.readlines()[0].strip()
            if len(secret_key) < 16:
                raise ValueError
            return secret_key
    except Exception as excep:
        raise ConfigurationError(
            "Please create a SECRET_KEY file in {} with a random string "
            "of at least 16 characters".format(directory)
        ) from excep


def parse_config(config):
    retdict = {}

    templates = config.get("templates", {})

    known_templates = [
        "how_to_cite",
        "about",
        "select_content",
        "upload_structure_additional_content",
    ]

    for template_name in known_templates:
        retdict[template_name] = templates[template_name]

    additional_accordion_entries = config.get("additional_accordion_entries", [])
    retdict["additional_accordion_entries"] = []
    for accordian_entry in additional_accordion_entries:
        retdict["additional_accordion_entries"].append(
            {
                "header": accordian_entry["header"],
                "template_page": os.path.join(accordian_entry["template_page"]),
            }
        )

    return retdict


def set_config_defaults(config):
    """Add defaults so the site works"""
    new_config = config.copy()

    new_config.setdefault("window_title", "Materials Cloud Tool")
    new_config.setdefault(
        "page_title",
        "<PLEASE SPECIFY A PAGE_TITLE AND A WINDOW_TITLE IN THE CONFIG FILE>",
    )

    new_config.setdefault("custom_css_files", {})
    new_config.setdefault("custom_js_files", {})
    new_config.setdefault("templates", {})

    return new_config


def get_config():
    try:
        with open(config_file_path) as config_file:
            config = yaml.safe_load(config_file)
            config["version"] = __version__
    except Exception as exc:

        config = {}
        config["version"] = __version__

    # set defaults
    config = set_config_defaults(config)

    return {"config": config, "include_pages": parse_config(config)}


def logme(logger, *args, **kwargs):
    """
    Log information on the passed logger.

    See docstring of generate_log for more info on the
    accepted kwargs.

    :param logger: a valid logger. If you pass `None`, no log is output.
    """
    if logger is not None:
        logger.debug(generate_log(*args, **kwargs))


def generate_log(filecontent, fileformat, request, call_source, reason, extra={}):
    """
    Given a string with the file content, a file format, a Flask request and
    a string identifying the reason for logging, stores the
    correct logs.

    :param filecontent: a string with the file content
    :param fileformat: string with the file format
    :param request: a Flask request
    :param call_source: a string identifying who called the function
    :param reason: a string identifying the reason for this log
    :param extra: additional data to add to the logged dictionary.
        NOTE! it must be JSON-serializable
    """
    # I don't know the fileformat
    data = {"filecontent": filecontent, "fileformat": fileformat}

    logdict = {
        "data": data,
        "reason": reason,
        "request": str(request.headers),
        "call_source": call_source,
        "source": request.headers.get("X-Forwarded-For", request.remote_addr),
        "time": datetime.datetime.now().isoformat(),
    }
    logdict.update(extra)
    return json.dumps(logdict)


class ReverseProxied:
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    Inspired by  http://flask.pocoo.org/snippets/35/

    In apache: use the following reverse proxy (adapt where needed)
    <Location /proxied>
      ProxyPass http://localhost:4444/
      ProxyPassReverse http://localhost:4444/
      RequestHeader set X-Script-Name /proxied
      RequestHeader set X-Scheme http
    </Location>

    :param app: the WSGI application
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]

        scheme = environ.get("HTTP_X_SCHEME", "")
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_HOST", "")
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)
