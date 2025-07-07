from datetime import datetime, timedelta
from unittest import TestCase

import numpy as np

from tasi.io.orm.pose import GeoPoseORM, PoseORM
from tasi.io.orm.traffic_participant import TrafficParticipantORM
from tasi.io.public.base import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    Position,
    Velocity,
)
from tasi.io.public.pose import GeoPosePublic, PosePublic
from tasi.io.public.traffic_participant import TrafficParticipant
from tasi.io.public.trajectory import TrajectoryPublic


class TrajectoryTestCase(TestCase):

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


class TestTrajectoryInit(TrajectoryTestCase):

    def test_init(self):

        tj = TrajectoryPublic(
            poses=self.poses, traffic_participant=self.traffic_participant
        )


class TrajectoryConversion(TrajectoryTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.tj = TrajectoryPublic(
            poses=cls.poses, traffic_participant=cls.traffic_participant
        )

    def test_to_geopose(self):

        geo = self.tj.as_geo()

        for pose in geo.poses:
            self.assertIsInstance(pose, GeoPosePublic)
            self.assertIsInstance(pose.traffic_participant, TrafficParticipant)
            self.assertEqual(pose.traffic_participant, geo.traffic_participant)

        self.assertEqual(self.tj.traffic_participant, geo.traffic_participant)

    def test_to_orm(self):

        orm = self.tj.as_orm()

        for pose in orm.poses:
            self.assertIsInstance(pose, PoseORM)
            self.assertIsInstance(pose.traffic_participant, TrafficParticipantORM)
            self.assertEqual(
                pose.traffic_participant.id_object, orm.traffic_participant.id_object
            )

        self.assertEqual(
            self.tj.traffic_participant.id_object, orm.traffic_participant.id_object
        )

    def test_to_tasi(self):

        tasi = self.tj.as_tasi()

        # ensure same length
        self.assertEqual(len(self.poses), len(tasi))

        # ensure id_object of traffic participant is available on TASI id
        self.assertEqual(self.traffic_participant.id_object, tasi.id)

    def test_from_tasi(self):

        tasi = self.tj.as_tasi()

        self.assertEqual(tasi.iloc[0].velocity.easting.item(), self.poses[0].velocity.x)
        self.assertEqual(
            tasi.iloc[0].velocity.northing.item(), self.poses[0].velocity.y
        )
        self.assertTrue(tasi.velocity.iloc[0].magnitude.isna().item())

        # check interval against poses - ensure sorted
        self.assertEqual(tasi.interval.left, self.poses[0].timestamp)
        self.assertEqual(tasi.interval.right, self.poses[-1].timestamp)

        for p in self.tj.poses:
            self.assertIsNotNone(p.timestamp)

        tj2 = TrajectoryPublic.from_tasi(tasi)

        for p in tj2.poses:
            self.assertIsNotNone(p.timestamp)

        # full traffic participant
        self.assertEqual(self.tj.traffic_participant, tj2.traffic_participant)

        # check by attribute by attribute
        for attr in [
            "id_object",
            "start_time",
            "end_time",
            "dimension",
            "classifications",
        ]:
            self.assertEqual(
                getattr(self.tj.traffic_participant, attr),
                getattr(tj2.traffic_participant, attr),
            )

        # check poses equal
        for p1, p2 in zip(self.tj.poses, tj2.poses):

            # check traffic participant equal
            self.assertEqual(p1.traffic_participant, p2.traffic_participant)

            # check by attribute
            self.assertEqual(p1.classifications, p2.classifications)
            self.assertEqual(p1.velocity, p2.velocity)
            self.assertEqual(p1.acceleration, p2.acceleration)

            # check boundingbox by positions
            for node in p1.boundingbox.model_dump().keys():
                self.assertEqual(
                    getattr(p1.boundingbox, node).easting,
                    getattr(p2.boundingbox, node).easting,
                )
                self.assertEqual(
                    getattr(p1.boundingbox, node).northing,
                    getattr(p2.boundingbox, node).northing,
                )


class GeoTrajectoryConversion(TrajectoryTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.tj = TrajectoryPublic(
            poses=cls.poses, traffic_participant=cls.traffic_participant
        ).as_geo()

    def test_to_orm(self):

        orm = self.tj.as_orm()

        for pose in orm.poses:
            self.assertIsInstance(pose, GeoPoseORM)
            self.assertIsInstance(pose.position, str)

            self.assertIsInstance(pose.traffic_participant, TrafficParticipantORM)
            self.assertEqual(
                pose.traffic_participant.id_object, orm.traffic_participant.id_object
            )

        self.assertEqual(
            self.tj.traffic_participant.id_object, orm.traffic_participant.id_object
        )
