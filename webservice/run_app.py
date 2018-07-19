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

import datetime
import flask
import os
import yaml

from web_module import (FlaskRedirectException, process_data_core)

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
logger = logging.getLogger("server")

logHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(
        os.path.split(os.path.realpath(__file__))[0], 'logs', 'requests.log'),
    when='midnight')
formatter = logging.Formatter(
    '[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

class ConfigurationError(Exception):
    pass

if __name__ == "__main__":
    # If run manually (=> debug/development mode),
    # use the local version of app, not the installed one
    import sys
    sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.pardir))


static_folder = os.path.join(
    os.path.split(os.path.realpath(__file__))[0], 'static')
view_folder = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'view')
config_file_path = os.path.join(static_folder, "config.yaml")

app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
directory = os.path.split(os.path.realpath(__file__))[0]
try:
    with open(os.path.join(directory, 'SECRET_KEY')) as f:
        app.secret_key = f.readlines()[0].strip()
        if len(app.secret_key) < 16:
            raise ValueError
except Exception:
    raise ConfigurationError(
        "Please create a SECRET_KEY file in {} with a random string "
        "of at least 16 characters".format(directory))


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
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
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_HOST', '')
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)

def parse_config(config):
    default_templates_folder = 'default_templates'
    user_templates_folder = 'user_templates'
    retdict = {}

    templates = config.get('templates', {})

    known_templates = ['how_to_cite', 'about']

    for template_name in known_templates:
        # Note that this still allows to set it to None explicitly to skip this section
        try:
            retdict[template_name] = templates[template_name]
            if retdict[template_name] is not None:
                retdict[template_name] = os.path.join(user_templates_folder, retdict[template_name])
        except KeyError:
            retdict[template_name] = os.path.join(default_templates_folder, '{}.html'.format(template_name))

    for template_name in templates:
        if template_name not in known_templates and templates[template_name] is not None:
            retdict[template_name] = os.path.join(user_templates_folder, templates[template_name])


    return retdict

def get_config():
    with open(config_file_path) as config_file:
        config = yaml.load(config_file)
    return {
        'config': config,
        'include_pages': parse_config(config)
    }


def get_visualizer_select_template(request):
    if get_style_version(request) == 'lite':
        return 'visualizer_select_lite.html'
    else:
        return 'visualizer_select.html'


def get_visualizer_template(request):
    if get_style_version(request) == 'lite':
        return 'visualizer_lite.html'
    else:
        return 'visualizer.html'


logger.debug("Start")

# From http://arusahni.net/blog/2014/03/flask-nocache.html
## Add @nocache right between @app.route and the 'def' line
from functools import wraps, update_wrapper


def nocache(view):

    @wraps(view)
    def no_cache(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.datetime.now()
        response.headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


@app.route('/')
def index():
    """
    Main view, redirect to input_data
    """
    return flask.redirect(flask.url_for('input_data'))


@app.route('/termsofuse/')
def termsofuse():
    """
    View for the terms of use
    """
    return flask.send_from_directory(view_folder, 'termsofuse.html')


@app.route('/input/')
def input_data():
    """
    Input structure selection
    """
    return flask.render_template(get_visualizer_select_template(flask.request), **get_config())


@app.route('/static/js/<path:path>')
def send_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'js'), path)

@app.route('/static/js/custom/<path:path>')
def send_custom_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'js', 'custom'), path)

@app.route('/static/img/<path:path>')
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'img'), path)


@app.route('/static/css/<path:path>')
def send_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'css'), path)


@app.route('/static/css/custom/<path:path>')
def send_custom_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'css', 'custom'), path)


@app.route('/static/css/images/<path:path>')
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(
        os.path.join(static_folder, 'css', 'images'), path)


@app.route('/static/fonts/<path:path>')
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'fonts'), path)


@app.route('/process_data/', methods=['GET', 'POST'])
def process_data():
    """
    Process data (uploaded from POST request)
    """
    if flask.request.method == 'POST':
        try:
            data_for_template = process_data_core(
                module_version="",
                call_source="process_data",
                logger=logger,
                flask_request=flask.request)
            config_dict = get_config()
            return flask.render_template(
                get_visualizer_template(flask.request), config=config_dict['config'], **data_for_template)
        except FlaskRedirectException as e:
            flask.flash(str(e))
            return flask.redirect(flask.url_for('input_data'))
        except Exception:
            flask.flash("Unable to process the data, sorry...")
            return flask.redirect(flask.url_for('input_data'))

    else:  # GET Request
        return flask.redirect(flask.url_for('input_data'))


@app.route('/process_example_data/', methods=['GET', 'POST'])
def process_example_data():
    """
    Process an example data file (example name from POST request)
    """
    if flask.request.method == 'POST':
        try:
            data_for_template = process_data_core(
                module_version="",
                call_source="process_example_data",
                logger=logger,
                flask_request=flask.request)
            return flask.render_template(
                get_visualizer_template(flask.request), config=config, **data_for_template)
        except FlaskRedirectException as e:
            flask.flash(str(e))
            return flask.redirect(flask.url_for('input_data'))

    else:  # GET Request
        return flask.redirect(flask.url_for('input_data'))


if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of app, not the installed one
    app.use_x_sendfile = False
    app.run(debug=True)
