"""
Computational Cancer Analysis Library v0.1


Authors:
Pablo Tamayo
pablo.tamayo.r@gmail.com
Computational Cancer Analysis, UCSD Cancer Center

Huwate (Kwat) Yeerna (Medetgul-Ernar)
kwat.medetgul.ernar@gmail.com
Computational Cancer Analysis, UCSD Cancer Center

James Jensen
jdjensen@eng.ucsd.edu
Laboratory of Jill Mesirov
"""
from numpy import ones, isnan
from numpy.random import random_integers, random_sample
from pandas import DataFrame, Series, read_csv

# ======================================================================================================================
# Parameters
# ======================================================================================================================
VERBOSE = True
SEED = 20121020


# ======================================================================================================================
# Utilities
# ======================================================================================================================
def print_log(string):
    """
    Print `string` together with logging information.
    :param string: str; message to printed
    :return: None
    """
    from datetime import datetime

    global VERBOSE
    if VERBOSE:
        print('<{}> {}'.format(datetime.now().strftime('%H:%M:%S'), string))


def install_libraries(libraries_needed):
    """
    Check if `libraries_needed` are installed; if not then install using pip.
    :param libraries_needed: iterable; library names
    :return: None
    """
    from pip import get_installed_distributions, main

    print_log('Checking library dependencies ...')
    libraries_installed = [lib.key for lib in get_installed_distributions()]
    for lib in libraries_needed:
        if lib not in libraries_installed:
            print_log('{} not found! Installing {} using pip ...'.format(lib, lib))
            main(['install', lib])
    print_log('Using the following libraries:')
    for lib in get_installed_distributions():
        if lib.key in libraries_needed:
            print_log('\t{} (v{})'.format(lib.key, lib.version))


def plant_seed(a_seed=SEED):
    """
    Set random seed.
    :param a_seed: int;
    :return: None
    """
    from random import seed
    seed(a_seed)
    print_log('Planted a random seed {}.'.format(SEED))


def establish_path(filepath):
    """
    Make directories up to `fullpath` if they don't already exist.
    :param filepath: str;
    :return: None
    """
    from os import path, mkdir

    if not (path.isdir(filepath) and path.isfile(filepath) and path.islink(filepath)):
        print_log('Full path {} doesn\'t exist, creating it ...'.format(filepath))

        dirs = []
        prefix, suffix = path.split(filepath)
        while suffix != '':
            dirs.append(suffix)
            prefix, suffix = filepath.split(prefix)
        dirs.append(prefix)

        partial_path = ''
        for d in dirs[::-1]:
            partial_path = path.join(partial_path, d)
            if not (path.isdir(partial_path) or path.isfile(partial_path) or path.islink(partial_path)):
                mkdir(partial_path)


def read_gct(filepath, fill_na=None, drop_description=True):
    """
    Read a .gct (`filepath`) and convert it into a pandas DataFrame.
    :param filepath: str;
    :param fill_na: *; value to replace NaN in the DataFrame
    :param drop_description: bool; drop the Description column (column 2 in the .gct) or not
    :return: pandas DataFrame; [n_samples, n_features (or n_features + 1 if not dropping the Description column)]
    """
    df = read_csv(filepath, skiprows=2, sep='\t')
    if fill_na:
        df.fillna(fill_na, inplace=True)
    c1, c2 = df.columns[:2]
    if c1 != 'Name':
        raise ValueError('Column 1 != \'Name\'')
    if c2 != 'Description':
        raise ValueError('Column 2 != \'Description\'')
    df.set_index('Name', inplace=True)
    df.index.name = None
    if drop_description:
        df.drop('Description', axis=1, inplace=True)
    return df


def write_gct(pandas_object, filepath, index_column_name=None, descriptions=None):
    """
    Write a `pandas_object` to a `filepath` as a .gct.
    :param pandas_object: pandas DataFrame or Serires; (n_samples, m_features)
    :param filepath: str;
    :param index_column_name: str; column to be used as the index for the .gct
    :param descriptions: iterable; (n_rows of `pandas_object`); description column for the .gct
    """
    obj = pandas_object.copy()

    # Convert Series to DataFrame
    if isinstance(obj, Series):
        obj = DataFrame(obj).T

    # Set index (Name)
    if index_column_name:
        obj.set_index(index_column_name, inplace=True)
    obj.index.name = 'Name'

    # Set Description
    if descriptions:
        obj.insert(0, 'Description', descriptions)
    else:
        obj.insert(0, 'Description', obj.index)

    # Set output filename suffix
    if not filepath.endswith('.gct'):
        filepath += '.gct'

    with open(filepath, 'w') as f:
        f.writelines('#1.2\n{}\t{}\n'.format(*obj.shape))
        obj.to_csv(f, sep='\t')


