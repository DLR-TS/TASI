from functools import wraps
from typing import Iterable, List, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd
from fastdtw import fastdtw
from typing_extensions import Self

from .base import CollectionBase, GeoPoseCollectionBase, PoseCollectionBase
from .trajectory import GeoTrajectory, Trajectory

__all__ = [
    "Dataset",
    "TrajectoryDataset",
    "GeoTrajectoryDataset",
    "WeatherDataset",
    "AirQualityDataset",
    "RoadConditionDataset",
    "TrafficLightDataset",
    "TrafficVolumeDataset",
]

ObjectClass = Union[str, int]


class Dataset(CollectionBase):
    """Base type of datasets"""

    def _ensure_correct_type(self, df, key):
        return df

    @property
    def _constructor(self):
        return type(self)

    @property
    def _constructor_sliced(self):
        return pd.Series


class TrajectoryDataset(Dataset, PoseCollectionBase):
    """A dataset of trajectories"""

    @property
    def _trajectory_constructor(self):
        from .trajectory import Trajectory

        return Trajectory

    @property
    def _pose_constructor(self):
        from .pose import Pose

        return Pose

    def trajectory(self, index: Union[int, Iterable[int]], inverse: bool = False):
        """
        Select trajectory data for specific indices, or exclude them if inverse is set to True.

        Args:
            index (Union[int, Iterable[int]], optional): An integer or an iterable of integers representing the indices of
                the trajectories to select. If a single integer is provided, only the trajectory corresponding
                to that index is selected. If a list or other iterable of integers is provided, all trajectories
                corresponding to those indices are selected.
            inverse (bool, optional): If set to True, the selection is inverted, meaning the specified indices
                are excluded from the resulting dataset, and all other trajectories are included. Defaults to False.

        Returns:
            TrajectoryDataset: A trajectory or multiple trajectories of the dataset.
        """

        if isinstance(index, (int, np.int_)):
            index = [index]

        if inverse:
            index = self.ids.difference(index)

        return self.atid(index)

    def most_likely_class(
        self, by: str = "trajectory", broadcast: bool = False
    ) -> pd.Series:
        """
        Get the name of the most probable object class for each pose or trajectory of the dataset

        Args:
            by (str): By which object the most likely class should be determined. Possible values: 'pose', 'trajectory'
            broadcast (bool, optional): Specifies whether the most likely class should be broadcasted to each pose of the dataset.
                The option only changes the output for trajectories. Defaults to False.

        Returns:
            pd.Series: Information about the most probable object class.
                If `by` is "pose" and broadcast is "False" or "True" return the most likely object class of each pose.
                If `by` is "trajectory" and broadcast is "False" return the most likely object class of each trajectory.
                If `by` is "trajectory" and broadcast is "True" return the most likely object class of each trajectory
                for each pose.

        Raises:
            ValueError: If the value of "by" is neither 'pose' nor 'trajectory'.
        """
        classifications: pd.DataFrame = self.classifications  # type: ignore

        if classifications.columns.nlevels >= 2:
            # remove the second level to ensure result is not a tuple
            classifications = classifications.droplevel(axis=1, level=1)

        if by == "pose":
            return classifications.idxmax(axis=1)

        elif by == "trajectory":
            trajectory_class = classifications.groupby("id").apply(
                lambda tj_classes: tj_classes.mean().idxmax()
            )
            trajectory_class.name = "classification"

            if broadcast:

                return self.apply(
                    lambda pose: trajectory_class[pose.name[1]], by="pose", tasi=False
                )
            else:
                return trajectory_class

        else:
            raise ValueError("'by' must be one of 'pose' or 'trajectory'.")

    def get_by_object_class(self, object_class: Union[List[ObjectClass], ObjectClass]):
        """
        Return only the poses of a specific object class.

        Args:
            object_class (ObjectClass): The object class.

        Returns:
            ObjectDataset: Dataset containing only the poses of a defined object class.

        Note:
            The object class of a pose is determined by the mean probability of all poses in the trajectory.
        """

        if not isinstance(object_class, list):
            object_class = [object_class]

        return self[
            self.most_likely_class(by="trajectory", broadcast=True).isin(object_class)
        ]

    @property
    def roi(self):
        """
        Return the region of interest of the dataset.

        Returns:
            np.ndarray: The region of interest.
        """
        return np.array(
            [
                self.position.easting.min(),
                self.position.northing.min(),
                self.position.easting.max(),
                self.position.northing.max(),
            ]
        ).reshape(-1, 2)

    @classmethod
    def from_attributes(
        cls,
        position: pd.DataFrame,
        velocity: pd.DataFrame,
        acceleration: pd.DataFrame,
        heading: Union[pd.Series, pd.DataFrame],
        classifications: pd.DataFrame,
        yaw_rate: Union[pd.Series, pd.DataFrame] = None,
        dimension: pd.DataFrame = None,
        boundingbox: pd.DataFrame = None,
    ):

        assert (
            dimension is None or boundingbox is None
        ), "either dimension or boundingbox needs to be specified"

        if boundingbox is None or boundingbox.empty:
            from tasi.calculus import boundingbox_from_dimension

            boundingbox = boundingbox_from_dimension(
                dimension, heading, relative_to=position
            )

        if velocity.empty:
            from tasi.calculus import calc_velocity_from_origins

            velocity = calc_velocity_from_origins(position)

        if acceleration.empty:
            from tasi.calculus import calc_acceleration_from_origins

            acceleration = calc_acceleration_from_origins(position)

        if yaw_rate is None or yaw_rate.empty:
            from tasi.calculus import calc_yaw_rate_from_headings

            yaw_rate = calc_yaw_rate_from_headings(heading)

        from tasi.utils import add_attributes

        df = add_attributes(
            position,
            velocity,
            acceleration,
            heading,
            yaw_rate,
            classifications,
            dimension,
            boundingbox,
            keys=[
                "position",
                "velocity",
                "acceleration",
                "heading",
                "yaw_rate",
                "classifications",
                "dimension",
                "boundingbox",
            ],
        )

        return cls(df)

    def as_geopandas(
        self, *args, activate: Union[str, Tuple[str]] = "position", **kwargs
    ) -> "GeoTrajectoryDataset":
        """Convert to a geospatial representation using `geopandas`.

        Returns:
            GeoTrajectoryDataset: The dataset represented with GeoObjects.
        """

        gtjs = [
            self.trajectory(tjid).as_geopandas(*args, **kwargs) for tjid in self.ids
        ]

        gds = GeoTrajectoryDataset.from_trajectories(gtjs)
        gds.set_geometry(activate, inplace=True)

        return gds

    @classmethod
    def from_trajectories(cls, tjs: List[Trajectory]) -> Self:
        """Create a dataset based on trajectories

        Args:
            tjs (List[Trajectory]): The trajectories

        Returns:
            TrajectoryDataset: A dataset with the given trajectories
        """
        return cls(pd.concat(tjs, axis=0))

    def apply(
        self,
        func: callable,
        by: str = "trajectory",
        tasi: bool = False,
        *args,
        **kwargs
    ):

        if by.lower() == "trajectory":

            if tasi:

                @wraps(func)
                def f(tj):
                    return func(self._trajectory_constructor(tj))

            else:
                f = func
            return self.groupby(by=self.ID_COLUMN).apply(f)
        elif by.lower() == "pose":
            if tasi:

                @wraps(func)
                def f(pose):
                    return func(self._as_pose(pose))

            else:
                f = func
            return super().apply(f, axis=1)
        else:
            return super().apply(*args, **kwargs)

    def _ensure_correct_type(self, *args, **kwargs):
        return PoseCollectionBase._ensure_correct_type(self, *args, **kwargs)


