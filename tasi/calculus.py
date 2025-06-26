import logging
from numbers import Number
from typing import List, Union

import numpy as np
import pandas as pd
from numba import float32, float64, jit, njit

#: Type definition for a 8 bit floating point number
Double = float64  # type: ignore

#: Type definition for a 8 bit floating point vector
DoubleVector = Double[:]

#: Type definition for a 8 bit floating point matrix
DoubleMatrix = Double[:, :]

#: Type definition for a 4 bit floating point value
Float = float32  # type: ignore

#: Type definition for a 4 bit floating point vector
FloatVector = float32[:]  # type: ignore

#: Type definition for a 4 bit floating point matrix
FloatMatrix = float32[:, :]  # type: ignore

#: Type definition for a 4 bit floating point vector or matrix
FloatVecOrMat = Union[FloatVector, FloatMatrix]


def dot(v1: FloatVector, v2: FloatVector):
    """
    The dot product between ``v1`` and ``v2``.

    The functions uses the Einstein-Summation-Convention for the dot product between either a matrix of column vectors
    and a single vector or multiple vectors (also as column vectors).

    Args:
        v1 (FloatVector): A M*2 matrix
        v2 (FloatVector): Either a 2*1 vector or a M*2 matrix.

    Returns:
        FloatVector: A 1*M vector with the dot product

    See Also:
        vdot: For a vectorized version of the dot product

    Examples:
        The dot product between a matrix and a vector

            >>> m1 = np.array([[1, 1], [2, 2], [3, 3]]).T
            >>> m1
            array([[1, 2, 3],
                   [1, 2, 3]])

            >>> v1 = np.array([1, 0])
            >>> dot(m1, v1)
            array([1, 2, 3])

        or to multiple vectors column-wise

            >>> m2 = np.array([[1, 0], [0, 1], [1, 0]]).T
            >>> m2
            array([[1, 0, 1],
                   [0, 1, 0]])

            >>> dot(m1, m2)
            array([1, 2, 3])

    """
    if len(v2.shape) == 1:
        return np.einsum("ij, i -> j", v1, v2)
    return np.einsum("ij, ij -> j", v1, v2)


@njit(fastmath=True)
def _vrotation_matrix(theta):  # pragma: no cover

    # preallocate matrices for rotation matrix
    k = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.float64)
    I = np.identity(3)
    k_m_k = k @ k

    # get adjacent and oppsite sides based on angles
    theta_sin = np.sin(theta)
    theta_cos = np.cos(theta)

    # first term is sin component
    arr_sin = np.expand_dims(k[:, :], -1) * theta_sin

    # second term is cos componet
    arr_cos = np.expand_dims(k_m_k, -1) * (1 - theta_cos)

    # combine everything and ensure the result is of shape (3n x 3)
    return (np.expand_dims(I, -1) + arr_sin + arr_cos).transpose(2, 0, 1)


@jit(nopython=True)
def calc_rotation_matrices(theta: np.ndarray) -> np.ndarray:  # pragma: no cover
    """
    Get the rotation matrix for counterclockwise rotation by the given radians.

    Args:
        theta (float): The angle in radians and within [-pi, pi]

    Raises:
        ValueError: [description]

    Returns:
        np.ndarray: A 3*3 matrix rotation matrix

    Examples:
        Estimate the rotation matrix for multiple angles

            >>> theta = np.array([0, np.pi/2, np.pi])
            >>> calc_rotation_matrices(theta)
            array([[[ 1.,  0.,  0.],
                    [ 0.,  1.,  0.],
                    [ 0.,  0.,  1.]],
            <BLANKLINE>
                   [[ 0., -1.,  0.],
                    [ 1.,  0.,  0.],
                    [ 0.,  0.,  1.]],
            <BLANKLINE>
                   [[-1., -0.,  0.],
                    [ 0., -1.,  0.],
                    [ 0.,  0.,  1.]]])
    """
    return _vrotation_matrix(theta.ravel())


@jit(nopython=True)
def calc_rotation_matrix(theta: np.float64) -> np.ndarray:  # pragma: no cover
    """
    Get the rotation matrix for counterclockwise rotation by the given angle in radians.

    Args:
        theta (float): The angle in radians and within [-pi, pi]

    Returns:
        np.ndarray: A 3*3 matrix rotation matrix

    Examples:
        Estimate the rotation matrix for multiple angles

            >>> calc_rotation_matrix(0.)
            array([[1., 0., 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]])
            >>> calc_rotation_matrix(np.pi / 2)
            array([[ 0., -1.,  0.],
                   [ 1.,  0.,  0.],
                   [ 0.,  0.,  1.]])
            >>> calc_rotation_matrix(np.pi)
            array([[-1., -0.,  0.],
                   [ 0., -1.,  0.],
                   [ 0.,  0.,  1.]])
    """
    return calc_rotation_matrices(np.array(theta))[0]


