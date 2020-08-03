# -*- coding: utf-8 -*-
# pylint:disable=invalid-name
import os


class ConfigurationError(Exception):
    pass


class FlaskRedirectException(Exception):
    pass


directory = os.path.split(os.path.realpath(__file__))[0]
static_folder = os.path.join(directory, 'static')
user_static_folder = os.path.join(directory, 'user_static')
view_folder = os.path.join(directory, 'view')
config_file_path = os.path.join(static_folder, 'config.yaml')

APPROXIMATE_MAPPING = {
    'True': True,
    'False': False,
}

DEFAULT_APPROXIMATE = APPROXIMATE_MAPPING['True']

EXAMPLEMAPPING = {
    'cui_ii_btc': 'KAJZIH_freeONLY.cif',
    'sno': 'SnO_mp-2097_computed.cif',
    'sno2': 'SnO2_mp-856_computed.cif',
    'bao': 'BaO_mp-1342_computed.cif',
    'bao2': 'BaO2_mp-1105_computed.cif',
    'fe_btc': 'ACODAA.cif',
    'uio_66': 'UiO66_GC1.cif',
}

MODEL_VERSION = '2019-12-7-voting_knn_gb_et_sgd_chem_metal_geo_tight'
