# -*- coding: utf-8 -*-
"""Some utility functions"""
import os
import pickle
import subprocess

from ase import Atoms
from pymatgen.io.ase import AseAtomsAdaptor

MAX_NUMBER_OF_ATOMS = 500
THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def load_pickle(file):
    with open(file, "rb") as fhandle:
        res = pickle.load(fhandle)
    return res


def string_to_pymatgen(structurestring):
    """Convert a string parsed by flask to a pymatgen structure object. We asume that structurestring is a CIF"""
    try:
        atoms = run_c2x(structurestring)
        s = AseAtomsAdaptor().get_structure(atoms)
        if len(s) > MAX_NUMBER_OF_ATOMS:
            raise LargeStructureError("Structure too large")
    except Exception as e:  # pylint:disable=invalid-name, broad-except
        raise ValueError(
            "We could not parse the CIF, you might try rewriting the CIF in P1 symmetry (and also remove any clashing atoms/disorder). The exception was {}".format(
                e
            )
        )
    return s


def get_structure_tuple(fileobject, fileformat):
    """
    Given a file-like object (using StringIO or open()), and a string
    identifying the file format, return a structure tuple as accepted
    by seekpath.
    :param fileobject: a file-like object containing the file content
    :param fileformat: a string with the format to use to parse the data
    :return: a structure tuple (cell, positions, numbers) as accepted
        by seekpath.
    """
    if fileformat == "cif":
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
    pass  # pylint:disable=unnecessary-pass


class OverlapError(Exception):
    """
    Error raised if overlaps of atoms are detected in the structure.
    """

    pass  # pylint:disable=unnecessary-pass


class LargeStructureError(Exception):
    """
    Error raised if structure is too large
    """

    pass  # pylint:disable=unnecessary-pass


def generate_csd_link(refcode: str) -> str:
    """Take a refocde string and make a link to WebCSD"""
    return '<a href="https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid={}&DatabaseToSearch=Published">{}</a>'.format(
        refcode, refcode
    )


# Todo: make this a bit cleaner
def run_c2x(string):
    """write string to cile, run c2x to parse to .py file and convert to primitive, then read this file and make Atoms"""
    try:
        with open(os.path.join(THIS_DIR, "file.cif"), "w") as tmp:
            tmp.write(string)
            tmp.close()

            subprocess.call(
                ["./c2x_linux"]  # hardcoded path for container!
                + "{} -P --pya ciffile2x2020.py".format("file.cif").split(),
                stderr=subprocess.STDOUT,
                cwd=THIS_DIR,
            )

        from . import ciffile2x2020  # pylint:disable=import-error, import-outside-toplevel

        atoms = Atoms(ciffile2x2020.structure)

        os.remove(os.path.join(THIS_DIR, 'ciffile2x2020.py'))
        os.remove(os.path.join(THIS_DIR, 'file.cif'))
    except Exception as e:  # pylint:disable=invalid-name, broad-except
        raise IOError("could not read cif {}".format(e))

    return atoms
