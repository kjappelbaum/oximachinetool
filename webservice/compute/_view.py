# -*- coding: utf-8 -*-
"""Returns the structure viewer with the oxidation state annotations."""
import nglview as nv
from pymatgen import Structure

from .utils import string_to_pymatgen


def return_viewer(structure: Structure, labels: list = None):
    """Returns nglview viewer with oxidationstates labels"""
    coords = structure.cart_coords  # - atoms.get_center_of_mass()
    visualizer = nv.show_pymatgen(structure, center=False, dis=False)
    visualizer.clear_representations()
    visualizer.component_1.add_ball_and_stick(radius=0.2)
    visualizer.component_1.add_unitcell()
    visualizer.layout.width = "500px"
    visualizer.parameters = dict(clipDist=-100, sampleLevel=10)
    if labels is not None:
        # For some reason labelType must be "format"
        for i, label in enumerate(labels[0]):
            visualizer.shape.add_label(
                [label],
                labelType="format",
                labelFormat=labels[1][i],
                opacity=1,
                fontWeight="bold",
                zOffset=1.2,
                attachment="middle-center",
                scale=0.5,
                color="black",
            )

    return visualizer, coords, labels[0], labels[1]


def view_structure(name, w, prediction_dict):  # pylint: disable=invalid-name
    structure = string_to_pymatgen(w.value[name + ".cif"]["content"])
    if prediction_dict:
        predictions = prediction_dict[name]
        oxidationstates = [value["prediction"] for value in list(predictions.values())]
        labels = (list(predictions.keys()), oxidationstates)

    else:
        labels = None
    visualizer, cart_coords, labels0, labels1 = return_viewer(structure, labels)
    return visualizer, cart_coords, labels0, labels1
