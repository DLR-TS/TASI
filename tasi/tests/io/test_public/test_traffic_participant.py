from datetime import datetime, timedelta
from unittest import TestCase

from tasi.io.public.base import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    Position,
    Velocity,
)
from tasi.io.public.pose import PosePublic
from tasi.io.public.traffic_participant import TrafficParticipant
from tasi.io.public.trajectory import TrajectoryPublic


class TrafficParticipantTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.dimension = Dimension(width=1, height=1, length=1)

        ts = datetime.now()

        cls.traffic_participant = TrafficParticipant(
            classifications=Classifications(pedestrian=1),
            dimension=cls.dimension,
            id_object=1,
        )

        def create_pose(idx):

            position = Position(easting=50000, northing=50000, altitude=1)

            return PosePublic(
                dimension=cls.dimension,
                position=position,
                velocity=Velocity(x=1, y=1, z=0),
                acceleration=Acceleration(),
                boundingbox=BoundingBox.from_dimension(
                    cls.dimension, relative_to=position
                ),
                classifications=Classifications(pedestrian=1),
                traffic_participant=cls.traffic_participant,
                timestamp=ts + timedelta(microseconds=idx),
                orientation=0,
            )

        cls.poses = [create_pose(i) for i in range(10)]

        cls.traffic_participant.start_time = cls.poses[0].timestamp
        cls.traffic_participant.end_time = cls.poses[-1].timestamp

    def setUp(self):
        self.tj = TrajectoryPublic(
            poses=self.poses, traffic_participant=self.traffic_participant
        )

        self.tasi = self.tj.as_tasi()

    def test_from_tasi_pose(self):
        tp = TrafficParticipant.from_tasi(self.tasi.iloc[0])

    def test_from_tasi_trajectory(self):
        tp = TrafficParticipant.from_tasi(self.tasi)

    def test_from_non_tasi(self):

        with self.assertRaises(TypeError):
            tp = TrafficParticipant.from_tasi(None)
