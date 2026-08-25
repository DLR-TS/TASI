import numpy as np

from tasi.dataset import TrajectoryDataset
from tasi.pose import Pose
from tasi.trajectory import Trajectory

from . import DatasetTestCase


class TrajectoryDatasetAddAttribute(DatasetTestCase):

    def test_add_series_index(self):

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = self.ds.yaw.copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = "yaw2"

        # add the attribute
        ds = self.ds.add_attribute(s1)

        # verify
        self.assertIn("yaw", ds.attributes)
        np.testing.assert_array_equal(ds.yaw + 10, ds.yaw2)
        self.assertIsInstance(ds, TrajectoryDataset)

    def test_add_series_multiindex(self):

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = self.ds[("position", "easting")].copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = ("center2", "easting")

        # add the attribute
        ds = self.ds.add_attribute(s1)

        # verify
        self.assertIn("center2", ds.attributes)
        self.assertIn("easting", ds.position.columns)
        np.testing.assert_array_equal(ds.position.easting + 10, ds.center2.easting)
        self.assertIsInstance(ds, TrajectoryDataset)


class TrajectoryAddAttribute(DatasetTestCase):

    def test_add_series_index(self):

        tj = self.ds.trajectory(self.ds.ids[0])

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = tj.yaw.copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = "yaw2"

        # add the attribute
        tj = tj.add_attribute(s1)

        # verify
        self.assertIn("yaw2", tj.attributes)
        np.testing.assert_array_equal(tj.yaw + 10, tj.yaw2)
        self.assertIsInstance(tj, Trajectory)

    def test_add_series_multiindex(self):

        tj = self.ds.trajectory(self.ds.ids[0])

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = tj[("position", "easting")].copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = ("center2", "easting")

        # add the attribute
        tj = tj.add_attribute(s1)

        # verify
        self.assertIn("center2", tj.attributes)
        self.assertIn("easting", tj.position.columns)
        np.testing.assert_array_equal(tj.position.easting + 10, tj.center2.easting)
        self.assertIsInstance(tj, Trajectory)


class PoseAddAttribute(DatasetTestCase):

    def test_add_series_index(self):

        pose = self.ds.iloc[0]

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = pose.yaw.copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = "yaw2"

        # add the attribute
        pose = pose.add_attribute(s1)

        # verify
        self.assertIn("yaw2", pose.attributes)
        np.testing.assert_array_equal(pose.yaw + 10, pose.yaw2)
        self.assertIsInstance(pose, Pose)

    def test_add_series_multiindex(self):

        pose = self.ds.iloc[0]

        # create a copy of the yaw attribute which we will use for testing purpose
        s1 = pose[("position", "easting")].copy()

        # increment by arbitraty number and change the name of the attribute
        s1 += 10
        s1.name = ("center2", "easting")

        # add the attribute
        pose = pose.add_attribute(s1)

        # verify
        self.assertIn("center2", pose.attributes)
        self.assertIn("easting", pose.position.columns)
        np.testing.assert_array_equal(pose.position.easting + 10, pose.center2.easting)
        self.assertIsInstance(pose, Pose)
