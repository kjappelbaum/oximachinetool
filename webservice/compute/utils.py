# -*- coding: utf-8 -*-
"""Some utility functions"""
import os
import pickle
import subprocess
from tempfile import NamedTemporaryFile

from pymatgen.io.ase import AseAtomsAdaptor

MAX_NUMBER_OF_ATOMS = 500
THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def load_pickle(file):
    """Read a pickle with and return content"""
    with open(file, "rb") as fhandle:
        res = pickle.load(fhandle)
    return res


def get_metals_idx_in_structure(structure):
    metal_idxs = []

    for index, site in enumerate(structure):
        if site.specie.is_metal:
            metal_idxs.append(index)
    return metal_idxs


def string_to_pymatgen(structurestring):
    """Convert a string parsed by flask to a pymatgen structure object.
    We asume that structurestring is a CIF"""
    try:
        atoms = run_c2x(structurestring)
        structure = AseAtomsAdaptor().get_structure(atoms)
        if len(structure) > MAX_NUMBER_OF_ATOMS:
            raise LargeStructureError("Structure too large")
    except Exception as excep:  # pylint:disable=broad-except)
        raise ValueError(
            "We could not parse the CIF, you might try rewriting the CIF in P1 symmetry \
                 (and also remove any clashing atoms/disorder). The exception was {}".format(
                excep
            )
        ) from excep
    return structure


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
    """Raised when the format cannot be read"""


class OverlapError(Exception):
    """Error raised if overlaps of atoms are detected in the structure."""


class LargeStructureError(Exception):
    """Error raised if structure is too large"""


def generate_csd_link(refcode: str) -> str:
    """Take a refocde string and make a link to WebCSD"""
    return '<a href="https://www.ccdc.cam.ac.uk/structures/Search?Ccdcid={}&DatabaseToSearch=Published">{}</a>'.format(
        refcode, refcode
    )


def run_c2x(string):
    """write string to cile, run c2x to parse to .py file and convert to primitive,
    then read this file and make Atoms"""
    try:
        tmp = NamedTemporaryFile(delete=False, suffix=".cif")
        tempfile_code = NamedTemporaryFile(delete=False)

        with open(tmp.name, "w") as handle:
            handle.write(string)

        subprocess.call(
            ["./c2x_linux"]  # hardcoded path for container!
            + "{} -P --pya {}".format(tmp.name, tempfile_code.name).split(),
            stderr=subprocess.STDOUT,
            cwd=THIS_DIR,
        )

        with open(tempfile_code.name, "r") as handle:
            code_to_execute = handle.read()

        my_context = {"structure": None}
        exec(code_to_execute, globals(), my_context)

        atoms = my_context["structure"]

        tempfile_code.close()
        os.remove(tempfile_code.name)
        os.remove(tmp.name)
    except Exception as excp:
        raise IOError("could not read cif {}".format(excp)) from excp

    return atoms
