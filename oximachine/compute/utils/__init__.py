from cifcheck.checks import check_clashing

MAX_NUMBER_OF_ATOMS = 500


def string_to_pymatgen(s):
    from pymatgen.io.cif import CifParser

    try:
        cp = CifParser.from_string(s)
        s = cp.get_structures()[0]
        coord_matrix = s.cart_coords
        if check_clashing(coord_matrix, method="kdtree"):
            raise OverlapError("Overlapping atoms")
        if len(s) > MAX_NUMBER_OF_ATOMS:
            raise LargeStructureError("Structure too large")
    except Exception as e:
        raise ValueError("Pymatgen could not parse CIF, you might try rewriting the CIF in P1 symmetry.")
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
    frac_coords = [site.frac_coords.tolist() for site in pmgstructure.sites]
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

