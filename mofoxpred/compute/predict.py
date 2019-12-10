import os
from glob import glob
from pathlib import Path
from collections import defaultdict
from functools import partial
import concurrent.futures
import warnings

warnings.simplefilter("ignore")
import numpy as np
from numeral import int2roman

from pymatgen import Structure
from mine_mof_oxstate.featurize import GetFeatures, FeatureCollector
from joblib import load
from .utils import string_to_pymatgen


# adjust these features according to model 
FEATURES = [
    "crystal_nn_no_steinhardt",
    "column_differences",
    "electronegativity_differences",
    "valence_differences",
    "unfilled_differences",
    "nsvalence_differences",
    "row",
    "column",
    "valenceelectrons",
    "diffto18electrons",
    "sunfilled",
    "punfilled",
    "dunfilled",
]


def prediction(feature_dict: dict, structures: dict):
    """
    
    Arguments:
        feature_dict {dict} -- dictionary of features
        structures {[type]} -- dictionary of structure
    
    Returns:
        [type] -- [description]
    """
    model = load("model/votingclassifier.joblib")
    scaler = load("model/scaler.joblib")

    prediction_dict = defaultdict(dict)

    # Iterate of the structure and get the indices of the sites
    # Create a prediction dictionary with the prediction, feature vector and the probabilities
    try:
        for key in list(structures.keys()):
            structure = string_to_pymatgen(structures[key]["content"])
            coords = structure.cart_coords
            name = key.replace(".cif", "")
            for site in feature_dict[name]:
                coordssite = np.array(
                    [site["coordinate_x"], site["coordinate_y"], site["coordinate_z"]]
                )
                index = np.argmin(np.sum(np.abs(coords - coordssite), axis=-1))
                feature = FeatureCollector._select_features(
                    FEATURES, np.array([site["feature"]])
                )
                prediction_dict[name][index] = {}
                transformed_feature = scaler.transform(feature)
                prediction_dict[name][index]["feature"] = transformed_feature
                predicted_probas = model.predict_proba(transformed_feature)
                prediction = model.classes[np.argmax(predicted_probas)]

                prediction_string = (
                    "{}".format(index)
                    + str(structure[index].specie)
                    + "({})".format(int2roman(prediction, only_ascii=True))
                )
                prediction_dict[name][index]["prediction"] = prediction_string
                if model.voting == "soft":
                    prediction_dict[name][index]["probability"] = round(
                        np.max(predicted_probas) * 100
                    )
                else:
                    prediction_dict[name][index]["probability"] = np.nan
    except KeyError as e:
        print(e)

    prediction_dict = dict(prediction_dict)
    return prediction_dict
