"""
Most of the functions needed by the web service are here. 
In run_app.py we just keep the main web logic.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import str

import datetime
import json
import os
from functools import wraps, update_wrapper

import yaml
import flask
from flask import Blueprint

from conf import directory, static_folder, user_static_folder, config_file_path, ConfigurationError

def get_secret_key():
    try:
        with open(os.path.join(directory, 'SECRET_KEY')) as f:
            secret_key = f.readlines()[0].strip()
            if len(secret_key) < 16:
                raise ValueError
            return secret_key
    except Exception:
        raise ConfigurationError(
            "Please create a SECRET_KEY file in {} with a random string "
            "of at least 16 characters".format(directory))


def parse_config(config):
    default_templates_folder = 'default_templates'
    user_templates_folder = 'user_templates'
    retdict = {}

    templates = config.get('templates', {})

    known_templates = ['how_to_cite', 'about', 'select_content']

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

    additional_accordion_entries = config.get('additional_accordion_entries', [])
    retdict['additional_accordion_entries'] = []
    for accordian_entry in additional_accordion_entries:
        retdict['additional_accordion_entries'].append({
            "header": accordian_entry["header"],
            "template_page": os.path.join(user_templates_folder, accordian_entry["template_page"])
        })

    return retdict

def set_config_defaults(config):
    """Add defaults so the site works"""
    new_config = config.copy()

    new_config.setdefault('window_title', "Materials Cloud Tool")
    new_config.setdefault('page_title', "<PLEASE SPECIFY A PAGE_TITLE AND A WINDOW_TITLE IN THE CONFIG FILE>")

    new_config.setdefault('custom_css_files', {})
    new_config.setdefault('custom_js_files', {})
    new_config.setdefault('templates', {})

    return new_config


def get_config():
    try:
        with open(config_file_path) as config_file:
            config = yaml.load(config_file)
    except IOError as exc:
        if exc.errno == 2: # No such file or directory
            config = {}
        else:
            raise

    #set defaults
    config = set_config_defaults(config)

    return {
        'config': config,
        'include_pages': parse_config(config)
    }

def nocache(view):
    """Add @nocache right between @app.route and the 'def' line.
    From http://arusahni.net/blog/2014/03/flask-nocache.html"""
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


def logme(logger, *args, **kwargs):
    """
    Log information on the passed logger. 

    See docstring of generate_log for more info on the
    accepted kwargs.

    :param logger: a valid logger. If you pass `None`, no log is output.
    """
    if logger is not None:
        logger.debug(generate_log(*args, **kwargs))


def generate_log(filecontent,
                 fileformat,
                 request,
                 call_source,
                 reason,
                 extra={}):
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
    data = {'filecontent': filecontent, 'fileformat': fileformat}

    logdict = {
        'data': data,
        'reason': reason,
        'request': str(request.headers),
        'call_source': call_source,
        'source': request.headers.get('X-Forwarded-For', request.remote_addr),
        'time': datetime.datetime.now().isoformat()
    }
    logdict.update(extra)
    return json.dumps(logdict)

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

static_bp = Blueprint('static', __name__, url_prefix='/static')
user_static_bp = Blueprint('user_static', __name__, url_prefix='/user_static')

@static_bp.route('/js/<path:path>')
def send_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'js'), path)

@user_static_bp.route('/js/<path:path>')
def send_custom_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, 'js'), path)

@static_bp.route('/img/<path:path>')
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'img'), path)

@user_static_bp.route('/img/<path:path>')
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, 'img'), path)


@static_bp.route('/css/<path:path>')
def send_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'css'), path)


@user_static_bp.route('/css/<path:path>')
def send_custom_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, 'css'), path)


@static_bp.route('/css/images/<path:path>')
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(
        os.path.join(static_folder, 'css', 'images'), path)

@user_static_bp.route('/css/images/<path:path>')
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(
        os.path.join(user_static_folder, 'css', 'images'), path)


@static_bp.route('/fonts/<path:path>')
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(static_folder, 'fonts'), path)


@user_static_bp.route('/fonts/<path:path>')
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(user_static_folder, 'fonts'), path)
