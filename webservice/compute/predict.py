# -*- coding: utf-8 -*-
"""Functions to run the prediciton and format the output"""
import logging
import os
import warnings
from typing import List

import joblib
import numpy as np
import shap
from numeral import int2roman
from oximachinerunner import OximachineRunner

from .utils import generate_csd_link  # pylint:disable=relative-beyond-top-level
from .utils import (
    load_pickle as read_pickle,  # pylint:disable=relative-beyond-top-level
)

RUNNER = OximachineRunner("mof")
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

EXPLAINER = joblib.load(os.path.join(THIS_DIR, "explainer.joblib"))
KDTREE = joblib.load(os.path.join(THIS_DIR, "kd_tree.joblib"))
NAMES = np.array(read_pickle(os.path.join(THIS_DIR, "names.pkl")))

warnings.simplefilter("ignore")

log = logging.getLogger("shap")  # pylint:disable=invalid-name
log.setLevel(logging.ERROR)


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

NEAREST_NEIGHBORS = 4


def get_nearest_neighbors(X: np.array) -> list:  # pylint:disable=invalid-name
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
        list: list of links to the CSD, each element of the list
            will be a string with NEAREST_NEIGBORS
            html links to the WEBCSD.
    """
    link_list = []
    X = RUNNER.scaler.transform(X)
    for metal_center in X:
        _, ids = KDTREE.query(metal_center.reshape(1, -1), k=NEAREST_NEIGHBORS)
        names = {NAMES[i] for i in ids[0]}
        links = ", ".join([generate_csd_link(name) for name in names])
        link_list.append(links)

    return link_list


def get_explanations(  # pylint:disable=invalid-name
    X: np.array,
    prediction_labels: list,
    class_idx: list,
    feature_names: list,
    approximate: bool = True,
) -> dict:
    """Get SHAP feature importance

    Arguments:
        X (np.array) -- feature matrix, unscaled
        prediction_labels (list) -- list of keys that will be used for the dictionary
        feature_names (list) -- list of strings containing the feature names

    Keyword Arguments:
        approximate (bool) --- If true uses and approximation of the SHAP value.
            Defaults to True

    Returns:
        dict -- Containing the prediction values as keys and HTML data for
            the explainer as values
    """
    result_dict = {}
    X = RUNNER.scaler.transform(X)
    shap_values = EXPLAINER.shap_values(
        X, approximate=approximate, check_additivity=False
    )
    for i, row in enumerate(X):
        html = shap.force_plot(
            EXPLAINER.expected_value[class_idx[i]],
            shap_values[class_idx[i]][i],
            row,
            feature_names=feature_names,
        )
        html_data = html.data

        result_dict[prediction_labels[i]] = html_data

    return result_dict


def predictions(X: np.ndarray, site_names: List[str]):  # pylint:disable=invalid-name
    """Format the predictions"""

    (
        prediction,
        max_probas,
        base_predictions,
    ) = RUNNER._make_predictions(  # pylint:disable=protected-access
        X
    )

    nearest_neighbors = get_nearest_neighbors(X)

    prediction_output = []
    for i, pred in enumerate(prediction):
        agreement = base_predictions[i].count(pred) / len(base_predictions[i]) * 100
        if agreement > 80:
            bartype = "progress-bar bg-success"
        elif agreement < 60:
            bartype = "progress-bar bg-danger"
        else:
            bartype = "progress-bar bg-warning"
        prediction_output.append(
            [
                site_names[i],
                int2roman(pred),
                max_probas[i],
                ", ".join([int2roman(j) for j in base_predictions[i]]),
                agreement,
                bartype,
                nearest_neighbors[i],
            ],
        )

    prediction_labels = []
    for i, pred in enumerate(prediction):
        prediction_labels.append("{} ({})".format(site_names[i], int2roman(pred)))

    class_idx = []

    for pred in prediction:
        class_idx.append(np.argwhere(RUNNER.model.classes == pred)[0][0])
    return prediction_output, prediction_labels, class_idx


def generate_warning(site_names: List[str]) -> str:
    """Given a site name string returns a warning string
    in case the metal is unusual for the training set"""
    dangerous_metals_in_structure = [
        "Ag",
        "Ce",
        "Er",
        "Hg",
        "Nb",
        "Os",
        "Pt",
        "Sn",
        "Yb",
        "Pu",
    ]

    for site_name in site_names:
        if site_name.split()[0] in dangerous_metals_in_structure:
            return "Your structure contains an element that is rare in MOFs. \
                 The prediction might be wrong."

    return ""
