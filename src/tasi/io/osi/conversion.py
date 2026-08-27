from bisect import insort
from datetime import datetime, timedelta, timezone
from itertools import repeat
from typing import Dict, List, Sequence, Tuple

from betterosi import (
    BaseMoving,
    Dimension3D,
    GroundTruth,
    Identifier,
    MovingObject,
    MovingObjectType,
    MovingObjectVehicleClassification,
)
from betterosi import MovingObjectVehicleClassificationType as OSIType
from betterosi import Orientation3D, Timestamp, Vector3D

from tasi.io import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    PosePublic,
    Position,
    TrafficParticipant,
    TrajectoryPublic,
    Velocity,
)
from tasi.io.public.base import Vector3DBase

OSI2TASI_MAPPING = {
    OSIType.BICYCLE: "bicycle",
    OSIType.BUS: "truck",
    OSIType.UNKNOWN: "unknown",
    OSIType.OTHER: "other",
    OSIType.SMALL_CAR: "car",
    OSIType.COMPACT_CAR: "car",
    OSIType.CAR: "car",
    OSIType.MEDIUM_CAR: "car",
    OSIType.LUXURY_CAR: "car",
    OSIType.DELIVERY_VAN: "van",
    OSIType.HEAVY_TRUCK: "truck",
    OSIType.SEMITRACTOR: "truck",
    OSIType.SEMITRAILER: "other",
    OSIType.TRAILER: "other",
    OSIType.MOTORBIKE: "motorbike",
    OSIType.BUS: "truck",
    OSIType.TRAM: "other",
    OSIType.TRAIN: "other",
    OSIType.WHEELCHAIR: "pedestrian",
    OSIType.STANDUP_SCOOTER: "pedestrian",
}


TASI2OSI_MAPPING = {
    "bicycle": OSIType.BICYCLE,
    "truck": OSIType.BUS,
    "unknown": OSIType.UNKNOWN,
    "other": OSIType.OTHER,
    "car": OSIType.CAR,
    "van": OSIType.DELIVERY_VAN,
    "truck": OSIType.HEAVY_TRUCK,
    "motorbike": OSIType.MOTORBIKE,
}


def convert_ground_truths(
    obj: Sequence[GroundTruth], time: datetime = datetime.fromtimestamp(0)
) -> List[TrajectoryPublic]:

    poses: Dict[int, List[PosePublic]] = {}
    for gt in obj:
        gt_poses = convert_ground_truth(gt, time=time)

        # aggregate poses by traffic participant for this ground truth
        for pose in gt_poses:
            idx = pose.traffic_participant.id_object
            if idx not in poses:
                poses[idx] = []

            # insert pose into list sorted by time
            insort(poses[idx], pose, key=lambda p: p.timestamp)

    # build trajectories per traffic participant
    # we will use the traffic_participant entry of the first pose
    tjs = [
        TrajectoryPublic(
            traffic_participant=tp_poses[0].traffic_participant, poses=tp_poses
        )
        for tp_poses in poses.values()
    ]
    return tjs


def convert_ground_truth(
    obj: GroundTruth, time: datetime = datetime.fromtimestamp(0)
) -> List[PosePublic]:

    if obj.timestamp is not None:
        dt = timedelta(
            seconds=obj.timestamp.seconds, milliseconds=obj.timestamp.nanos / 1e6
        )
    else:
        dt = timedelta(seconds=0)

    # get the base time
    ts_base = time + dt

    return [convert_moving_object(mo, time=ts_base) for mo in obj.moving_object]


def get_classification(obj: MovingObject) -> Classifications:
    """Get the object's TASI classification

    Args:
        obj (MovingObject): The object to evaluate

    Raises:
        AssertionError: If the `vehicle_classification` attribute is not specified.

    Returns:
        Classifications: The classification representation in TASI
    """
    if obj.type == MovingObjectType.VEHICLE:
        assert (
            obj.vehicle_classification is not None
        ), "The vehicle classification information is missing!"

        return Classifications.model_validate(
            {OSI2TASI_MAPPING[obj.vehicle_classification.type]: 1}
        )
    elif obj.type == MovingObjectType.PEDESTRIAN:
        return Classifications(pedestrian=1)
    else:
        return Classifications(other=1)