def _rotate_single_vector(vector: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate the vector about angle radians

    Args:
        vector (np.ndarray): The vector to rotate as a 1*3 array
        angle (float): The rotation magnitude in radians

    Returns:
        np.ndarray: The rotated vector

    Examples:
        Rotate the unit vector of the ``x-axis`` in 3D around the ``z-axis`` about ``90 degrees`` counterclockwise.

            >>> v = np.array([1, 0])
            >>> v
            array([1, 0])

            >>> theta = np.pi / 2
            >>> _rotate_single_vector(v, theta)
            array([0.,  1.])

    """

    if vector.size < 3:
        vector = np.append(vector, 0)

    # get the rotation matrix for that angle only once
    matrix = calc_rotation_matrix(angle)

    # estimate dot product for each matrix and vector (2D with 2D matrix)
    return np.einsum("ij, j -> i", matrix, vector)[:2]


def _make_3d_vectors(vectors):
    """
    Make the given vectors 3D

    Args:
        vectors (np.ndarray): A P*2 or P*3 matrix of vectors

    Returns:
        np.ndarray: A P*3 matrix of vectors with the last component as a vector of zeros

    Examples:

        >>> import numpy as np
        >>> _make_3d_vectors(np.asarray([[1, 0]],  dtype=np.float64))
        array([[1., 0., 0.]])

    """
    if vectors.shape[1] < 3:
        vectors3d = np.zeros((vectors.shape[0], vectors.shape[1] + 1))
        vectors3d[:, :-1] = vectors
        vectors = vectors3d

    return vectors


def _rotate_vectors_single_angle(vectors: np.ndarray, angle: float):
    """
    Rotate the vectors by the given angle

    Args:
        vectors (np.ndarray): A P*3 matrix of vectors with P as the number of vectors
        angle (float): The angle to rotate the vectors about. In mathematical sense and radians.

    Returns:
        np.ndarray: The rotate vectors as P*2 matrix
    """
    # get the rotation matrix for that angle only once
    matrix = calc_rotation_matrix(angle)

    vectors = _make_3d_vectors(vectors)

    # estimate dot product for a matrix A and vector B as A.dot(B.T).T without two transposes
    return np.einsum("ij, kj -> ki", matrix, vectors)[:, :2]


def _rotate_vectors_multiple_angles(vectors: np.ndarray, angles: np.ndarray):
    """
    Rotate each vectors by its rotation angle

    Args:
        vectors (np.ndarray): A P*2 matrix of vectors with P as the number of vectors
        angles (np.ndarray): A P vector of rotation ss. In mathematical sense and radians.

    Raises:
        ValueError: If the number of vectors and rotation angles do not match.
    Returns:
        np.ndarray: The rotatet vectors as a P*2 matrix.
    """
    if not vectors.shape[0] == angles.shape[0]:
        raise ValueError(
            "The number of vectors must match with the number of rotation angles"
        )

    vectors = _make_3d_vectors(vectors)

    matrices = calc_rotation_matrices(angles)

    # estimate dot product for each matrix (3D with 2D matrix)
    return np.einsum("aij, aj -> ai", matrices, vectors)[:, :2]


def rotate_points(
    points: np.ndarray, angle: Union[float, List[float]], degree: bool = True
):
    """
    Rotate the point(s) according to the given angle

    Args:
        points (np.ndarray): P*2 array with P as the number of points
        angle (float): The angle to rotate the points
        degree (bool):  If the angle is in degree. By default, we assume radians.

    Returns:
        np.ndarray: The rotated points

    Examples:

        You can use the function different ways. For instance, you can rotate a single vector by a single angle

            >>> import numpy as np
            >>> rotate_points(np.array([1, 0], dtype=np.float64), np.pi / 2, degree=False)
            array([0., 1.])

            >>> rotate_points(np.array([1, 0], dtype=np.float64), np.pi, degree=False)
            array([-1., 0.])

            >>> rotate_points(np.array([[1, 0], [1, 0]], dtype=np.float64), np.pi, degree=False)
            array([[-1., 0.],
                   [-1., 0.]])
    """
    if degree:
        angle = np.radians(angle)
    else:
        # ensure value is always a numpy object
        angle = np.float64(angle)
    if angle.size == 1:
        # if angle has only one element, ensure it is not a vector
        try:
            angle = angle[0]
        except IndexError:
            pass

    if len(points.shape) == 1 or points.shape[0] == 1:
        # rotate a single vector according to a single angle

        points = points.ravel()  # ensure points is a vector

        if points.size < 3:
            # ensure the length of points is three
            points = np.append(points, 0)

        return _rotate_single_vector(points, angle)[:2]

    if points.shape[1] < 3:
        points3d = np.zeros((points.shape[0], points.shape[1] + 1))
        points3d[:, :-1] = points
        points = points3d

    if angle.size == 1:
        return _rotate_vectors_single_angle(points, angle)

    # ensure the angle is a vector by raveling the array
    return _rotate_vectors_multiple_angles(points, np.ascontiguousarray(angle.ravel()))


def calc_velocity_from_origins(origins: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate the velocities based on the given vehicle origins

    Args:
        origins (pd.DataFrame): A n*3 array of (timestamp, x, y) timstamped coordinates in UTM.

    Note:
        The first column of the array is used as time-reference.

    Returns:
        pd.DataFrame: The estimated velocities in (x, y)

        The result is an (n-1) * 2 dataframe in meter per second. The first value denotes the velocity
        between t=0 and t=1.
    """
    # estimate the velocity for each point in time
    magnitude = origins.diff().dropna()

    timestamps = magnitude.index.get_level_values("timestamp").values

    velocity = magnitude.iloc[1:].div(
        (np.diff(timestamps) / np.timedelta64(1, "s")),
        axis=0,
    )
    return velocity


def calc_acceleration_from_origins(origins: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate the acceleration based on the given vehicle origins

    Args:
        origins (pd.DataFrame): A n*3 array of (timestamp, x, y) timstamped coordinates in UTM.

    Note:
        The index is used as time-reference.

    Returns:
        pd.DataFrame: The estimated acceleration in (x, y)

        The result is an (n-2) * 2 dataframe in meter per second. The first value denotes the velocity
        between t=1 and t=2.
    """

    return calc_velocity_from_origins(calc_velocity_from_origins(origins))


def calc_yaw_rate_from_headings(headings: pd.Series, math_range=False) -> pd.Series:
    """
    Estimate the yaw rate based on the given vehicle headings

    Args:
        headings (pd.Series): An array of headings of (x,y) coordinates in UTM and the time as the index.

    Note:
        The index of the given dataframe has to timestamps.

    Returns:
        pd.Series: The yaw rates as (n-1) array.
    """
    headings = headings.copy()

    if not math_range:
        headings.loc[headings > 180] = headings.loc[headings > 180] - 360

    angle_diff = headings.diff().dropna()
    angle_diff[angle_diff > 180] -= 360
    angle_diff[angle_diff < -180] += 360

    timestamps = headings.index.get_level_values("timestamp").values

    return pd.Series(
        angle_diff / (np.diff(timestamps) / np.timedelta64(1, "s")),
        index=headings.index[1:],
        name="yaw_rate",
    )


def boundingbox_from_dimension(
    df_dimension: pd.DataFrame,
    heading: Union[pd.Series, pd.DataFrame],
    relative_to: pd.DataFrame,
):

    index = (
        heading.index
        if isinstance(heading, (pd.Series, pd.DataFrame))
        else dimension.index if isinstance(dimension, pd.DataFrame) else None
    )

    if heading is None:
        # by default, rotate by zero degrees
        heading = np.asarray([0])
    elif isinstance(heading, Number):
        # ensure heading is always as numpy array
        heading = np.asarray([heading])
    elif isinstance(heading, list):
        heading = np.asarray(heading)

    if len(relative_to.shape) == 1:
        relative_to = relative_to.reshape(-1, 2)

    extend_to = np.max([heading.size, relative_to.shape[0], df_dimension.shape[0]])

    if df_dimension.shape[0] != extend_to:
        points = pd.DataFrame(
            np.repeat(df_dimension.values, extend_to, axis=0),
            columns=df_dimension.columns,
        )

    if relative_to.shape[0] != extend_to:
        relative_to = np.repeat(relative_to, extend_to, axis=0)

    # create the boundingbox points and rotate them
    ps = []
    for x1, x2 in zip(
        [-0.5, 0, 0.5, 0.5, 0.5, 0, -0.5, -0.5], [0.5, 0.5, 0.5, 0, -0.5, -0.5, -0.5, 0]
    ):

        points = np.array([x1 * df_dimension.length, x2 * df_dimension.width]).T

        if points.shape[0] != extend_to:
            points = np.repeat(points, extend_to, axis=0)

        ps.append(relative_to + rotate_points(points, heading.to_numpy(), degree=True))

    bbox = np.hstack(ps)

    return pd.DataFrame(
        bbox,
        columns=pd.MultiIndex.from_product(
            [
                [
                    "rear_left",
                    "left",
                    "front_left",
                    "front",
                    "front_right",
                    "right",
                    "rear_right",
                    "rear",
                ],
                ["easting", "northing"],
            ]
        ),
        index=index,
    )
