from copy import copy
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from shapely import LineString, MultiLineString, MultiPoint, Point

MULTI_INDEX_SEPERATOR = "|"


def enlarge_index(index: pd.MultiIndex, max_levels: int, attr=None) -> List[Tuple]:
    """
    Enlarge the given index so that all levels have the depth of the maximum level.

    Args:
        index (pd.MultiIndex): The index to enlarge
        max_levels (int): The maximum index depth
        attr (Any, optional): An optional attribute prepended to the index. Defaults to None.

    Returns:
        List[Tuple]: A list of tuples representing the enlarged index

    Examples:
        This function is helpful if you concatenate `pd.DataFrame` s with different column levels as in the following
        examples::

            >>> df1 = pd.DataFrame(np.ones((2, 2)), columns=pd.MultiIndex.from_tuples([('a', 1), ('a',2)]))
            >>> df1
               a
               1    2
            0  1.0  1.0
            1  1.0  1.0

            >>> df2 = pd.DataFrame(np.ones((2, 2)), columns=['b', 'c'])
            >>> df2
                 b    c
            0  1.0  1.0
            1  1.0  1.0

            # The df1 has two levels but the df2 only one. After concatenation, the index is flattened
            >>> df3 = pd.concat([df1, df2], axis=1)
            >>> df3
               (a, 1)  (a, 2)    b    c
            0     1.0     1.0  1.0  1.0
            1     1.0     1.0  1.0  1.0

            # We can recover the multi-index columns by expanding each df's columns
            >>> c = [idx for df in [df1, df2] for idx in enlarge_index(df.columns, 2)]
            >>> c
            [('a', 1), ('a', 2), ('b', ''), ('c', '')]

            # and create a multi-index from the list of tuples
            >>> idx = pd.MultiIndex.from_tuples(c)
            >>> idx
            MultiIndex([('a',  1),
                        ('a',  2),
                        ('b', ''),
                        ('c', '')],
                       )

            >>> df3.columns = idx
            >>> df3
                 a         b    c
                 1    2
            0  1.0  1.0  1.0  1.0
            1  1.0  1.0  1.0  1.0


        You may also want to add a certain name to the index, i.e. add another level with a custom name. For that
        purpose, the optional `attr` parameter is available

            >>> c = [idx for df in [df1, df2] for idx in enlarge_index(df.columns, 2, 'test')]
            >>> c
            [('test', 'a', 1), ('test', 'a', 2), ('test', 'b', ''), ('test', 'c', '')]
    """

    indices = []
    for key_idx in range(len(index)):
        new_index = [attr, *[""] * max_levels]

        if attr is None:
            new_index = new_index[1:]

        offset = 1 if attr is not None else 0

        if index.nlevels > 1:
            for level_idx in range(len(index[0])):
                new_index[offset + level_idx] = index[key_idx][level_idx]
        else:
            new_index[offset] = index[key_idx]
        indices.append(tuple(new_index))
    return indices


def flatten_index(
    index: pd.MultiIndex, sep: str = None
) -> Optional[Union[pd.Index, pd.MultiIndex]]:
    """
    Get the reduced index removing all entries with *''*

    Args:
        index (pd.MultiIndex): The index to flatten

    Returns:
        Optional[Union[pd.Index, pd.MultiIndex]]: The columns without empty levels

    Examples:
        If you have a `pd.DataFrame` with a column having multiple levels and get an attribute with a lower level of
        columns, the additional empty level still exists. For that purpose, you can use this function to remove the
        obsolete index level.

            >>> df = pd.DataFrame([[1, 2, 3], [1, 2, 3]], columns=pd.MultiIndex.from_tuples([('a', 'b', ''), ('a', 'c', ''), ('d', 'e', 'f')]))
            >>> df
               a     d
               b  c  e
                     f
            0  1  2  3
            1  1  2  3

            # Accessing the column `b` gives access to the sup-column `c`
            >>> df.d
               e
               f
            0  3
            1  3

            # But, the value of `a` contains another blank line.
            >>> a = df.a
            >>> a
               b  c
            <BLANKLINE>
            0  1  2
            1  1  2

            # We may want to get rid of it. Note that you cannot update the column inplace.
            >>> a.columns = flatten_index(a.columns)
            >>> a
               b  c
            0  1  2
            1  1  2

    """

    if sep is not None:
        # flatten the pd.MultiIndex to an pd.Index by joining the values with a seperator
        return pd.Index([sep.join(filter(None, col)) for col in index.values])

    # get the maximum index depth
    levels = []
    for level in range(index.nlevels):
        level_values = index.get_level_values(level)

        if not (level_values == "").all():
            levels.append(level_values.values)

    if len(levels) > 1:
        return pd.MultiIndex.from_arrays(levels)
    else:
        try:
            return pd.Index(levels[0])
        except IndexError:
            # if the value has no valid index
            return pd.Index([])


