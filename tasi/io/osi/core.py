from datetime import datetime
from pathlib import Path
from typing import Generator, List, Sequence, Tuple, Union, overload

from betterosi import (
    GroundTruth,
    GroundTruthProjFrameOffset,
    Identifier,
    InterfaceVersion,
    MovingObject,
    Vector3D,
    Writer,
)
from betterosi import read as read_osi
from pyproj import CRS

from tasi import Pose, Trajectory, TrajectoryDataset
from tasi._version import __version_tuple__
from tasi.io import TrajectoryPublic

from .conversion import (
    convert_ground_truth,
    convert_ground_truths,
    convert_moving_object,
    convert_trajectories,
)
from .util import resolve_countrycode


@overload
def convert(
    obj: Sequence[GroundTruth],
    time: datetime,
    offset: None = None,
    **kwargs: object,
) -> List[Trajectory]: ...


@overload
def convert(
    obj: GroundTruth,
    time: datetime | None = None,
    offset: None = None,
    **kwargs: object,
) -> List[Pose]:
    """Convert a GroundTruth element into a TASI list of TASI Poses

    Args:
        obj (GroundTruth): The OSI element
        time (datetime, optional): The time origin as reference

    Returns:
        List[Pose]: A TASI Pose per MovingObject in the GroundTruth element
    """
    ...


@overload
def convert(
    obj: MovingObject,
    time: datetime | None = None,
    offset: None = None,
    **kwargs: object,
) -> Pose:
    """Convert a MovingObject element into a TASI Pose

    Args:
        obj (MovingObject): The OSI element
        time (datetime, optional): The time origin as reference

    Returns:
        Pose: A TASI Pose
    """
    ...


@overload
def convert(
    obj: TrajectoryDataset,
    time: datetime | None = None,
    offset: Tuple[float, float] = ...,
) -> List[GroundTruth]:
    """Convert a TrajectoryDataset to GroundTruth objects

    Args:
        obj (TrajectoryDataset): The dataset to convert
        time (datetime, optional): The time origin as reference
        offset (tuple[float, float]): Offset applied to the object positions.

    Returns:
        List[GroundTruth]: Representation of the trajectories in ASAM OSI as
        GroundTruth messages.
    """
    ...


@overload
def convert(
    obj: List[TrajectoryPublic],
    time: datetime | None = None,
    offset: Tuple[float, float] = ...,
) -> List[GroundTruth]:
    """Convert a list of TrajectoryPublic to GroundTruth objects

    Args:
        obj (List[TrajectoryPublic]): The trajectories to convert
        time (datetime, optional): The time origin as reference
        offset (tuple[float, float]): Offset applied to the object positions.

    Returns:
        List[GroundTruth]: Representation of the trajectories in ASAM OSI as
        GroundTruth messages.
    """
    ...


@overload
def convert(
    obj: List[Trajectory],
    time: datetime | None = None,
    offset: Tuple[float, float] = ...,
) -> List[GroundTruth]:
    """Convert a list of Trajectory to GroundTruth objects

    Args:
        obj (List[Trajectory]): The trajectories to convert
        time (datetime, optional): The time origin as reference
        offset (tuple[float, float]): Offset applied to the object positions.

    Returns:
        List[GroundTruth]: Representation of the trajectories in ASAM OSI as
        GroundTruth messages.
    """
    ...


