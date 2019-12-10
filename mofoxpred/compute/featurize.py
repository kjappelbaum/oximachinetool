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


def _featurize_single(structure: tuple, feature_dir: str):
    """[summary]
    
    Arguments:
        structure {tuple} -- (name of structure, string with structure)
        feature_dir {str} -- output directory for features
    """
    name = structure[0]
    gf = GetFeatures.from_string(structure[1], feature_dir)
    gf.path = name
    gf.outname = os.path.join(gf.outpath, "".join([name, ".pkl"]))
    gf.run_featurization()


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass
