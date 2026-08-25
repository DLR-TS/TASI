from typing import Generic, TypeVar

from tasi import Pose, Trajectory
from tasi.pose.base import CollectionBase

A = TypeVar("A", bound="CollectionBase", covariant=True)


class ExtensionBase(Generic[A]):

    def __init__(self, obj: A, *args, **kwargs) -> None:
        self.obj: A = obj

        super().__init__(*args, **kwargs)


class PoseExtensionBase(ExtensionBase[Pose]): ...


class TrajectoryExtensionBase(ExtensionBase[Trajectory]): ...
