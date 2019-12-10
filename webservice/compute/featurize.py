from joblib import load
from mine_mof_oxstate.featurize import GetFeatures, FeatureCollector
from pymatgen import Structure
from numeral import int2roman
import numpy as np
import os
from glob import glob
from pathlib import Path
from collections import defaultdict
from functools import partial
import concurrent.futures
import warnings
from .predict import FEATURES

warnings.simplefilter("ignore")


def _featurize_single(structure, feature_dir: str = ""):
    """[summary]

    Arguments:
        structure {pymatgen Structe} -- (name of structure, string with structure)
        feature_dir {str} -- output directory for features
    """
    gf = GetFeatures(structure, feature_dir)
    features = gf.return_features()
    metal_indices = gf.metal_indices
    X = []
    rl = FeatureCollector.create_dict_for_feature_table_from_dict(features)
    for f in rl:
        X.append(f["feature"])
    X = np.vstack(X)
    X, names = FeatureCollector._select_features_return_names(FEATURES, X)
    metals = [site.species_string for site in gf.metal_sites]
    feature_value_dict = {}
    for i, site in enumerate(X):
        feature_value_dict[metals[i] + "_" + str(i)] = dict(zip(names, site))
    return X, feature_value_dict, metal_indices


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass
