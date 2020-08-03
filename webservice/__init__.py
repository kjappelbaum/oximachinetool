# -*- coding: utf-8 -*-

import flask
from conf import FlaskRedirectException, static_folder, view_folder
from web_module import ReverseProxied, get_config, get_secret_key, logme



app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = get_secret_key()
