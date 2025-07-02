from datetime import datetime

from sqlmodel import Session

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
from tasi.tests.io.test_orm import DBTestCase


class TestPoseSave(DBTestCase):

    def setUp(self) -> None:
        super().setUp()

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        self.pose = PosePublic(
            dimension=dimension,
            position=Position(easting=50000, northing=50000, altitude=1),
            velocity=Velocity(x=1, y=1, z=0),
            acceleration=Acceleration(),
            boundingbox=BoundingBox.from_dimension(dimension, relative_to=position),
            classifications=Classifications(pedestrian=1),
            traffic_participant=TrafficParticipant(
                classifications=Classifications(pedestrian=1),
                dimension=dimension,
                id_object=1,
            ),
            timestamp=datetime.now(),
            orientation=0,
        )

    def test_save_pose(self):

        from tasi.io.orm.pose import PoseORM

        pose_orm = self.pose.as_orm()

        with Session(self.engine) as sess:
            sess.add(pose_orm)
            sess.commit()

            sess.refresh(pose_orm)

            # verify entity has an id
            self.assertIsNotNone(pose_orm.id)

            # verify entity has an id
            self.assertIsNotNone(pose_orm.traffic_participant)

            # try refetch obj
            obj = sess.get(PoseORM, pose_orm.id)

            # verify entity has an id
            self.assertIsNotNone(obj)

            self.assertEqual(obj, pose_orm)

            # try create pose from orm
            pose = PosePublic.from_orm(obj)

            # verify entity has an id
            self.assertIsNotNone(obj.traffic_participant)

            self.assertEqual(
                pose.traffic_participant.id_object, obj.traffic_participant.id_object
            )
            self.assertEqual(pose.traffic_participant, self.pose.traffic_participant)


class TestGeoPoseSave(DBTestCase):

    def setUp(self) -> None:
        super().setUp()

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        self.pose = PosePublic(
            dimension=dimension,
            position=Position(easting=50000, northing=50000, altitude=1),
            velocity=Velocity(x=1, y=1, z=0),
            acceleration=Acceleration(),
            boundingbox=BoundingBox.from_dimension(dimension, relative_to=position),
            classifications=Classifications(pedestrian=1),
            traffic_participant=TrafficParticipant(
                classifications=Classifications(pedestrian=1),
                dimension=dimension,
                id_object=1,
            ),
            timestamp=datetime.now(),
            orientation=0,
        ).as_geo()

    def test_save_pose(self):

        from tasi.io.orm.pose import GeoPoseORM

        pose_orm = self.pose.as_orm()

        with Session(self.engine) as sess:
            sess.add(pose_orm)
            sess.commit()

            sess.refresh(pose_orm)

            # verify entity has an id
            self.assertIsNotNone(pose_orm.id)

            # verify entity has an id
            self.assertIsNotNone(pose_orm.traffic_participant)

            # try refetch obj
            obj = sess.get(GeoPoseORM, pose_orm.id)

            # verify entity has an id
            self.assertIsNotNone(obj)

            self.assertEqual(obj, pose_orm)

            # try create pose from orm
            pose: GeoPosePublic = GeoPosePublic.from_orm(obj)

            # verify entity has an id
            self.assertIsNotNone(obj.traffic_participant)
            self.assertIsNotNone(pose.boundingbox)
            self.assertIsNotNone(pose.position)

            self.assertEqual(
                pose.traffic_participant.id_object, obj.traffic_participant.id_object
            )
            self.assertEqual(pose.traffic_participant, self.pose.traffic_participant)
