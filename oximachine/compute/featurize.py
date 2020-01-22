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
alph = 'abcdefghijlmnopqrstuvwxyzABZDEFGHIJKLMNOPQRSTUVQXYZ0123456789'

TRAIN_DATA = np.load(os.path.join(THIS_DIR, 'features.npy'))

def _get_cmaps(upper_threshold=0.75, lower_threshold=0.25):
    cmaps = []
    for column in TRAIN_DATA.T:
        cmap = plt.cm.inferno
        upper = np.quantile(column, upper_threshold)
        lower = np.quantile(column, lower_threshold)
        norm = matplotlib.colors.Normalize(vmin=lower, vmax=upper)  
        
        cmaps.append(cm.ScalarMappable(norm=norm, cmap=cmap)) 
        
    return cmaps 

CMAPS = _get_cmaps()
        

def _return_feature_statistics(feature_number: int, feature_value: float):
    """
    ToDo: vectorize this function. 
    
    Arguments:
        feature_number {int} -- number of the feature
        feature_value {float} -- value of the feature (used to compute color)
        
    Returns: 
        {dict} -- with percentile position (ranked) and the color for the cell
    """
    
    percentile_score = stats.percentileofscore(TRAIN_DATA.T[feature_number], feature_value)
    color = matplotlib.colors.to_hex(CMAPS[feature_number].to_rgba(feature_value))
    
    return percentile_score, color
    
def _return_feature_statistics_array(X): 
    ranks = []
    colors = []
    for i, val in enumerate(X): 
        score, color = _return_feature_statistics(i, val)
        ranks.append(score)
        colors.append(color)
    
    return np.hstack([X, ranks, color])

def _featurize_single(structure, feature_dir: str = ""):
    """Featurizes structure, returns feature vector, feature values and metal indices.  

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
        feature_stats = _return_feature_statistics_array(site)
        feature_value_dict[metals[i] + ' ' + alph[i]] = dict(zip(names, feature_stats))
    return X, feature_value_dict, metal_indices


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass
