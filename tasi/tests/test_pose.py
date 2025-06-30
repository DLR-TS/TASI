from datetime import datetime
from unittest import TestCase

import pandas as pd

from tasi import Pose
from tasi.calculus import boundingbox_from_dimension


class TestPoseInit(TestCase):

    def test_init_from_attributes(self):

        dimension = pd.DataFrame([[2, 8, 2]], columns=["width", "length", "height"])

        heading = pd.Series([0])

        position = pd.DataFrame([[0, 0]], columns=["easting", "northing"])

        ts = datetime.now()
        pose = Pose.from_attributes(
            index=0,
            timestamp=ts,
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

        self.assertEqual(0, pose.id)
        self.assertEqual(ts, pose.timestamp)
