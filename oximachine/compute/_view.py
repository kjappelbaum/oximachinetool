# -*- coding: utf-8 -*-
from .utils import string_to_pymatgen


def return_viewer(s: Structure, labels: list = None):
    import nglview as nv
    from pymatgen.io.ase import AseAtomsAdaptor

    coords = s.cart_coords  # - atoms.get_center_of_mass()
    v = nv.show_pymatgen(s, center=False, dis=False)
    v.clear_representations()
    v.component_1.add_ball_and_stick(radius=0.2)
    v.component_1.add_unitcell()
    v.layout.width = '500px'
    v.parameters = dict(clipDist=-100, sampleLevel=10)
    if labels is not None:
        # For some reason labelType must be "format"
        for i, label in enumerate(labels[0]):
            v.shape.add_label(
                [label],
                labelType='format',
                labelFormat=labels[1][i],
                opacity=1,
                fontWeight='bold',
                zOffset=1.2,
                attachment='middle-center',
                scale=0.5,
                color='black',
            )

    return v, coords, labels[0], labels[1]


def view_structure(name, w, prediction_dict):
    s = string_to_pymatgen(w.value[name + '.cif']['content'])
    if prediction_dict:
        predictions = prediction_dict[name]
        oxidationstates = [v['prediction'] for v in list(predictions.values())]
        probabilities = [v['probability'] for v in list(predictions.values())]
        labels = (list(predictions.keys()), oxidationstates)

    else:
        labels = None
    v, cart_coords, labels0, labels1 = return_viewer(s, labels)
    assignment_string = ', '.join(
        ['{}: {} ({}%)'.format(s[0], s[1], s[2]) for s in zip(labels0, labels1, probabilities)])
    print('Assignments: {}'.format(assignment_string))
    return v, cart_coords, labels0, labels1