def add_attributes(
    df1: Union[pd.DataFrame, Dict[str, Union[pd.Series, pd.DataFrame]]],
    df2: Optional[Union[pd.Series, pd.DataFrame]] = None,
    *args,
    keys: List[str] = None,
    copy: bool = False,
) -> pd.DataFrame:
    """
    Add the attributes in `df2` to the dataframe `df1` as new columns

    This function can be employed concatenate two dataframes or a dataframe and a series. This function ensures that
    pandas MultiIndex are not flattened.

    Args:
        df1 (Union[pd.DataFrame, Dict[str, Union[pd.Series, pd.DataFrame]]]): The first attribute or a dictionary of
        attributes
        df2 (Optional[Union[pd.Series, pd.DataFrame]], optional): The second attribute. Defaults to None.
        keys (List[str], optional): If the data should be copied. Defaults to None.
        copy (bool, optional): List of keys added as a new level to the columns. Defaults to False.

    Returns:
        pd.DataFrame: The concatenated dataframes


    Notes:
        If an attributes is a `pandas.Series` then this function assumes that this is an attribute with only one
        component but multiple measurements. In that case, this function assumes that the indices match with other
        specified series or dataframes. If the series has a name, this will be the column name in the final dataframe if
        and only if no key is given for that attributes.


    Examples:
        Add a new attribute to `df1` with `s2` as a simple `pandas.Series`.

            >>> df1 = pd.DataFrame({'a' : [1, 2], 'b' : [3, 4]})
            >>> df1
               a  b
            0  1  3
            1  2  4

            >>> s2 = pd.Series([5, 6], name='c')
            >>> s2
            0    5
            1    6
            Name: c, dtype: int64

            >>> add_attributes(df1, s2, copy=True)
               a  b  c
            0  1  3  5
            1  2  4  6

        We can also concatenate multiple attributes sharing the same index

            >>> df2 =  pd.DataFrame({'c' : [5, 6], 'd' : [7, 8]})
            >>> df2
               c  d
            0  5  7
            1  6  8

            >>> add_attributes(df1, df2)
               a  b  c  d
            0  1  3  5  7
            1  2  4  6  8

        Moreover, this function makes it easy to concatenate attributes having multiple levels of components

            >>> df3 = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=pd.MultiIndex.from_tuples([('e', 'A'), ('e', 'B'), ('f', '')]))
            >>> df3
               e     f
               A  B
            0  1  2  3
            1  4  5  6

            >>> add_attributes(df1, df3, copy=False)
               a  b  e     f
                     A  B
            0  1  3  1  2  3
            1  2  4  4  5  6

        We can also concatenate multiple attributes at once

            >>> add_attributes(df1, df2, df3)
               a  b  c  d  e     f
                           A  B
            0  1  3  5  7  1  2  3
            1  2  4  6  8  4  5  6

        and add another level of columns so it

            >>> add_attributes(df1, df2, df3, keys=['U', 'V', 'W'])
               U     V     W
               a  b  c  d  e     f
                           A  B
            0  1  3  5  7  1  2  3
            1  2  4  6  8  4  5  6

        The same result can be achived with the second interface of the function using a dictionary.

            >>> add_attributes({'U' : df1, 'V' : df2, 'W' : df3})
               U     V     W
               a  b  c  d  e     f
                           A  B
            0  1  3  5  7  1  2  3
            1  2  4  6  8  4  5  6

            >>> add_attributes({'U' : df1, 'V' : df2, '' : df3})
               U     V     e     f
               a  b  c  d  A  B
            0  1  3  5  7  1  2  3
            1  2  4  6  8  4  5  6

        The function is also able to add attributes with different level of columns

            >>> df3
               e     f
               A  B
            0  1  2  3
            1  4  5  6

            >>> df1
               a  b
            0  1  3
            1  2  4

            >>> add_attributes(df3, df1)
               e     f  a  b
               A  B
            0  1  2  3  1  3
            1  4  5  6  2  4

            >>> add_attributes(df1, df3)
               a  b  e     f
                     A  B
            0  1  3  1  2  3
            1  2  4  4  5  6

            >>> s1 = pd.Series([10, 11], name='g')
            >>> s1
            0    10
            1    11
            Name: g, dtype: int64

            >>> add_attributes(df3, s1)
               e     f   g
               A  B
            0  1  2  3  10
            1  4  5  6  11


    """

    if isinstance(df1, dict):
        # Get all attributes names and values
        values = list(df1.values())
        keys = list(df1.keys())
    else:
        # Get all attributes values. The keys might be in the keys variable (are optional, though)
        values = [df1, df2, *args]

    # convert all series to dataframes
    collection = []

    for d_idx, d in enumerate(values):
        if isinstance(d, pd.Series):
            df = d.to_frame()

            # if keys are given, reset the current column name
            if keys and len(keys) > d_idx and keys[d_idx] != "":
                df.columns = [""]

            collection.append(df)
        else:
            collection.append(d)

    try:
        # add the boundingbox information to the attributes
        df = pd.concat(collection, axis=1, keys=keys, copy=copy)
    except AssertionError:
        df = pd.concat(collection, axis=1, keys=keys, copy=copy, ignore_index=True)

    # if the columns levels do not match, recover the multi index
    levels = [d.columns.nlevels for d in collection]

    if np.unique(levels).size > 1:

        # get the maximum number of column levels
        levels = np.max(levels)

        # recover the correct multi-index and append the key if specified. For single component attributes and a given
        # key, just set the upper-level attribute name
        df.columns = flatten_index(
            pd.MultiIndex.from_tuples(
                [
                    c
                    for d in [
                        enlarge_index(
                            c, levels if k != "" else levels + 1, k if k != "" else None
                        )
                        for c, k in zip(
                            [df.columns for df in collection],
                            keys if keys is not None else [None] * len(collection),
                        )
                    ]
                    for c in d
                ]
            )
        )

    return df