# ======================================================================================================================#
# Data analysis
# ======================================================================================================================#
def get_unique_in_order(iterable):
    """
    Get unique elements in order or appearance in `iterable`.
    :param iterable: iterable;
    :return: list;
    """
    unique_in_order = []
    for x in iterable:
        if x not in unique_in_order:
            unique_in_order.append(x)
    return unique_in_order


def make_random_features(n_rows, n_cols, n_categories=None):
    """
    Simulate DataFrame (2D) or Series (1D).
    :param n_rows: int;
    :param n_cols: int;
    :param n_categories: None or int; continuous if None and categorical if int
    :return: pandas DataFrame; (`n_rows`, `n_cols`)
    """
    shape = (n_rows, n_cols)
    indices = ['Feature {}'.format(i) for i in range(n_rows)]
    columns = ['Element {}'.format(i) for i in range(n_cols)]
    if n_categories:
        features = DataFrame(random_integers(0, n_categories - 1, shape), index=indices, columns=columns)
    else:
        features = DataFrame(random_sample(shape), index=indices, columns=columns)
    if n_rows == 1:
        # Return series
        return features.iloc[0, :]
    else:
        return features


def drop_nan_columns(arrays):
    """
    Keep only not-NaN column positions in all `arrays`.
    :param arrays: iterable of numpy arrays; must have the same length
    :return: list of numpy arrays; none of the arrays contains NaN
    """
    not_nan_filter = ones(len(arrays[0]), dtype=bool)
    for v in arrays:
        not_nan_filter &= ~isnan(v)
    return [v[not_nan_filter] for v in arrays]


def normalize_pandas_object(pandas_object, method='-0-', axis=0):
    """
    Normalize a pandas object.
    :param pandas_object: pandas DataFrame or Series;
    :param method: str; normalization type; {'-0-', '0-1'}
    :param axis: int; 0 for by-row and 1 for by-column
    :return: pandas DataFrame or Series;
    """
    if isinstance(pandas_object, Series) or axis == 0:
        obj = pandas_object.copy()
    elif axis == 1:
        obj = pandas_object.T
    else:
        raise ValueError('Axis is not either 0 or 1.')

    if method == '-0-':
        if isinstance(obj, DataFrame):
            for i, (idx, s) in enumerate(obj.iterrows()):
                ax_mean = s.mean()
                ax_std = s.std()
                for j, v in enumerate(s):
                    obj.ix[i, j] = (v - ax_mean) / ax_std
        elif isinstance(obj, Series):
            obj = (obj - obj.mean()) / obj.std()
        else:
            raise ValueError('Not a pandas DataFrame or Series.')

    elif method == '0-1':
        if isinstance(obj, DataFrame):
            for i, (idx, s) in enumerate(obj.iterrows()):
                ax_min = s.min()
                ax_max = s.max()
                ax_range = ax_max - ax_min
                for j, v in enumerate(s):
                    obj.ix[i, j] = (v - ax_min) / ax_range
        elif isinstance(obj, Series):
            obj = (obj - obj.min()) / (obj.max() - obj.min())
        else:
            raise ValueError('Not a pandas DataFrame or Series.')
    else:
        raise ValueError('\'method\' is not one of {\'-0-\', \'0-1\'}')
    return obj


def compare_matrices(matrix1, matrix2, function, axis=0, is_distance=False):
    """
    Make association or distance matrix of `matrix1` and `matrix2` by row or column.
    :param matrix1: pandas DataFrame;
    :param matrix2: pandas DataFrame;
    :param function: function; function used to compute association or dissociation
    :param axis: int; 0 for by-row and 1 for by-column
    :param is_distance: bool; True for distance and False for association
    :return: pandas DataFrame;
    """
    if axis == 0:
        m1 = matrix1.copy()
        m2 = matrix2.copy()
    else:
        m1 = matrix1.T
        m2 = matrix2.T

    compared_matrix = DataFrame(index=m1.index, columns=m2.index, dtype=float)
    nrow = m1.shape[0]
    for i, (i1, r1) in enumerate(m1.iterrows()):
        print_log('Comparing {} ({}/{}) vs. ...'.format(i1, i + 1, nrow))
        for i2, r2 in m2.iterrows():
            compared_matrix.ix[i1, i2] = function(r1, r2)

    if is_distance:
        print_log('Converting association to distance (1 - association) ...')
        compared_matrix = 1 - compared_matrix

    return compared_matrix
