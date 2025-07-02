import numpy as np
import pandas as pd

from tasi.base import CollectionBase, PandasBase
from tasi.dataset import PoseCollectionBase, TrajectoryDataset
from tasi.pose import Pose
from tasi.trajectory import Trajectory

from . import DatasetTestCase


class TrajectoryDatasetAccess(DatasetTestCase):

    def test_during(self):

        t0, t1 = self.ds.timestamps[5], self.ds.timestamps[10]

        ds2 = self.ds.during(t0, t1)
        self.assertEqual(ds2.interval.left, t0)
        self.assertEqual(
            ds2.interval.right,
            self.ds.timestamps[list(self.ds.timestamps).index(t1) - 1],
        )

    def test_during_include_right(self):

        t0, t1 = self.ds.timestamps[5], self.ds.timestamps[10]

        ds2 = self.ds.during(t0, t1, include_until=True)
        self.assertEqual(ds2.interval.left, t0)
        self.assertEqual(ds2.interval.right, t1)

    def test_trajectory_access(self):

        tj1 = self.ds.trajectory(self.ds.ids[0])
        tj2 = self.ds.trajectory(self.ds.ids[1])

        self.assertIsInstance(tj1, Trajectory)
        self.assertIsInstance(tj2, Trajectory)

    def test_multiple_trajectory_access(self):

        ds2 = self.ds.trajectory(self.ds.ids[:2])

        self.assertIsInstance(ds2, TrajectoryDataset)

    def test_multiple_trajectory_access_inverse(self):

        ds2 = self.ds.trajectory(self.ds.ids[0], inverse=True)

        self.assertIsInstance(ds2, TrajectoryDataset)
        np.testing.assert_array_equal(ds2.ids, self.ds.ids[1:])

    def test_get_classifications(self):

        df_classes = self.ds.most_likely_class()

        self.assertIsInstance(df_classes, pd.Series)
        self.assertEqual(len(df_classes), len(self.ds.ids))

    def test_get_classifications_by_pose(self):

        df_classes = self.ds.most_likely_class(by="pose")

        self.assertIsInstance(df_classes, pd.Series)
        self.assertIsInstance(df_classes.iloc[0], str)
        self.assertEqual(len(df_classes), len(self.ds))

    def test_get_classifications_by_trajectory_broascast(self):

        df_classes = self.ds.most_likely_class(by="trajectory", broadcast=True)

        self.assertIsInstance(df_classes, pd.Series)
        self.assertEqual(len(df_classes), len(self.ds))

    def test_get_classifications_by_invalid_type(self):

        with self.assertRaises(ValueError):
            self.ds.most_likely_class(by="something")

    def test_get_by_classification(self):

        ds = self.ds.get_by_object_class("motorbike")
        self.assertIsInstance(ds, TrajectoryDataset)
        self.assertEqual(ds.most_likely_class(by="trajectory").unique().size, 1)


class ObjectDatasetAccessColumns(DatasetTestCase):

    def test_access_single_columns(self):

        self.assertCountEqual(self.ds.position.columns, ["easting", "northing"])
        self.assertNotIsInstance(self.ds.position, type(self.ds))
        self.assertIsInstance(self.ds.position, pd.DataFrame)


class ObjectDatasetIndexingTestCase(DatasetTestCase):

    def test_index_with_timestamps(self):
        df = self.ds.loc[pd.IndexSlice[self.ds.timestamps[:2], :], :]

        self.assertTrue(isinstance(df, TrajectoryDataset))
        self.assertTrue(isinstance(df, CollectionBase))
        self.assertEqual(2, len(df.timestamps))

    def test_index_with_single_timestamp(self):
        p1 = self.ds.loc[self.ds.timestamps[0]]

        self.assertTrue(isinstance(p1, PandasBase))

        self.assertTrue(isinstance(p1, PoseCollectionBase))
        np.testing.assert_array_equal(p1.index[0], self.ds.index[0])
        self.assertEqual(1, len(p1.timestamps))

    def test_index_with_integer(self):

        p = self.ds.iloc[0]
        self.assertTrue(isinstance(p, Pose))
        self.assertEqual(2, p.index.nlevels)

    def test_index_single_row(self):
        p1 = self.ds.iloc[0]

        self.assertTrue(isinstance(p1, Pose))
        self.assertEqual(p1.index[0], self.ds.index[0])
        self.assertEqual(1, len(p1))

    def test_att(self):
        df = self.ds.att(self.ds.timestamps[:2])

        self.assertTrue(isinstance(df, PoseCollectionBase))
        self.assertEqual(2, len(df.timestamps))

        df = self.ds.att(self.ds.timestamps[:4], "position")

        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertFalse(isinstance(df, PoseCollectionBase))
        self.assertIn("easting", df.columns)
        self.assertIn("northing", df.columns)

        self.assertEqual(68, len(df))

    def test_single_att(self):
        p1 = self.ds.att(self.ds.timestamps[0])

        self.assertTrue(isinstance(p1, PoseCollectionBase))

        self.assertFalse(isinstance(p1, Trajectory))
        self.assertFalse(isinstance(p1, TrajectoryDataset))
        self.assertFalse(isinstance(p1, Pose))

    def test_group_by_trajectory(self):

        def trajectory_length(tj):
            return len(tj)

        lengths = self.ds.apply(trajectory_length, by="trajectory")

        self.assertEqual(self.ds.ids.size, lengths.size)
        self.assertIsInstance(lengths, pd.Series)

    def test_group_by_pose(self):

        lengths = self.ds.apply(len, by="pose")

        self.assertEqual(len(self.ds), lengths.size)
        self.assertIsInstance(lengths, pd.Series)

    def test_access_single_column_by_index(self):

        c = self.ds.columns[0]

        obj = self.ds.iloc[:, 0]

        self.assertIsInstance(obj, pd.Series)
        self.assertFalse(isinstance(obj, Pose))


