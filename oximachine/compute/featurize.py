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
from oximachinerunner.featurize import GetFeatures, FeatureCollector
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

feature_cat_dict = {
    "wt CN_1": "geometry",
    "sgl_bd CN_1": "geometry",
    "wt CN_2": "geometry",
    "L-shaped CN_2": "geometry",
    "water-like CN_2": "geometry",
    "bent 120 degrees CN_2": "geometry",
    "bent 150 degrees CN_2": "geometry",
    "linear CN_2": "geometry",
    "wt CN_3": "geometry",
    "trigonal planar CN_3": "geometry",
    "trigonal non-coplanar CN_3": "geometry",
    "T-shaped CN_3": "geometry",
    "wt CN_4": "geometry",
    "square co-planar CN_4": "geometry",
    "tetrahedral CN_4": "geometry",
    "rectangular see-saw-like CN_4": "geometry",
    "see-saw-like CN_4": "geometry",
    "trigonal pyramidal CN_4": "geometry",
    "wt CN_5": "geometry",
    "pentagonal planar CN_5": "geometry",
    "square pyramidal CN_5": "geometry",
    "trigonal bipyramidal CN_5": "geometry",
    "wt CN_6": "geometry",
    "hexagonal planar CN_6": "geometry",
    "octahedral CN_6": "geometry",
    "pentagonal pyramidal CN_6": "geometry",
    "wt CN_7": "geometry",
    "hexagonal pyramidal CN_7": "geometry",
    "pentagonal bipyramidal CN_7": "geometry",
    "wt CN_8": "geometry",
    "body-centered cubic CN_8": "geometry",
    "hexagonal bipyramidal CN_8": "geometry",
    "wt CN_9": "geometry",
    "q2 CN_9": "geometry",
    "q4 CN_9": "geometry",
    "q6 CN_9": "geometry",
    "wt CN_10": "geometry",
    "q2 CN_10": "geometry",
    "q4 CN_10": "geometry",
    "q6 CN_10": "geometry",
    "wt CN_11": "geometry",
    "q2 CN_11": "geometry",
    "q4 CN_11": "geometry",
    "q6 CN_11": "geometry",
    "wt CN_12": "geometry",
    "cuboctahedral CN_12": "geometry",
    "q2 CN_12": "geometry",
    "q4 CN_12": "geometry",
    "q6 CN_12": "geometry",
    "wt CN_13": "geometry",
    "wt CN_14": "geometry",
    "wt CN_15": "geometry",
    "wt CN_16": "geometry",
    "wt CN_17": "geometry",
    "wt CN_18": "geometry",
    "wt CN_19": "geometry",
    "wt CN_20": "geometry",
    "wt CN_21": "geometry",
    "wt CN_22": "geometry",
    "wt CN_23": "geometry",
    "wt CN_24": "geometry",
    "local difference in MendeleevNumber": "chemistry",
    "local difference in Column": "chemistry",
    "local difference in Row": "chemistry",
    "local difference in Electronegativity": "chemistry",
    "local difference in NsValence": "chemistry",
    "local difference in NpValence": "chemistry",
    "local difference in NdValence": "chemistry",
    "local difference in NfValence": "chemistry",
    "local difference in NValence": "chemistry",
    "local difference in NsUnfilled": "chemistry",
    "local difference in NpUnfilled": "chemistry",
    "local difference in NdUnfilled": "chemistry",
    "local difference in NfUnfilled": "chemistry",
    "local difference in NUnfilled": "chemistry",
    "local difference in GSbandgap": "chemistry",
    "local signed difference in MendeleevNumber": "chemistry",
    "local signed difference in Column": "chemistry",
    "local signed difference in Row": "chemistry",
    "local signed difference in Electronegativity": "chemistry",
    "local signed difference in NsValence": "chemistry",
    "local signed difference in NpValence": "chemistry",
    "local signed difference in NdValence": "chemistry",
    "local signed difference in NfValence": "chemistry",
    "local signed difference in NValence": "chemistry",
    "local signed difference in NsUnfilled": "chemistry",
    "local signed difference in NpUnfilled": "chemistry",
    "local signed difference in NdUnfilled": "chemistry",
    "local signed difference in NfUnfilled": "chemistry",
    "local signed difference in NUnfilled": "chemistry",
    "local signed difference in GSbandgap": "chemistry",
    "maximum local difference in MendeleevNumber": "chemistry",
    "maximum local difference in Column": "chemistry",
    "maximum local difference in Row": "chemistry",
    "maximum local difference in Electronegativity": "chemistry",
    "maximum local difference in NsValence": "chemistry",
    "maximum local difference in NpValence": "chemistry",
    "maximum local difference in NdValence": "chemistry",
    "maximum local difference in NfValence": "chemistry",
    "maximum local difference in NValence": "chemistry",
    "maximum local difference in NsUnfilled": "chemistry",
    "maximum local difference in NpUnfilled": "chemistry",
    "maximum local difference in NdUnfilled": "chemistry",
    "maximum local difference in NfUnfilled": "chemistry",
    "maximum local difference in NUnfilled": "chemistry",
    "maximum local difference in GSbandgap": "chemistry",
    "mimum local difference in MendeleevNumber": "chemistry",
    "mimum local difference in Column": "chemistry",
    "mimum local difference in Row": "chemistry",
    "mimum local difference in Electronegativity": "chemistry",
    "mimum local difference in NsValence": "chemistry",
    "mimum local difference in NpValence": "chemistry",
    "mimum local difference in NdValence": "chemistry",
    "mimum local difference in NfValence": "chemistry",
    "mimum local difference in NValence": "chemistry",
    "mimum local difference in NsUnfilled": "chemistry",
    "mimum local difference in NpUnfilled": "chemistry",
    "mimum local difference in NdUnfilled": "chemistry",
    "mimum local difference in NfUnfilled": "chemistry",
    "mimum local difference in NUnfilled": "chemistry",
    "mimum local difference in GSbandgap": "chemistry",
    "G2_0.05": "geometry",
    "G2_4.0": "geometry",
    "G2_20.0": "geometry",
    "G2_80.0": "geometry",
    "G4_0.005_1.0_1.0": "geometry",
    "G4_0.005_1.0_-1.0": "geometry",
    "G4_0.005_4.0_1.0": "geometry",
    "G4_0.005_4.0_-1.0": "geometry",
    "number": "metal",
    "row": "metal",
    "column": "metal",
    "valenceelectrons": "metal",
    "diffto18electrons": "metal",
    "sunfilled": "metal",
    "punfilled": "metal",
    "dunfilled": "metal",
    "random_column": "metal",
}


