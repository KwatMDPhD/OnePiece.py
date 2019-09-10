def merge_2_dicts_recursively(dict_0, dict_1):

    dict_ = {}

    for key in dict_0.keys() | dict_1.keys():

        if key in dict_0 and key in dict_1:

            value_0 = dict_0[key]

            value_1 = dict_1[key]

            if isinstance(value_0, dict) and isinstance(value_1, dict):

                dict_[key] = merge_2_dicts_recursively(value_0, value_1)

            else:

                dict_[key] = value_1

        elif key in dict_0:

            dict_[key] = dict_0[key]

        elif key in dict_1:

            dict_[key] = dict_1[key]

    return dict_