def convert(
    obj: Union[
        Sequence[GroundTruth],
        GroundTruth,
        MovingObject,
        TrajectoryDataset,
        List[TrajectoryPublic],
        List[Trajectory],
    ],
    time: datetime | None = None,
    offset: Tuple[float, float] | None = None,
    **kwargs: object,
) -> Union[Pose, List[Pose], List[Trajectory], List[GroundTruth]]:
    """Convert a OSI object into a TASI compatible object or vice versa

    Args:
        obj (Union[Sequence[GroundTruth], GroundTruth, MovingObject,
            TrajectoryDataset, List[TrajectoryPublic], List[Trajectory]]):
            Either an OSI element or TASI entity
        time (datetime, optional): The time origin as reference
        offset (Tuple[float, float], optional): Offset for TASI to OSI conversion

    Raises:
        ValueError: If an unsupported OSI element is provided

    Returns:
        Union[Pose, List[Pose], List[Trajectory], List[GroundTruth]]:
            A TASI entity or List[GroundTruth] for OSI conversion
    """
    # TASI -> OSI conversion
    if isinstance(obj, TrajectoryDataset):
        if offset is None:
            raise ValueError("offset is required for TASI to OSI conversion")
        trajectories: List[Trajectory] = [obj.trajectory(id_) for id_ in obj.ids]
        # ensure public trajectories
        if isinstance(trajectories[0], Trajectory):
            trajectories = [TrajectoryPublic.from_tasi(tj) for tj in trajectories]  # type: ignore[assignment]
        # convert to OSI
        return convert_trajectories(trajectories, offset=offset)  # type: ignore[arg-type]
    elif (
        isinstance(obj, list)
        and obj
        and isinstance(obj[0], (TrajectoryPublic, Trajectory))
    ):
        if offset is None:
            raise ValueError("offset is required for TASI to OSI conversion")
        # Type narrow: obj is either List[TrajectoryPublic] or List[Trajectory]
        if isinstance(obj[0], Trajectory):
            trajectories: List[Trajectory] = obj  # type: ignore[assignment]
            trajectories = [TrajectoryPublic.from_tasi(tj) for tj in trajectories]  # type: ignore[assignment]
        else:
            trajectories = obj  # type: ignore[assignment]
        # convert to OSI
        return convert_trajectories(trajectories, offset=offset)  # type: ignore[arg-type]

    # OSI -> TASI
    if obj and isinstance(obj, (list, tuple, Generator)):
        # Type narrow: obj is Sequence[GroundTruth] at this point
        # Ensure time is not None for convert_ground_truths
        time_val = time if time is not None else datetime.fromtimestamp(0)
        return [o.as_tasi() for o in convert_ground_truths(obj, time=time_val, **kwargs)]  # type: ignore[arg-type]
    elif isinstance(obj, GroundTruth):
        time_val = time if time is not None else datetime.fromtimestamp(0)
        return [o.as_tasi() for o in convert_ground_truth(obj, time=time_val, **kwargs)]
    elif isinstance(obj, MovingObject):
        time_val = time if time is not None else datetime.fromtimestamp(0)
        # Filter kwargs to only pass valid arguments (exclude 'index' which expects int)
        mov_obj_kwargs = {k: v for k, v in kwargs.items() if k != "index"}
        return convert_moving_object(obj, time=time_val, **mov_obj_kwargs).as_tasi()  # type: ignore[arg-type]

    raise ValueError(f"The given object {type(obj)} is not supported.")


def read(
    path: Union[str, Path], time: datetime = datetime.fromtimestamp(0)
) -> TrajectoryDataset:
    """Read a OSI file

    Args:
        path (Union[str, Path]): The path to the OSI file
        time (datetime, optional): The origin as reference

    Raises:
        RuntimeError: If there are no GroundTruth elements in the file

    Returns:
        TrajectoryDataset: A dataset of TASI trajectories
    """
    if isinstance(path, Path):
        path = str(path)

    # read the OSI file using betterosi
    gts: List[GroundTruth] = read_osi(path, return_ground_truth=True)

    if not gts:
        raise RuntimeError("There are no GroundTruth elements in the osi file.")

    # convert all moving objects into a TASI Dataset of trajectories
    return TrajectoryDataset.from_trajectories(convert(gts, time))


def write(
    obj: Union[TrajectoryDataset, List[TrajectoryPublic], List[Trajectory]],
    path: Union[str, Path],
    offset: Tuple[float, float],
    ego: int,
    epsg: int = 32632,
) -> str:
    if isinstance(path, Path):
        path = str(path)

    # ensure file ends with .osi
    path = path.split(".")[0] + ".osi"

    # convert to GroundTruth messages
    gts = convert(obj, offset=offset)

    with Writer(path) as writer:

        # specify converter version
        version = InterfaceVersion(*tuple(map(int, __version_tuple__[:3])))

        # specify country code
        country_code = resolve_countrycode(obj, epsg=epsg)

        crs = CRS.from_epsg(epsg).to_proj4()

        for gt in gts:

            # set attributes for every time steo
            gt.version = version
            gt.country_code = country_code
            gt.proj_string = crs
            gt.host_vehicle_id = Identifier(value=ego)

            # we have no offset since we are using UTM coordinates
            gt.proj_frame_offset = GroundTruthProjFrameOffset(
                position=Vector3D(x=offset[0], y=offset[1], z=0)
            )

            writer.add(gt)

    return path