def _return_feature_statistics(feature_number: int, feature_value: float, names: list):
    """
    ToDo: vectorize this function. 
    
    Arguments:
        feature_number {int} -- number of the feature
        feature_value {float} -- value of the feature (used to compute color)
        names {list} -- list of feature names
        
    Returns: 
     
    """

    percentile_score = int(
        stats.percentileofscore(TRAIN_DATA.T[feature_number], feature_value)
    )

    color = matplotlib.colors.to_hex(MAPPABLE.to_rgba(percentile_score))

    # ToDo: Maybe not only return the category but also the color which we used in the article
    return percentile_score, color, feature_cat_dict[names[feature_number]]


def _return_feature_statistics_array(X, names):
    results = []
    for i, val in enumerate(X.T):
        score, color, category = _return_feature_statistics(i, val, names)

        results.append((val, str(score), str(color), category))

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
    structure = structure.get_primitive_structure()
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
    names_ = [n.replace("mimum", "minimum") for n in names]  # ToDo: Cleanup name
    feature_value_dict = {}
    for i, site in enumerate(X):
        feature_stats = _return_feature_statistics_array(site, names)
        feature_value_dict[metals[i] + " " + alph[i]] = dict(zip(names_, feature_stats))
    return X, feature_value_dict, metal_indices, names


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass
