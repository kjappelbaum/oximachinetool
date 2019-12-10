import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
from glob import glob
from pathlib import Path
from collections import defaultdict
from functools import partial
import concurrent.futures
import warnings

warnings.simplefilter("ignore")
import numpy as np
from numeral import int2roman
import joblib

from pymatgen import Structure
from mine_mof_oxstate.featurize import GetFeatures, FeatureCollector
from joblib import load
from .utils import string_to_pymatgen

from learnmofox import utils
import sys

sys.modules["utils"] = utils

# adjust these features according to model
METAL_CENTER_FEATURES = [
    "column",
    "row",
    "valenceelectrons",
    "diffto18electrons",
    "sunfilled",
    "punfilled",
    "dunfilled",
]
GEOMETRY_FEATURES = ["crystal_nn_fingerprint", "behler_parinello"]
CHEMISTRY_FEATURES = ["local_property_stats"]
FEATURES = CHEMISTRY_FEATURES + METAL_CENTER_FEATURES + ["crystal_nn_no_steinhardt"]


MODEL = joblib.load(os.path.join(THIS_DIR, "votingclassifier.joblib"))
SCALER = joblib.load(os.path.join(THIS_DIR, "scaler_0.joblib"))


def predictions(X, site_names):
    X_scaled = SCALER.transform(X)
    prediction = MODEL.predict(X_scaled)

    max_probas = np.max(MODEL.predict_proba(X_scaled), axis=1)
    base_predictions = MODEL._predict(X_scaled)

    print(prediction, site_names, max_probas, base_predictions)
    prediction_output = []
    for i, pred in enumerate(prediction):
        prediction_output.append(
            [
                site_names[i],
                int2roman(pred),
                max_probas[i],
                [int2roman(MODEL.classes[i]) for i in base_predictions[i]],
            ],
        )
    return prediction_output