class GeoTrajectoryDataset(Dataset, GeoPoseCollectionBase):
    """Representation of a dataset of trajectory information using ``GeoPandas``"""

    @classmethod
    def from_trajectories(cls, tjs: List[GeoTrajectory]) -> Self:
        """Create a dataset based on trajectories

        Args:
            tjs (List[GeoTrajectory]): The trajectories

        Returns:
            GeoTrajectoryDataset: A dataset with the given trajectories
        """
        return cls(pd.concat(tjs, axis=0))

    def explore(self, crs: str = "EPSG:32632", *args, **kwargs):

        if self.crs is None:
            self = self.set_crs(crs)

        # a quick hack for now since we dont want to update the orignal columns
        self = gpd.GeoDataFrame(self)

        # we need to flatten index for visualization purpose
        self.columns = [
            "_".join(l) if l[1] else l[0] for l in self.columns.to_flat_index()
        ]

        return self.explore(*args, **kwargs)


class WeatherDataset(Dataset):
    """Dataset of weather information"""

    pass


class AirQualityDataset(Dataset):
    """Dataset of air quality information"""

    pass


class RoadConditionDataset(Dataset):
    """Dataset of road conditioning information"""

    pass


class TrafficLightDataset(Dataset, PoseCollectionBase):
    """Dataset of traffic light information"""

    @property
    def _trajectory_constructor(self):
        return TrafficLightDataset

    @property
    def _pose_constructor(self):
        from .pose import TrafficLightPose

        return TrafficLightPose

    def _ensure_correct_type(self, *args, **kwargs):
        return PoseCollectionBase._ensure_correct_type(self, *args, **kwargs)

    def synchronize(self, ds: TrajectoryDataset) -> Tuple[TrajectoryDataset, Self]:
        """Synchronize the given trajectory with this traffic light dataset

        Args:
            ds (TrajectoryDataset): A dataset of trajectories

        Returns:
            Tuple[TrajectoryDataset, Self]: Both datasets synchronized
        """
        # ensure given dataset is in the traffic light interval
        mask = (ds.timestamps > self.interval.left) & (
            ds.timestamps < self.interval.right
        )

        ds = ds.att(ds.timestamps[mask])  # type: ignore

        # we will replicate every entry to match the entries in the given
        # trajectory dataset
        route = fastdtw(self.timestamps, ds.timestamps)[1]

        return ds, self.iloc[[r[0] for r in route]]


class TrafficVolumeDataset(Dataset):
    """Dataset of traffic volume information"""

    @classmethod
    def from_csv(cls, *args, **kwargs) -> Self:

        df = super().from_csv(*args, **kwargs)

        # transform data to Dataset format
        df = df.stack().to_frame("volume")

        # ensure index names are correnct
        df.index.names = cls.INDEX_COLUMNS

        return cls(df)

    @property
    def lanes(self) -> pd.Index:
        """Returns the unique lanes of the dataset

        Returns:
            pd.Index: The unique lanes as Index
        """
        return self.ids

    def lane(self, lane: str) -> pd.Series:
        """Returns the traffic volume from a specific lane

        Returns:
            pd.Series: A pd.Series of traffic volume data
        """
        return self.atid(lane).volume
