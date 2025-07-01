from datetime import datetime
from typing import List, Self, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd

from .indexing import ILocator, LocatableEntity, LocLocator
from .utils import MULTI_INDEX_SEPERATOR, add_attributes, to_pandas_multiindex


class TimestampMixin:

    TIMESTAMP_COLUMN = "timestamp"

    @property
    def timestamps(self) -> np.ndarray[np.datetime64]:
        """The unique timestamps in the dataframe

        Returns:
            np.ndarray[np.datetime64]: A list of timestamps
        """
        return self.index.get_level_values(self.TIMESTAMP_COLUMN).unique()

    def att(
        self,
        timestamps: Union[pd.Timestamp, List[pd.Timestamp], pd.Index],
        columns: pd.Index = None,
    ):

        try:
            len(timestamps)
        except:
            timestamps = [timestamps]

        if self.index.nlevels == 1:
            # assume timestamps are on the index
            idx = timestamps
        elif self.index.nlevels == 2:
            # timestamps are on the first index level
            idx = pd.IndexSlice[timestamps, :]
        else:
            raise RuntimeError(
                "Unsupported dataframe with an multi index with number of levels > 2"
            )

        if columns is None:
            return self.loc[idx, :]
        else:
            return self.loc[idx, columns]

    @property
    def interval(self) -> pd.Interval:
        """Returns the time interval this object spans

        Returns:
            pd.Interval: The interval of this
        """
        return pd.Interval(self.timestamps[0], self.timestamps[-1])


class IndexMixin:

    ID_COLUMN = "id"

    @property
    def ids(self) -> pd.Index:
        """Returns the unique ids in the dataset

        Returns:
            np.ndarray: A List of ids
        """
        idx: pd.MultiIndex = self.index  # type: ignore

        return idx.get_level_values(self.ID_COLUMN).unique()


class TASIBase(LocatableEntity):

    @property
    def attributes(self) -> pd.Index:
        """Returns the dataset attributes

        Returns:
            pd.Index: A list of attribute names
        """
        return self.columns.get_level_values(0).unique()

    def add_attribute(self, attr: Union[pd.Series, pd.DataFrame]):
        df = add_attributes(self, attr)

        return self._ensure_correct_type(df, None)


class PandasBase(pd.DataFrame, TASIBase, TimestampMixin):

    INDEX_COLUMNS = [TimestampMixin.TIMESTAMP_COLUMN]

    @property
    def iloc(self):
        return ILocator(self)

    @property
    def loc(self):
        return LocLocator(self)

    @classmethod
    def from_csv(
        cls,
        file: str,
        indices: Union[List, str] = (),
        seperator: str = MULTI_INDEX_SEPERATOR,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Read a dictionary-alike object from a `.csv` file as a pandas DataFrame.

        Args:
            file (str): The path and name of the dataset `.csv` file
            indices (Union[List, str]): The name of the columns to use as index

        """
        if indices and not hasattr(kwargs, "index_col"):
            kwargs["index_col"] = indices

        # read csv data
        df = pd.read_csv(file, **{"parse_dates": True, **kwargs})

        # parse dates
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")

        # try to set index
        try:
            df.set_index(cls.TIMESTAMP_COLUMN, inplace=True)
        except KeyError:
            pass

        # ensure the column is a pandas MultiIndex
        df.columns = to_pandas_multiindex(df.columns.to_list(), separator=seperator)

        return cls(df).sort_index(axis=1)


class CollectionBase(PandasBase, IndexMixin):

    INDEX_COLUMNS = [*PandasBase.INDEX_COLUMNS, IndexMixin.ID_COLUMN]

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

    def atid(
        self, ids: Union[int, List[int], pd.Index], attributes: pd.Index = None
    ) -> Self:
        """Select rows by the given id and optionally by attributes

        Args:
            ids (Union[int, List[int], pd.Index]): A list of IDs
            attributes (pd.Index, optional): A list of attribute names. Defaults to None.

        Returns:
            Self: The selected rows and attributes
        """
        try:
            len(ids)
        except BaseException:
            ids = [ids]

        if attributes is None:
            return self.loc[pd.IndexSlice[:, ids], :]
        else:
            return self.loc[pd.IndexSlice[:, ids], attributes]

    @classmethod
    def from_csv(cls, file, indices=(), **kwargs):

        obj = pd.DataFrame(super().from_csv(file, indices, **kwargs))

        obj.set_index(cls.ID_COLUMN, append=True, inplace=True)

        return cls(obj)

    def to_csv(
        self,
        file: str,
        indices: Tuple = (),
        seperator: str = MULTI_INDEX_SEPERATOR,
        **kwargs,
    ):
        """
        Write the object to a .csv file with custom multiindex.

        Args:
            file (str): The path of the file

        Notes:
            The `kwargs` will be forwarded to the `pd.to_csv()` method for customization.

            An attribute with a `pd.MultiIndex` column will be joined with `seperator`.

        """
        if not indices:
            indices = self.INDEX_COLUMNS

        old_columns = self.columns
        try:
            self.columns = [seperator.join(c) for c in self.columns.to_flat_index()]

            super().to_csv(file, **{"index": True, **kwargs})
        finally:
            self.columns = old_columns


class PoseCollectionBase(CollectionBase):

    @property
    def _trajectory_constructor(self):  # pragma: no cover
        raise NotImplementedError(
            "Please implement the trajectory_constructor property"
        )

    @property
    def _pose_constructor(self):  # pragma: no cover
        raise NotImplementedError(
            "Please implement the trajectory_constructor property"
        )

    def _as_pose(self, df: Union[pd.Series, pd.DataFrame], key=None) -> "Pose":
        """
        Convert the given `df` to a `Pose`.

        Args:
            df (Union[pd.Series, pd.DataFrame]): The data to convert to a Pose.

            key (Any, optional): The used access key. Defaults to None.

        Returns:
            Pose: The given series or dataframe as `Pose`.

        """
        if isinstance(df, pd.Series):
            df = df.to_frame().T

        # correctly set the name of the index levels
        df.index.names = self.INDEX_COLUMNS

        return self._pose_constructor(df.infer_objects())

    def _ensure_correct_type(self, df: pd.DataFrame, key=None):

        # assume attributes are on the index for series and on the columns for dataframe
        attributes = df.index if isinstance(df, pd.Series) else df.columns

        # check that attributes match (no column-based slicing)
        if self.attributes.difference(attributes.get_level_values(0).unique()).empty:
            if len(df) == 1 or isinstance(df, pd.Series):
                return self._as_pose(df, key=key)
            else:
                obj = PoseCollectionBase(df)
                if obj.ids.size == 1:
                    return self._trajectory_constructor(df)
                elif obj.timestamps.size > 1:
                    return self._constructor(df)
                return obj

        else:
            if not isinstance(df, pd.Series):
                return pd.DataFrame(df)
            return df


class GeoPoseCollectionBase(PoseCollectionBase, gpd.GeoDataFrame):
    pass
