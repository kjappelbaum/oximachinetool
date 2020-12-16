# -*- coding: utf-8 -*-
# pylint:disable=invalid-name
"""Configuration variables for the app"""
import os


class ConfigurationError(Exception):
    """Raised for example if SECRET_KEY file is missing"""


class FlaskRedirectException(Exception):
    """Raised for most errors in the webapp"""


directory = os.path.split(os.path.realpath(__file__))[0]
static_folder = os.path.join(directory, "static")
user_static_folder = os.path.join(directory, "user_static")
view_folder = os.path.join(directory, "view")
config_file_path = os.path.join(static_folder, "config.yaml")

APPROXIMATE_MAPPING = {
    "True": True,
    "False": False,
}

DEFAULT_APPROXIMATE = APPROXIMATE_MAPPING["True"]

EXAMPLEMAPPING = {
    "cui_ii_btc": "KAJZIH_freeONLY.cif",
    "sno": "SnO_mp-2097_computed.cif",
    "sno2": "SnO2_mp-856_computed.cif",
    "bao": "BaO_mp-1342_computed.cif",
    "bao2": "BaO2_mp-1105_computed.cif",
    "fe_btc": "ACODAA.cif",
    "uio_66": "UiO66_GC1.cif",
}