class ObjectTrajectoryLocIndexingTestCase(DatasetTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tj = cls.ds.trajectory(cls.ds.ids[0])

    def test_index_with_timestamps_via_att(self):
        tj = self.tj.att(self.tj.timestamps[:2])

        self.assertEqual(2, len(tj))
        self.assertTrue(isinstance(tj, Trajectory))

    def test_index_with_timestamps_via_loc(self):
        tj = self.tj.loc[self.tj.timestamps[:2]]

        self.assertEqual(2, len(tj))
        self.assertTrue(isinstance(tj, Trajectory))

    def test_index_with_timestamps_with_column_via_loc(self):
        df = self.tj.loc[self.tj.timestamps[:2], "position"]

        self.assertEqual(2, len(df))
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_index_with_timestamps_with_column(self):
        df = self.tj.att(self.tj.timestamps[:2], "position")

        self.assertEqual(2, len(df))
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_index_with_timestamps_with_multiple_columns_via_loc(self):
        df = self.tj.loc[
            self.tj.timestamps[:2], (["position", "velocity"], ["easting", "northing"])
        ]

        self.assertEqual(2, len(df))
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertIn("position", df.columns)
        self.assertIn("velocity", df.columns)

    def test_index_with_single_timestamp(self):
        p1 = self.tj.loc[self.tj.timestamps[2]]

        self.assertTrue(isinstance(p1, Pose))
        self.assertEqual(1, len(p1))

    def test_access_column_with_single_index(self):
        s1 = self.tj.loc[self.tj.timestamps[2], "position"]

        self.assertTrue(isinstance(s1, pd.Series))
        self.assertEqual(2, len(s1))

    def test_access_multiple_columns_with_single_index(self):
        s1 = self.tj.loc[self.tj.timestamps[2], ["position", "position"]]

        self.assertTrue(isinstance(s1, pd.Series))
        self.assertEqual(4, len(s1))
        self.assertEqual(s1.name, self.tj.id)

    def test_access_multiple_nested_columns_with_single_index(self):
        s1 = self.tj.loc[
            self.tj.timestamps[2], (["position", "position"], ["easting", "northing"])
        ]

        self.assertTrue(isinstance(s1, pd.Series))
        self.assertEqual(2, len(s1))
        self.assertEqual(s1.name, self.tj.id)

    def test_access_multiple_column_with_all_indexes(self):
        df = self.tj.loc[:, (["position", "position"], ["easting", "northing"])]

        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertEqual(len(self.tj), len(df))


class ObjectTrajectoryiLocIndexingTestCase(DatasetTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tj = cls.ds.trajectory(cls.ds.ids[0])

    def test_index_with_timestamps(self):
        tj = self.tj.iloc[:2]

        self.assertEqual(2, len(tj))
        self.assertTrue(isinstance(tj, Trajectory))

    def test_index_with_timestamps_with_column(self):

        with self.assertRaises(ValueError):
            # this does not work
            df = self.tj.iloc[:2, "position"]

        # but this should
        df = self.tj.iloc[:2].position

        self.assertEqual(2, len(df))
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_index_with_timestamps_with_multiple_columns(self):

        with self.assertRaises(IndexError):
            # this does not work
            df = self.tj.iloc[:2, ["position", "velocity"]]

        # but this should
        df = self.tj.iloc[:2][["position", "velocity"]]

        self.assertEqual(2, len(df))
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertIn("position", df.columns)
        self.assertIn("velocity", df.columns)

    def test_index_with_single_timestamp(self):
        p1 = self.tj.iloc[0]

        self.assertTrue(isinstance(p1, Pose))
        self.assertEqual(2, p1.index.nlevels)
        self.assertEqual(1, len(p1))

    def test_access_column_with_single_index(self):

        with self.assertRaises(ValueError):
            # this does not work
            df1 = self.tj.iloc[0, "position"]
        df1 = self.tj.iloc[0].position

        self.assertTrue(isinstance(df1, pd.DataFrame))
        self.assertEqual(1, len(df1))
        self.assertEqual(2, len(df1.columns))
        self.assertEqual(self.tj.iloc[0].index, df1.index)

    def test_access_multiple_columns_with_single_index(self):

        with self.assertRaises(IndexError):
            # this does not work
            df1 = self.tj.iloc[0, ["position", "position"]]

        df1 = self.tj.iloc[0][["position", "position"]]

        self.assertTrue(isinstance(df1, pd.DataFrame))
        self.assertEqual(1, len(df1))
        self.assertEqual(4, len(df1.columns))
        self.assertEqual(self.tj.iloc[0].index, df1.index)


class ObjectDatasetManipulationTestCase(DatasetTestCase):

    def test_incrementing_attribute(self):

        ds: TrajectoryDataset = self.ds.copy()
        ds["position"] = ds.position + 10

        np.testing.assert_array_equal(ds.position, self.ds.position + 10)

        ds["position"] = ds.position + 10

        np.testing.assert_array_equal(ds.position, self.ds.position + 10 + 10)

    def test_shifting_center(self):

        ds = self.ds.copy()
        ds["position"] = ds.position + 10

        np.testing.assert_array_almost_equal(ds.position, self.ds.position + 10)

    def test_heading_column_access(self):
        col = self.ds.loc[:, "yaw"]

        self.assertIsInstance(col, pd.Series)

    def test_heading_column_access_dataframe(self):
        col = self.ds.loc[:, ["yaw"]]

        self.assertIsInstance(col, pd.DataFrame)


class ObjectTrajectoryILocIndexingTestCase(DatasetTestCase):

    def test_single_row_access(self):
        row = self.ds.iloc[0]

        self.assertIsInstance(row, Pose)

    def test_single_column_access(self):
        col = self.ds.iloc[:, 0]

        self.assertIsInstance(col, pd.Series)

    def test_single_column_access_dataframe(self):
        col = self.ds.iloc[:, [0]]

        self.assertIsInstance(col, pd.DataFrame)


class ObjectTrajectoryAttIndexingTestCase(DatasetTestCase):

    def test_single_row_access(self):
        t1 = self.ds.timestamps[0]

        row = self.ds.att(t1)

        self.assertIsInstance(row, PoseCollectionBase)

    def test_single_row_with_key_access(self):
        t1 = self.ds.timestamps[-1]

        row = self.ds.att(t1, "yaw")

        self.assertIsInstance(row, pd.Series)

    def test_multiple_rows_access(self):
        t1 = self.ds.timestamps[:500]

        row = self.ds.att(t1)

        # the rows contain multiple objects -> dataset
        self.assertIsInstance(row, TrajectoryDataset)
        self.assertNotEqual(1, row.ids.size)


class ObjectTrajectoryAtIdIndexingTestCase(DatasetTestCase):

    def test_single_object_access(self):
        idx = self.ds.ids[0]

        obj = self.ds.atid(idx)

        self.assertIsInstance(obj, Trajectory)
        self.assertEqual(obj.id, idx)

    def test_multiple_object_access(self):
        idx = self.ds.ids[:5]

        obj = self.ds.atid(idx)

        self.assertIsInstance(obj, TrajectoryDataset)
        np.testing.assert_array_equal(obj.ids, idx)


class ObjectTrajectoryAtIndexingTestCase(DatasetTestCase):

    def test_single_row_and_columns_access_via_index(self):

        c1 = self.ds.columns[0]
        idx = self.ds.index[0]

        obj = self.ds.iat[0, 0]

        self.assertEqual(obj, self.ds.loc[idx, c1])

    def test_single_row_and_columns_access_via_iindex(self):

        c1 = self.ds.columns[0]
        idx = self.ds.index[0]

        obj = self.ds.at[idx, c1]

        self.assertEqual(obj, self.ds.loc[idx, c1])


class ObjectPoseAtIndexingTestCase(DatasetTestCase):

    def test_access_properties(self):

        # use the first traffic participant
        idx = self.ds.ids[0]

        # get the trajectory
        tj = self.ds.trajectory(idx)

        # and the first measurement of the traffic participant -> its pose
        p: Pose = tj.att(tj.timestamps[0])

        # check if ids and timestamp equal
        self.assertEqual(idx, p.id)
        self.assertEqual(p.timestamp, tj.timestamps[0])

        self.assertEqual(p.yaw.item(), tj.loc[tj.index[0], "yaw"])
