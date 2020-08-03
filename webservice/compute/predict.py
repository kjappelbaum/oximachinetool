# -*- coding: utf-8 -*-
import logging
import os
import sys
import warnings

import joblib
import numpy as np
import shap
from numeral import int2roman
from pymatgen import Structure

import oximachinerunner.learnmofox as learnmofox
from oximachine_featurizer.featurize import FeatureCollector, GetFeatures
from oximachinerunner.utils import read_pickle
from webservice import EXPLAINER, KDTREE, MODEL, NAMES, SCALER

from .utils import generate_csd_link, string_to_pymatgen

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

warnings.simplefilter('ignore')

log = logging.getLogger('shap')
log.setLevel(logging.ERROR)

sys.modules['learnmofox'] = learnmofox

# adjust these features according to model
METAL_CENTER_FEATURES = [
    'column',
    'row',
    'valenceelectrons',
    'diffto18electrons',
    'sunfilled',
    'punfilled',
    'dunfilled',
]
GEOMETRY_FEATURES = ['crystal_nn_fingerprint', 'behler_parinello']
CHEMISTRY_FEATURES = ['local_property_stats']
FEATURES = CHEMISTRY_FEATURES + METAL_CENTER_FEATURES + ['crystal_nn_no_steinhardt']

NEAREST_NEIGHBORS = 4


def get_nearest_neighbors(X: np.array) -> list:
    """Get list of links to closest structures in the training set.
    For this we query a KD-Tree that is built using the scaled training data
    with a Euclidean distance metric and return the NEAREST_NEIGHBORS closest
    structures from the training set. This is an additional way to understand
    if the predictions can be trusted. Note that Euclidean distance between
    structures in feature space does not necessarily mean that the resulting
    nearest neighbors are the nearest neighbors a chemists would have intuitively
    chosen.

    Args:
        X (np.array): unscaled feature array

    Returns:
        list: list of links to the CSD, each element of the list will be a string with NEAREST_NEIGBORS
            html links to the WEBCSD.
    """
    link_list = []
    X = SCALER.transform(X)
    for metal_center in X:
        _, ids = KDTREE.query(metal_center.reshape(1, -1), k=NEAREST_NEIGHBORS)
        names = set([NAMES[i] for i in ids[0]])
        links = ', '.join([generate_csd_link(name) for name in names])
        link_list.append(links)

    return link_list


def get_explanations(
        X: np.array,
        prediction_labels: list,
        class_idx: list,
        feature_names: list,
        approximate: bool = True,
) -> dict:
    """[summary]

    Arguments:
        X {np.array} -- feature matrix, already unscaled (!, to be easier compatible with the current API)
        prediction_labels {list} -- list of keys that will be used for the dictionary
        feature_names {list} -- list of strings containing the feature names

    Keyword Arguments:

    Returns:
        dict -- [description]
    """
    result_dict = {}
    X = SCALER.transform(X)
    shap_values = EXPLAINER.shap_values(X, approximate=approximate, check_additivity=False)
    for i, row in enumerate(X):
        html = shap.force_plot(
            EXPLAINER.expected_value[class_idx[i]],
            shap_values[i][class_idx[i]],
            row,
            feature_names=feature_names,
        )
        html_data = html.data

        result_dict[prediction_labels[i]] = html_data

    return result_dict


def predictions(X, site_names):
    X_scaled = SCALER.transform(X)
    prediction = MODEL.predict(X_scaled)

    max_probas = np.max(MODEL.predict_proba(X_scaled), axis=1)
    base_predictions = MODEL._predict(X_scaled)
    nearest_neighbors = get_nearest_neighbors(X)

    print(prediction, site_names, max_probas, base_predictions)
    prediction_output = []
    for i, pred in enumerate(prediction):
        agreement = ([MODEL.classes[j] for j in base_predictions[i]].count(pred) / len(base_predictions[i]) * 100)
        if agreement > 80:
            bartype = 'progress-bar bg-success'
        elif agreement < 60:
            bartype = 'progress-bar bg-danger'
        else:
            bartype = 'progress-bar bg-warning'
        prediction_output.append([
            site_names[i],
            int2roman(pred),
            max_probas[i],
            ', '.join([int2roman(MODEL.classes[j]) for j in base_predictions[i]]),
            agreement,
            bartype,
            nearest_neighbors[i],
        ],)

    prediction_labels = []
    for i, pred in enumerate(prediction):
        prediction_labels.append('{} ({})'.format(site_names[i], int2roman(pred)))

    class_idx = []

    for pred in prediction:
        class_idx.append(np.argwhere(MODEL.classes == pred)[0][0])
    return prediction_output, prediction_labels, class_idx
