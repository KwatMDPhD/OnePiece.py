from pandas import DataFrame, read_csv
from scipy.io import mmread


def read_matrix_market(
    matrix_mtx_file_path,
    index_file_path,
    column_file_path,
    index_name=None,
    column_name=None,
):

    index_file = read_csv(index_file_path, sep="\t", header=None)

    index_file_column = 1

    print(
        f"Index File (using column {index_file_column} as feature):\n{index_file.head()}"
    )

    dataframe = DataFrame(
        mmread(matrix_mtx_file_path).toarray(),
        index=index_file.iloc[:, index_file_column],
        columns=read_csv(column_file_path, sep="\t", header=None, squeeze=True),
    )

    if dataframe.index.has_duplicates:

        print("Merging duplicated index with median ...")

        dataframe = dataframe.groupby(level=0).median()

    dataframe.sort_index(inplace=True)

    dataframe.index.name = index_name

    if dataframe.columns.has_duplicates:

        print("Merging duplicated column with median ...")

        dataframe = dataframe.T.groupby(level=0).median().T

    dataframe.sort_index(axis=1, inplace=True)

    dataframe.columns.name = column_name

    return dataframe