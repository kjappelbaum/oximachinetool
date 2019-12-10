#!/usr/bin/env python
"""
Main Flask python function that manages the server backend

If you just want to try it out, just run this file and connect to
http://localhost:5000 from a browser. Otherwise, read the instructions
in README_DEPLOY.md to deploy on a Apache server.
"""
from __future__ import unicode_literals
from future import standard_library

standard_library.install_aliases()

import flask
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
import copy
import io

import jinja2
import logging
import flask
import json
import numpy as np
import time, datetime
from compute.utils import (
    get_structure_tuple,
    tuple_from_pymatgen,
    UnknownFormatError,
    OverlapError,
    LargeStructureError,
    MAX_NUMBER_OF_ATOMS,
)

from compute.featurize import _featurize_single
from compute.predict import predictions
from ase.data import chemical_symbols

from web_module import get_secret_key, get_config, logme, ReverseProxied

from conf import (
    FlaskRedirectException,
    ConfigurationError,
    static_folder,
    view_folder,
)

examplemapping = {
    "cui_ii_btc": "KAJZIH_freeONLY.cif",
    "sno": "SnO_mp-2097_computed.cif",
    "sno2": "SnO2_mp-856_computed.cif",
}

# This (undocumented) flag changes the style of the webpage (CSS, etc.)
# and decides whether some of the headers (e.g. the App title) and the
# description of what app can do should appear or not
#
# Options:
# - 'lite': simple version, not title, no info description, different CSS
# - anything else: default
#
# How to pass: with Apache, when forwarding, in a ReverseProxy section, add
#   RequestHeader set X-App-Style lite
def get_style_version(request):
    return request.environ.get("HTTP_X_APP_STYLE", "")


import logging, logging.handlers

logger = logging.getLogger("tools-app")

