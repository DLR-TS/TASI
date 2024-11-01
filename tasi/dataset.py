"""
Functions and classes to load and manage datasets.

Classes
--------

.. autosummary::
    Dataset
    TrajectoryDataset
    WeatherDataset
    TrafficLightDataset


Module content
-----------------
"""
from datetime import datetime
from typing import Iterable, List, Union

import numpy as np
import pandas as pd
from typing_extensions import Self

from tasi.utils import to_pandas_multiindex

__all__ = [
    'Dataset',
    'TrajectoryDataset',
    'WeatherDataset',
    'AirQualityDataset',
    'RoadConditionDataset'
    'TrafficLightDataset',
]

ObjectClass = Union[str, int]


class Dataset(pd.DataFrame):

    TIMESTAMP_COLUMN = 'timestamp'
    ID_COLUMN = 'id'
    INDEX_COLUMNS = [TIMESTAMP_COLUMN, ID_COLUMN]

    @property
    def _constructor(self):
        return self.__class__

    @property
    def timestamps(self) -> np.ndarray[np.datetime64]:
        """The unique timestamps in the dataset

        Returns:
            np.ndarray[np.datetime64]: A list of timestamps
        """
        return self.index.get_level_values(self.TIMESTAMP_COLUMN).unique()

    @property
    def ids(self) -> np.ndarray[np.int64]:
        """Returns the unique ids in the dataset

        Returns:
            np.ndarray: A List of ids
        """
        try:
            return self.index.get_level_values(self.ID_COLUMN).unique()
        except:
            return self[self.ID_COLUMN].unique()

    @property
    def attributes(self) -> np.ndarray[str]:
        """Returns the dataset attributes

        Returns:
            np.ndarray: A list of attribute names
        """
        return self.columns.get_level_values(0).unique()

    def att(
        self,
        timestamps: Union[pd.Timestamp, List[pd.Timestamp], pd.Index],
        attribute: Union[List[str], pd.Index] = None
    ) -> Union[Self, pd.Series]:
        """Select the rows at the specified times and optionally the specified attributes.

        Args:
            timestamps (Union[pd.Timestamp, List[pd.Timestamp], pd.Index]): The timestamps to select
            attribute (pd.Index, optional): The attribute to select. Defaults to None.

        Returns:
            Union[Self, pd.Series]: The selected row(s) and column(s)
        """
        try:
            len(timestamps)
        except:
            timestamps = [timestamps]

        if attribute is None:
            return self.loc[pd.IndexSlice[timestamps, :]]
        else:
            return self.loc[pd.IndexSlice[timestamps, :], attribute]

    def atid(self, ids: Union[int, List[int], pd.Index], attributes: pd.Index = None) -> Self:
        """Select rows by the given id and optionally by attributes

        Args:
            ids (Union[int, List[int], pd.Index]): A list of IDs 
            attributes (pd.Index, optional): A list of attribute names. Defaults to None.

        Returns:
            Self: The selected rows and attributes
        """
        try:
            len(ids)
        except:
            ids = [ids]

        if attributes is None:
            return self.loc[pd.IndexSlice[:, ids], :]
        else:
            return self.loc[pd.IndexSlice[:, ids], attributes]

    @property
    def interval(self) -> pd.Interval:
        """Returns the time interval this dataset spans

        Returns:
            pd.Interval: The interval of this
        """
        return pd.Interval(self.timestamps[0], self.timestamps[-1])

    def during(self, since: datetime, until: datetime, include_until: bool = False):
        """
        Select rows within a specific time range (include "since", exclude "until").

        Args:
            since (datetime): The start datetime for the selection.
            until (datetime): The end datetime for the selection.
            include_until (bool, optional): Whether to include data with timestamp "until". Defaults to False.

        Returns:
            ObjectDataset: A subset of the dataset with rows between the specified datetimes.
        """

        # get all timestamps
        timestamps = self.index.get_level_values(self.TIMESTAMP_COLUMN)

        # create a mask selecting only the relevant point in times
        valid_since = timestamps >= since
        if include_until:
            valid_until = timestamps <= until
        else:
            valid_until = timestamps < until

        # select the entries
        return self.loc[valid_since & valid_until]

    @classmethod
    def from_csv(cls, file: str, indices: Union[List, str] = (), **kwargs) -> Self:
        """
        Read a dictionary-alike object from a `.csv` file as a pandas DataFrame.

        Args:
            file (str): The path and name of the dataset `.csv` file
            indices (Union[List, str]): The name of the columns to use as index

        """
        if indices and not hasattr(kwargs, 'index_col'):
            kwargs['index_col'] = indices

        # read csv data
        df = pd.read_csv(file, **kwargs)

        # parse dates
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')

        # try to set index
        try:
            df.set_index(cls.INDEX_COLUMNS, inplace=True)
        except KeyError:
            try:
                df.set_index(cls.TIMESTAMP_COLUMN, inplace=True)
            except KeyError:
                pass

        return cls(df)


class TrajectoryDataset(Dataset):

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

        if isinstance(index, int):
            index = [index]

        if inverse:
            index = self.ids.difference(index)

        return self.atid(index)

    def most_likely_class(self, by: str = 'trajectory', broadcast: bool = False) -> pd.Series:
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
        if by == 'pose':
            return self.classifications.idxmax(axis=1)

        elif by == 'trajectory':
            trajectory_class = self.classifications.groupby('id').apply(lambda tj_classes: tj_classes.mean().idxmax())

            if broadcast:
                return self.apply(lambda ser: trajectory_class[ser.name[1]], axis=1)
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

        return self[self.most_likely_class(by='trajectory', broadcast=True).isin(object_class)]

    @classmethod
    def from_csv(cls, *args, **kwargs) -> Self:

        df = super().from_csv(*args, **kwargs)

        # ensure the column is a pandas MultiIndex
        df.columns = to_pandas_multiindex(df.columns.to_list())

        return cls(df)


class WeatherDataset(Dataset):

    pass


class AirQualityDataset(Dataset):

    pass


class RoadConditionDataset(Dataset):

    pass


class TrafficLightDataset(Dataset):
    
    pass
