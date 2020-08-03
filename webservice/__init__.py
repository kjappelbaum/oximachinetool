# -*- coding: utf-8 -*-
import flask
import joblib

from conf import FlaskRedirectException, static_folder, view_folder
from web_module import ReverseProxied, get_config, get_secret_key, logme

MODEL = joblib.load(os.path.join(THIS_DIR, 'compute', 'votingclassifier.joblib'))
SCALER = joblib.load(os.path.join(THIS_DIR, 'compute', 'scaler_0.joblib'))
EXPLAINER = joblib.load(os.path.join(THIS_DIR, 'compute', 'explainer.joblib'))
KDTREE = joblib.load(os.path.join(THIS_DIR, 'compute', 'kd_tree.joblib'))
NAMES = np.array(read_pickle(os.path.join(THIS_DIR, 'compute', 'names.pkl')))
TRAIN_DATA = np.load(os.path.join(THIS_DIR, 'features.npy'))

app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = get_secret_key()