logHandler = logging.handlers.TimedRotatingFileHandler(
    os.path.join(os.path.split(os.path.realpath(__file__))[0], "logs", "requests.log"),
    when="midnight",
)
formatter = logging.Formatter("[%(asctime)s]%(levelname)s-%(funcName)s ^ %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

## Create the app
app = flask.Flask(__name__, static_folder=static_folder)
app.use_x_sendfile = True
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.secret_key = get_secret_key()


def get_visualizer_template(request):
    if get_style_version(request) == "lite":
        return "visualizer_lite.html"
    else:
        return "visualizer.html"


def get_visualizer_select_template(request):
    if get_style_version(request) == "lite":
        return "visualizer_select_lite.html"
    else:
        return "visualizer_select.html"


MODEL_VERSION = "2019-12-7-voting_knn_gb_et_sgd_chem_metal_geo_tight"

logger = logging.getLogger("tools-app")


def get_json_for_visualizer(s):
    s = s.get_primitive_structure()
    cell, frac_coord, atomic_numbers = tuple_from_pymatgen(s)
    res = {
        "primitive_positions": np.array(frac_coord),
        "primitive_lattice": np.array(cell),
        "primitive_types": np.array(atomic_numbers),
    }
    return res


def process_structure_core(
    filecontent, fileformat, call_source="", logger=None, flask_request=None,
):
    """
    The main function that generates the data to be sent back to the view.
    
    :param filecontent: The file content (string)
    :param fileformat: The file format (string), among the accepted formats
    :param seekpath_module: the seekpath module. The reason for passing it
         is that, when running in debug mode, you want to get the local 
         seekpath rather than the installed one.
    :param call_source: a string identifying the source (i.e., who called
       this function). This is a string, mainly for logging reasons.
    :param logger: if not None, should be a valid logger, that is used
       to output useful log messages.
    :param flask_request: if logger is not None, pass also the flask.request
       object to help in logging.
    :return: this function calls directly flask methods and returns flask 
        objects
    :raise: FlaskRedirectException if there is an error that requires
        to redirect the the main selection page. The Exception message
        is the message to be flashed via Flask (or in general shown to
        the user).
    """

    start_time = time.time()
    form_data = dict(flask_request.form)
    try:
        structure_tuple, s = get_structure_tuple(
            filecontent, fileformat, extra_data=form_data
        )
    except UnknownFormatError:
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="unknownformat",
            extra={"form_data": form_data},
        )
        raise FlaskRedirectException("Unknown format '{}'".format(fileformat))
    except OverlapError:
        ## Structure too big
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="overlap",
            extra={"form_data": form_data},
        )
        raise FlaskRedirectException(
            "Sorry, there seem to be overlapping errors in the input structure"
        )
    except LargeStructureError:
        ## Structure too big
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="toolarge",
            extra={"number_of_atoms": len(structure_tuple[1]), "form_data": form_data},
        )
        raise FlaskRedirectException(
            "Sorry, this online visualizer is limited to {} atoms "
            "in the input cell, while your structure has {} atoms."
            "".format(MAX_NUMBER_OF_ATOMS, len(structure_tuple[1]))
        )
    except Exception as e:
        # There was an exception...

        print(e)
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="exception",
            extra={"exception": str(e), "form_data": form_data},
        )
        raise FlaskRedirectException(
            "I tried my best, but I wasn't able to load your "
            "file in format '{}'... because of {}".format(fileformat, e)
        )

    logme(
        logger,
        filecontent,
        fileformat,
        flask_request,
        call_source,
        reason="OK",
        extra={"number_of_atoms": len(structure_tuple[1]), "form_data": form_data},
    )

    # Now, featurize
    try:
        feature_array, feature_value_dict, metal_indices = _featurize_single(s)

    except Exception as e:
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="featurizationexception",
            extra={"exception": str(e)},
        )
    else:
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="Featurize-OK",
            extra={
                "feature_val_dict": feature_value_dict,
                "feature_array_shape": feature_array.shape,
            },
        )

    # Now, predict

    try:
        metal_sites = list(feature_value_dict.keys())
        predictions_output, prediction_labels = predictions(feature_array, metal_sites)
    except Exception as e:
        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="predictionexception",
            extra={"exception": str(e), "shape_array": feature_array.shape},
        )

    try:
        in_json_data = {
            "cell": structure_tuple[0],
            "scaled_coords": structure_tuple[1],
            "atomic_numbers": structure_tuple[2],
        }

        path_results = get_json_for_visualizer(s)

        raw_code_dict = copy.copy(path_results)

        raw_code_dict["primitive_lattice"] = path_results["primitive_lattice"].tolist()
        raw_code_dict["primitive_positions"] = path_results[
            "primitive_positions"
        ].tolist()
        inputstructure_positions_cartesian = np.dot(
            np.array(in_json_data["scaled_coords"]), np.array(in_json_data["cell"])
        ).tolist()
        primitive_positions_cartesian = np.dot(
            np.array(path_results["primitive_positions"]),
            np.array(path_results["primitive_lattice"]),
        ).tolist()
        primitive_positions_cartesian_refolded = np.dot(
            np.array(path_results["primitive_positions"]) % 1.0,
            np.array(path_results["primitive_lattice"]),
        ).tolist()
        raw_code_dict["primitive_positions_cartesian"] = primitive_positions_cartesian

        raw_code_dict["primitive_types"] = path_results["primitive_types"].tolist()
        primitive_symbols = [
            chemical_symbols[num] for num in path_results["primitive_types"]
        ]
        raw_code_dict["primitive_symbols"] = primitive_symbols
        # raw_code_dict["primitive_symbols"] = path_results["primitive_types"]

        raw_code = json.dumps(raw_code_dict, indent=2)

        raw_code = (
            str(jinja2.escape(raw_code)).replace("\n", "<br>").replace(" ", "&nbsp;")
        )
        inputstructure_cell_vectors = [
            [idx, coords[0], coords[1], coords[2]]
            for idx, coords in enumerate(in_json_data["cell"], start=1)
        ]
        inputstructure_symbols = [
            chemical_symbols[num] for num in in_json_data["atomic_numbers"]
        ]
        inputstructure_atoms_scaled = [
            [label, coords[0], coords[1], coords[2]]
            for label, coords in zip(
                inputstructure_symbols, in_json_data["scaled_coords"]
            )
        ]
        inputstructure_atoms_cartesian = [
            [label, coords[0], coords[1], coords[2]]
            for label, coords in zip(
                inputstructure_symbols, inputstructure_positions_cartesian
            )
        ]

        atoms_scaled = [
            [label, coords[0], coords[1], coords[2]]
            for label, coords in zip(
                primitive_symbols, path_results["primitive_positions"]
            )
        ]

        atoms_cartesian = [
            [label, coords[0], coords[1], coords[2]]
            for label, coords in zip(primitive_symbols, primitive_positions_cartesian)
        ]

        direct_vectors = [
            [idx, coords[0], coords[1], coords[2]]
            for idx, coords in enumerate(path_results["primitive_lattice"], start=1)
        ]

        primitive_lattice = path_results["primitive_lattice"]
        xsfstructure = []
        xsfstructure.append("CRYSTAL")
        xsfstructure.append("PRIMVEC")
        for vector in primitive_lattice:
            xsfstructure.append("{} {} {}".format(vector[0], vector[1], vector[2]))
        xsfstructure.append("PRIMCOORD")
        xsfstructure.append("{} 1".format(len(primitive_positions_cartesian_refolded)))
        for atom_num, pos in zip(
            path_results["primitive_types"], primitive_positions_cartesian_refolded
        ):
            xsfstructure.append("{} {} {} {}".format(atom_num, pos[0], pos[1], pos[2]))
        xsfstructure = "\n".join(xsfstructure)

        compute_time = time.time() - start_time

    except Exception as e:

        logme(
            logger,
            filecontent,
            fileformat,
            flask_request,
            call_source,
            reason="codeexception",
            extra={"exception": str(e), "form_data": form_data},
        )
        raise

    return dict(
        # jsondata=json.dumps(out_json_data),
        raw_code=raw_code,
        prediction_labels=prediction_labels,
        metal_indices=metal_indices,
        predictions_output=predictions_output,
        inputstructure_cell_vectors=inputstructure_cell_vectors,
        inputstructure_atoms_scaled=inputstructure_atoms_scaled,
        inputstructure_atoms_cartesian=inputstructure_atoms_cartesian,
        atoms_scaled=atoms_scaled,
        direct_vectors=direct_vectors,
        atoms_cartesian=atoms_cartesian,
        compute_time=compute_time,
        model_version=MODEL_VERSION,
        xsfstructure=xsfstructure,
        feature_values=feature_value_dict,
    )


