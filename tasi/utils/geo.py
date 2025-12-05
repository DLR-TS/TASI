from typing import Any, Union, overload

import numpy as np
import pandas as pd
from shapely import GeometryCollection, LineString, MultiLineString, MultiPoint, Point

from tasi.utils.base import flatten_index

__all__ = ["position_to_point", "position_to_linestring"]

BasicGeometry = Union[Point, LineString]
MultiGeometry = Union[GeometryCollection, MultiPoint, MultiLineString]


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

    values = df[position][["easting", "northing"]]

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

    values = df[position][["easting", "northing"]]

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


@overload
def geometry_to_coords(obj: BasicGeometry, **kwargs) -> np.ndarray | None: ...


@overload
def geometry_to_coords(
    obj: Union[GeometryCollection, MultiPoint, MultiLineString], **kwargs
) -> np.ndarray | None: ...


def geometry_to_coords(
    obj: Union[BasicGeometry, MultiGeometry],
    return_first: bool = True,
    **kwargs,
) -> np.ndarray | None:
    """
    Returns the coordinates of the first point of a Shapely object.

    Args:
        geom (Union[BasicGeometry, BasicGeometry]): A Shapely object
        return_first (bool, optional): If the first geometry should be returned

    Returns:
        np.ndarray | None: A NumPy array with the coordinates or None if the geometry is empty.

    Raises:
        TypeError: If the input geometry type is unsupported.

    Notes:
        If the given object contains multiple points, the first one is selected.
    """

    if isinstance(obj, BasicGeometry):

        if obj.is_empty:
            return None

        return np.array(obj.coords[0])

    elif isinstance(obj, MultiGeometry):

        if obj.is_empty:
            return None

        if return_first:
            return geometry_to_coords(list(obj.geoms)[0])  # type: ignore
        else:
            return geometry_to_coords(list(obj.geoms)[-1])  # type: ignore
    else:
        raise TypeError(f"Unsupported geometry type: {type(obj)}")