def convert_moving_object(
    obj: MovingObject, time: datetime, index: int = -1
) -> PosePublic:

    if obj.base is None:
        raise ValueError("The base attribute is missing but mandatory")

    if obj.base.orientation is None:
        raise ValueError("The orientation attribute is missing but mandatory")

    if obj.base.orientation.yaw is None:
        raise ValueError("The base attribute orientation.yaw is missing but mandatory")

    dimension = Dimension.model_validate(obj.base.dimension)
    position = Position.from_3dvector(Vector3DBase.model_validate(obj.base.position))

    # get the object's classification
    classifications = get_classification(obj)

    tp = TrafficParticipant(
        id_object=obj.id.value if obj.id is not None else index,
        dimension=Dimension.model_validate(obj.base.dimension),
        classifications=classifications,
    )

    pose = PosePublic(
        dimension=dimension,
        position=position,
        orientation=obj.base.orientation.yaw if obj.base.orientation else 0,
        acceleration=(
            Acceleration.model_validate(obj.base.acceleration)
            if obj.base.acceleration
            else Acceleration()
        ),
        velocity=Velocity.model_validate(obj.base.velocity),
        classifications=classifications,
        traffic_participant=tp,
        boundingbox=BoundingBox.from_dimension(
            dimension, relative_to=position, orientation=obj.base.orientation.yaw
        ),
        timestamp=time,
    )

    return pose


def convert_pose(pose: PosePublic, offset: Tuple[float, float]) -> MovingObject:

    most_likely: str = pose.classifications.as_series().idxmax()  # type: ignore

    if most_likely == "pedestrian":
        obj_type = MovingObjectType.PEDESTRIAN
    elif most_likely == "unknown":
        obj_type = MovingObjectType.UNKNOWN
    elif most_likely == "other":
        obj_type = MovingObjectType.OTHER
    else:
        obj_type = MovingObjectType.VEHICLE

    return MovingObject(
        id=Identifier(value=pose.traffic_participant.id_object),
        type=obj_type,
        base=BaseMoving(
            position=Vector3D(
                x=pose.position.easting - offset[0],
                y=pose.position.northing - offset[1],
                z=pose.position.altitude if pose.position.altitude is not None else 0,
            ),
            dimension=Dimension3D.from_dict(pose.dimension.model_dump()),
            velocity=Vector3D.from_dict(
                pose.velocity.model_dump(exclude={"magnitude"})
            ),
            acceleration=Vector3D.from_dict(
                pose.acceleration.model_dump(exclude={"magnitude"})
            ),
            orientation=Orientation3D(yaw=pose.orientation),
        ),
        vehicle_classification=(
            MovingObjectVehicleClassification(type=TASI2OSI_MAPPING[most_likely])
            if obj_type not in (MovingObjectType.PEDESTRIAN, MovingObjectType.UNKNOWN)
            else MovingObjectVehicleClassification()
        ),
    )


def convert_poses(
    poses: List[PosePublic],
    offset: Tuple[float, float] = (0, 0),
    time_reference: datetime = datetime.fromtimestamp(0, tz=timezone.utc),
) -> GroundTruth:
    """Convert the poses to a OSI `GroundTruth` message.

    Args:
        poses (List[PosePublic]): The poses at a certain time instant
        offset (Tuple[float, float]): An optional offset to shift the position.
        time_reference (datetime): The reference time

    Returns:
        GroundTruth: The `GroundTruth` representation of the poses

    Raises:
        AssertionError: If the poses do not belong to the same time instant
    """

    # ensure all poses have the same time
    if len(poses) > 2:
        for p1, p2 in zip(poses[:-1], poses[1:]):
            assert p1.timestamp == p2.timestamp
    elif len(poses) == 2:
        assert poses[0].timestamp == poses[1].timestamp
    else:
        pass

    dt = poses[0].timestamp - time_reference

    return GroundTruth(
        moving_object=list(map(convert_pose, poses, repeat(offset))),
        timestamp=Timestamp(seconds=dt.seconds, nanos=dt.microseconds * 1000),
    )


def convert_trajectories(
    trajectories: List[TrajectoryPublic],
    offset: Tuple[float, float],
    time_reference: datetime = datetime.fromtimestamp(0, timezone.utc),
) -> List[GroundTruth]:

    # at first, we let's create a mapping of time and list of poses.
    # this is required since the trajectories may span different time ranges.
    time_mapping: Dict[datetime, List[PosePublic]] = {}

    for tj in trajectories:
        for p in tj.poses:
            if p.timestamp not in time_mapping:
                time_mapping[p.timestamp] = []
            time_mapping[p.timestamp].append(p)

    return [
        convert_poses(time_mapping[ts], time_reference=time_reference, offset=offset)
        for ts in sorted(time_mapping.keys())
    ]
