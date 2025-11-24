from typing import Any, Union

import pandas as pd
from shapely import LineString, MultiLineString, MultiPoint, Point

from .base import flatten_index

__all__ = ["position_to_point", "position_to_linestring"]


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
