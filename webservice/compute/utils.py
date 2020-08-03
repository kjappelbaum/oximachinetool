# -*- coding: utf-8 -*-
import pickle
from io import StringIO

from ase.build import niggli_reduce
from ase.io import read
from pymatgen.io.ase import AseAtomsAdaptor

MAX_NUMBER_OF_ATOMS = 500


def load_pickle(f):
    with open(f, 'rb') as fh:
        res = pickle.load(fh)
    return res


def string_to_pymatgen(s):
    try:
        fileobj = StringIO(s)
        atoms = read(fileobj, format='cif')
        s = AseAtomsAdaptor().get_structure(atoms)
        s = s.get_primitive_structure()
        if len(s) > MAX_NUMBER_OF_ATOMS:
            raise LargeStructureError('Structure too large')
    except Exception as e:
        raise ValueError(
            'We could not parse the CIF, you might try rewriting the CIF in P1 symmetry (and also remove any clashing atoms/disorder). The exception was {}'
            .format(e))
    return s


def get_structure_tuple(fileobject, fileformat, extra_data=None):
    """
    Given a file-like object (using StringIO or open()), and a string
    identifying the file format, return a structure tuple as accepted
    by seekpath.
    :param fileobject: a file-like object containing the file content
    :param fileformat: a string with the format to use to parse the data
    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    if fileformat == 'cif':
        structure = string_to_pymatgen(fileobject)
        structure_tuple = tuple_from_pymatgen(structure)
        return structure_tuple, structure
    raise UnknownFormatError(fileformat)


def tuple_from_pymatgen(pmgstructure):
    """
    Given a pymatgen structure, return a structure tuple as expected from seekpath
    :param pmgstructure: a pymatgen Structure object

    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    frac_coords = pmgstructure.frac_coords.tolist()
    structure_tuple = (
        pmgstructure.lattice.matrix.tolist(),
        frac_coords,
        pmgstructure.atomic_numbers,
    )
    return structure_tuple


class UnknownFormatError(ValueError):
    pass


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass


class LargeStructureError(Exception):
    """
    Error raised if structure is too large
    """

    pass


def generate_csd_link(refcode: str) -> str:
    return '<a href="https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid={}&DatabaseToSearch=Published">{}</a>'.format(
        refcode, refcode)
