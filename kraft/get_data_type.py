from numpy import asarray, unique

from .check_nd_array_for_bad import check_nd_array_for_bad


def get_data_type(data):

    data = asarray(data)

    data_good = data[~check_nd_array_for_bad(data, raise_for_bad=False)]

    if all(float(n).is_integer() for n in data_good):

        n_good_unique = unique(data_good).size

        if n_good_unique == 2:

            return "binary"

        elif n_good_unique <= 32:

            return "categorical"

    return "continuous"