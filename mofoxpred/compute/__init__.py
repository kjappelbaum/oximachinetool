import logging
import flask
from flask import Blueprint

blueprint = Blueprint("compute", __name__, url_prefix="/compute")

logger = logging.getLogger("tools-app")


@blueprint.route("/process_structure/", methods=["GET", "POST"])
def process_structure():
    if flask.request.method == "POST":
        structurefile = flask.request.files["structurefile"]
        fileformat = flask.request.form.get("fileformat", "unknown")
        filecontent = structurefile.read().decode("utf-8")

        try:
            return "FORMAT: {}<br>CONTENT:<br><code><pre>{}</pre></code>".format(
                fileformat, filecontent
            )
        except Exception:
            flask.flash("Unable to process the data, sorry...")
            return flask.redirect(flask.url_for("input_data"))
    else:
        return flask.redirect(flask.url_for("compute.process_structure_example"))


@blueprint.route("/process_example_structure/", methods=["GET", "POST"])
def process_structure_example():
    if flask.request.method == "POST":
        return "This was a POST"
    else:
        return "This was a GET"
