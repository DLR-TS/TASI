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

__all__ = [
    'Dataset',
    'TrajectoryDataset',
    'WeatherDataset',
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

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        raise NotImplementedError()

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

    def most_likely_class(self) -> pd.Series:
        """
        Get the name of the most probable object class for each traffic participant of the dataset

        Returns:
            pd.Series: Information about the most probable object class. Return the most likely object class of each trajectory.

        Raises:
            ValueError: If the value of "by" is neither 'pose' nor 'trajectory'.
        """
        trajectory_class = self.classifications.droplevel(axis=1, level=1).groupby(
            self.ID_COLUMN
        ).apply(lambda tj_classes: tj_classes.mean().idxmax())

        return trajectory_class

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

        return self[self.most_likely_class(by='trajectory', broadcast=True).isin(object_classes)]


class WeatherDataset(Dataset):

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        pass


class TrafficLightDataset(Dataset):

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        pass

    def signal(self, signal_id: int):
        """
        Filter the dataset by a signal id.

        Args:
            signal_id (int): The id of the signal.

        Returns:
            TraiffLightDataset: The data from the signal
        """
        return self.xs(signal_id, level=1)

    def state(self, eventstate: int):
        """
        Filter the dataset by an event state.

        Args:
            eventstate (int): The eventstate used for filtering.

        Returns:
            TraiffLightDataset: The data with the user defined eventstate.
        """
        return self.loc[self.eventstate == eventstate]
