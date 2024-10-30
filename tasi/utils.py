from typing import List
import numpy as np
import pandas as pd
from copy import copy


def to_pandas_multiindex(values: List[str], separator='_') -> pd.MultiIndex:
    """
    Convert a list of nested names to a `pandas.MultiIndex`.

    Args:
        values (List[str]): The list of names joined by the `separator`
        separator (str, optional): The character used as separator. Defaults to '_'.

    Returns:
        pd.MultiIndex: The list of nested names converted to a `pandas.MultiIndex`

    Examples:
        This function can be employed if you have a list of attributes names where the attributes are hierarchical.
        Let's assume we have the attribute `a` with the components `b` and `c` and the attribute `v` with the components
        `x` and `y` which are joined by the separator `|` so that there is a list with the values `['a|b', 'a|c', 'v|x',
        'v|y']` we want to convert to a `pandas.MultiIndex` since this is used to manage hierarchical attributes.
        Therefore, we can use this function with::

            >>> attributes = ['a|b', 'a|c', 'v|x', 'v|y']
            >>> to_pandas_multiindex(attributes, separator='|')
            MultiIndex([('a', 'b'),
                        ('a', 'c'),
                        ('v', 'x'),
                        ('v', 'y')],
                       )

    """

    columns = copy(values)

    # get the maximum number of multiindex rows
    depth = max([c.count(separator) for c in columns]) + 1

    names = []
    # for each attribute get the corresponding columns
    for attr in values:
        values = attr.split(separator)

        # get the missing inner names
        missing_names = depth - len(values)

        # append the missing names
        if missing_names > 0:
            values.extend([''] * missing_names)

        names.append(values)

    # to set the name of the columns with a multiindex we need to transpose the list of columns names from a
    # column-wise to a row-wise representation
    return pd.MultiIndex.from_arrays(np.array(names).T)