@app.route("/")
def index():
    """
    Main view, redirect to input_structure
    """
    return flask.redirect(flask.url_for("input_structure"))


@app.route("/")
def input_data():
    """
    Main view, input data selection and upload
    """
    return flask.render_template(
        get_visualizer_select_template(flask.request), **get_config()
    )


@app.route("/termsofuse/")
def termsofuse():
    """
    View for the terms of use
    """
    return flask.send_from_directory(view_folder, "termsofuse.html")


@app.route("/input_structure/")
def input_structure():
    """
    Input structure selection
    """
    return flask.render_template(get_visualizer_select_template(flask.request))


@app.route("/process_structure/", methods=["GET", "POST"])
def process_structure():
    """
    Process a structure (uploaded from POST request)
    """
    if flask.request.method == "POST":
        # check if the post request has the file part
        if "structurefile" not in flask.request.files:
            return flask.redirect(flask.url_for("input_structure"))
        structurefile = flask.request.files["structurefile"]
        fileformat = flask.request.form.get("fileformat", "unknown")
        filecontent = structurefile.read().decode("utf-8")

        try:
            data_for_template = process_structure_core(
                filecontent=filecontent,
                fileformat=fileformat,
                call_source="process_structure",
                logger=logger,
                flask_request=flask.request,
            )
            return flask.render_template(
                get_visualizer_template(flask.request), **data_for_template
            )
        except FlaskRedirectException as e:
            flask.flash(str(e))
            return flask.redirect(flask.url_for("input_structure"))
        except OverlapError:
            flask.flash("Maybe you have overlapping atoms?")
            return flask.redirect(flask.url_for("input_structure"))
        except LargeStructureError:
            flask.flash(
                "You seem to have too many atoms in your structure to run on the web"
            )
            return flask.redirect(flask.url_for("input_structure"))
        except Exception as e:
            flask.flash("Unable to process the structure, sorry... {}".format(e))
            return flask.redirect(flask.url_for("input_structure"))

    else:  # GET Request
        return flask.redirect(flask.url_for("input_structure"))


@app.route("/process_example_structure/", methods=["GET", "POST"])
def process_example_structure():
    """
    Process an example structure (example name from POST request)
    """
    if flask.request.method == "POST":
        examplestructure = flask.request.form.get("examplestructure", "<none>")
        flask.flash("Example {}".format(examplestructure))

        structurefilepath = os.path.join(
            THIS_DIR, "compute", "examples", examplemapping[examplestructure]
        )
        fileformat = 'cif'
        with open(structurefilepath, "r") as structurefile:
            filecontent = structurefile.read()
        
        try:
            data_for_template = process_structure_core(
                filecontent=filecontent,
                fileformat=fileformat,
                call_source="process_structure",
                logger=logger,
                flask_request=flask.request,
            )
            return flask.render_template(
                get_visualizer_template(flask.request), **data_for_template
            )
        except FlaskRedirectException as e:
            flask.flash(str(e))
            return flask.redirect(flask.url_for("input_structure"))
        except OverlapError:
            flask.flash("Maybe you have overlapping atoms?")
            return flask.redirect(flask.url_for("input_structure"))
        except LargeStructureError:
            flask.flash(
                "You seem to have too many atoms in your structure to run on the web"
            )
            return flask.redirect(flask.url_for("input_structure"))
        except Exception as e:
            flask.flash("Unable to process the structure, sorry... {}".format(e))
            return flask.redirect(flask.url_for("input_structure"))

    else:  # GET Request
        return flask.redirect(flask.url_for("input_structure"))


@app.route("/static/js/<path:path>")
def send_js(path):
    """
    Serve static JS files
    """
    return flask.send_from_directory(os.path.join(static_folder, "js"), path)


@app.route("/static/img/<path:path>")
def send_img(path):
    """
    Serve static image files
    """
    return flask.send_from_directory(os.path.join(static_folder, "img"), path)


@app.route("/static/css/<path:path>")
def send_css(path):
    """
    Serve static CSS files
    """
    return flask.send_from_directory(os.path.join(static_folder, "css"), path)


@app.route("/static/css/images/<path:path>")
def send_cssimages(path):
    """
    Serve static CSS images files
    """
    return flask.send_from_directory(os.path.join(static_folder, "css", "images"), path)


@app.route("/static/fonts/<path:path>")
def send_fonts(path):
    """
    Serve static font files
    """
    return flask.send_from_directory(os.path.join(static_folder, "fonts"), path)


if __name__ == "__main__":
    # Don't use x-sendfile when testing it, because this is only good
    # if deployed with Apache
    # Use the local version of app, not the installed one
    app.use_x_sendfile = False
    app.run(debug=True)
