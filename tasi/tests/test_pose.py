from datetime import datetime
from unittest import TestCase

import pandas as pd

from tasi import Pose
from tasi.calculus import boundingbox_from_dimension


def init_pose(index, timestamp):
    dimension = pd.DataFrame([[2, 8, 2]], columns=["width", "length", "height"])

    heading = pd.Series([0])

    position = pd.DataFrame([[0, 0]], columns=["easting", "northing"])

    return Pose.from_attributes(
        index=index,
        timestamp=timestamp,
        position=position,
        acceleration=pd.DataFrame(
            [[0, 0, 0]], columns=["easting", "northing", "magnitude"]
        ),
        velocity=pd.DataFrame(
            [[0, 0, 0]], columns=["easting", "northing", "magnitude"]
        ),
        heading=heading,
        boundingbox=boundingbox_from_dimension(
            dimension, heading=heading, relative_to=position
        ),
        classifications=pd.DataFrame([[1, 0]], columns=["car", "bicycle"]),
    )


class TestPoseInit(TestCase):

    def test_init_from_attributes(self):

        ts = datetime.now()
        index = 0
        pose = init_pose(index=index, timestamp=ts)

        self.assertEqual(index, pose.id)
        self.assertEqual(ts, pose.timestamp)


class TestPoseConversion(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.pose = init_pose(index=0, timestamp=datetime.now())

    def test_convert_geopose(self):

        geopose = self.pose.as_geopandas()

        self.assertIsNotNone(geopose.geometry)
