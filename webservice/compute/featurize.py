import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
from glob import glob
from pathlib import Path
from collections import defaultdict
from functools import partial
import concurrent.futures
import warnings
from numeral import int2roman
import numpy as np
from scipy import stats
from joblib import load
from mine_mof_oxstate.featurize import GetFeatures, FeatureCollector
from pymatgen import Structure
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.cm as cm
from .predict import FEATURES

warnings.simplefilter("ignore")
alph = "abcdefghijlmnopqrstuvwxyzABZDEFGHIJKLMNOPQRSTUVQXYZ0123456789"

TRAIN_DATA = np.load(os.path.join(THIS_DIR, "features.npy"))

cmap = plt.cm.coolwarm
norm = matplotlib.colors.Normalize(vmin=10, vmax=90)
MAPPABLE = cm.ScalarMappable(norm=norm, cmap=cmap)


def _return_feature_statistics(feature_number: int, feature_value: float):
    """
    ToDo: vectorize this function. 
    
    Arguments:
        feature_number {int} -- number of the feature
        feature_value {float} -- value of the feature (used to compute color)
        
    Returns: 
        {dict} -- with percentile position (ranked) and the color for the cell
    """

    percentile_score = int(
        stats.percentileofscore(TRAIN_DATA.T[feature_number], feature_value)
    )

    color = matplotlib.colors.to_hex(MAPPABLE.to_rgba(percentile_score))

    return percentile_score, color


def _return_feature_statistics_array(X):
    results = []
    for i, val in enumerate(X.T):
        score, color = _return_feature_statistics(i, val)

        results.append((val, str(score), str(color)))

    return results


def _featurize_single(structure, feature_dir: str = ""):
    """Featurizes structure, returns feature vector, feature values and metal indices.  

    Arguments:
        structure {pymatgen Structe} -- (name of structure, string with structure)
        feature_dir {str} -- output directory for features
        
    Returns: 
        X {np.array} -- feature matrix
        feature_value_dict {dict}  --
        metal_indices {list}
        names {list} -- list of feature names
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
        feature_stats = _return_feature_statistics_array(site)
        feature_value_dict[metals[i] + " " + alph[i]] = dict(zip(names, feature_stats))
    return X, feature_value_dict, metal_indices, names


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass
