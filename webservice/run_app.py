#!/usr/bin/env python
"""
Main Flask python function that manages the server backend

If you just want to try it out, just run this file and connect to
http://localhost:5000 from a browser. Otherwise, read the instructions
in README_DEPLOY.md to deploy on a Apache server.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

import flask
import os

from web_module import (ReverseProxied, static_bp, user_static_bp, get_secret_key, get_config)
from conf import (FlaskRedirectException, ConfigurationError, static_folder)

# This (undocumented) flag changes the style of the webpage (CSS, etc.)
# and decides whether some of the headers (e.g. the App title) and the
# description of what app can do should appear or not
#
# Options:
# - 'lite': simple version, not title, no info description, different CSS
# - anything else: default
#
# How to pass: with Apache, when forwarding, in a ReverseProxy section, add
#   RequestHeader set X-App-Style lite
def get_style_version(request):
    return request.environ.get("HTTP_X_APP_STYLE", "")

import logging, logging.handlers
logger = logging.getLogger("tools-app")

logHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(
        os.path.split(os.path.realpath(__file__))[0], 'logs', 'requests.log'),
    when='midnight')
formatter = logging.Formatter(
    '[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

## Create the app
app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = get_secret_key()

def get_visualizer_select_template(request):
    if get_style_version(request) == 'lite':
        return 'visualizer_select_lite.html'
    else:
        return 'visualizer_select.html'

@app.route('/')
def input_data():
    """
    Main view, input data selection and upload
    """
    return flask.render_template(get_visualizer_select_template(flask.request), **get_config())

# Register blueprints
app.register_blueprint(static_bp)
app.register_blueprint(user_static_bp)

try:
    from compute import blueprint
    app.register_blueprint(blueprint)
except ImportError:
    logger.warning("NOTE: could not import the 'compute' module with custom functions")

if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of app, not the installed one
    app.use_x_sendfile = False
    app.run(debug=True)