def to_pandas_multiindex(
    values: List[str], separator=MULTI_INDEX_SEPERATOR
) -> pd.MultiIndex:
    """
    Convert a list of nested names to a `pandas.MultiIndex`.

    Args:
        values (List[str]): The list of names joined by the `separator`
        separator (str, optional): The character used as separator. Defaults to `MULTI_INDEX_SEPERATOR`.

    Returns:
        pd.MultiIndex: The list of nested names converted to a `pandas.MultiIndex`

    Examples:
        This function can be employed if you have a list of attributes names where the attributes are hierarchical.
        Let's assume we have the attribute `a` with the components `b` and `c` and the attribute `v` with the components
        `x` and `y` which are joined by the separator `|` so that there is a list with the values `['a|b', 'a|c', 'v|x',
        'v|y']` we want to convert to a `pandas.MultiIndex` since this is used to manage hierarchical attributes.
        Therefore, we can use this function with::

            >>> attributes = ['a|b', 'a|c', 'v|x', 'v|y']
            >>> to_pandas_multiindex(attributes)
            MultiIndex([('a', 'b'),
                        ('a', 'c'),
                        ('v', 'x'),
                        ('v', 'y')],
                       )

    """

    # get the maximum number of multiindex rows
    depth = max([c.count(separator) for c in values]) + 1

    if depth == 1:
        return values

    names = []
    # for each attribute get the corresponding columns
    for attr in values:
        values = attr.split(separator)

        # get the missing inner names
        missing_names = depth - len(values)

        # append the missing names
        if missing_names > 0:
            values.extend([""] * missing_names)

        names.append(values)

    # to set the name of the columns with a multiindex we need to transpose the list of columns names from a
    # column-wise to a row-wise representation
    return pd.MultiIndex.from_arrays(np.array(names).T)


def position_to_point(df: pd.DataFrame, position: Any) -> Union[Point, MultiPoint]:
    """
    Convert the position to a shapely Point

    Args:
        position (Any): The position to convert

    Raises:
        ValueError: If the position is unsupported

    Returns:
        Union[Point, MultiPoint]: Either a single Point or multiple Points for nested positions.
    """
    df = df.sort_index(axis=1)

    values = df[position]

    # get the flatten columns (remove empty levels)
    flat_columns = flatten_index(values.columns)

    if flat_columns.nlevels == 2:
        # nested position attributes
        return MultiPoint(
            [
                position_to_point(df, (position, p))
                for p in values.columns.get_level_values(0)
            ]
        )

    elif flat_columns.nlevels == 1:
        # single position attribute
        return Point(values.values[:, :2])
    else:
        # unsupported position attribute
        raise ValueError(f"Unsupported position {position}")


def position_to_linestring(
    df: pd.DataFrame, position: Any
) -> Union[LineString, MultiLineString]:
    """
    Convert the position to a shapely LineString

    Args:
        position (Any): The position to convert

    Raises:
        ValueError: If the position is unsupported

    Returns:
        Union[LineString, MultiLineString]: Either a single LineString or multiple LineStrings for nested positions.
    """
    df = df.sort_index(axis=1)

    values = df[position]

    # get the flatten columns (remove empty levels)
    flat_columns = flatten_index(values.columns)

    if flat_columns.nlevels == 2:
        # nested position attributes
        return MultiLineString(
            [
                position_to_linestring(df, (position, p))
                for p in values.columns.get_level_values(0)
            ]
        )

    elif flat_columns.nlevels == 1:
        # single position attribute
        return LineString(values.values[:, :2])
    else:
        # unsupported position attribute
        raise ValueError(f"Unsupported position {position}")
