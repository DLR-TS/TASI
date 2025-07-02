from sqlmodel import Session

from tasi.io.orm.trajectory import GeoTrajectoryORM, TrajectoryORM
from tasi.io.public.trajectory import GeoTrajectoryPublic, TrajectoryPublic
from tasi.tests.io.test_orm import DBTestCase
from tasi.tests.io.test_public.test_trajectory import TrajectoryTestCase


class TrajectoryDBCase(DBTestCase, TrajectoryTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.tj = TrajectoryPublic(
            poses=cls.poses, traffic_participant=cls.traffic_participant
        )


class TestTrajectorySave(TrajectoryDBCase):

    def test_save_pose(self):

        tj_orm = self.tj.as_orm()

        with Session(self.engine) as sess:
            sess.add(tj_orm)
            sess.commit()

            sess.refresh(tj_orm)

            # verify entity has an id
            self.assertIsNotNone(tj_orm.id)

            # verify entity has an id
            self.assertIsNotNone(tj_orm.traffic_participant)

            # try refetch obj
            obj = sess.get(TrajectoryORM, tj_orm.id)

            # verify entity has an id
            self.assertIsNotNone(obj)

            self.assertEqual(obj, tj_orm)

            # try create pose from orm
            tj = TrajectoryPublic.from_orm(obj)

            # verify entity has an id
            self.assertIsNotNone(obj.traffic_participant)

            self.assertEqual(
                tj.traffic_participant.id_object, obj.traffic_participant.id_object
            )
            self.assertEqual(tj.traffic_participant, self.tj.traffic_participant)


class TestGeoTrajectorySave(TrajectoryDBCase):

    def test_save_pose(self):

        tj_orm = self.tj.as_geo().as_orm()

        with Session(self.engine) as sess:
            sess.add(tj_orm)
            sess.commit()

            sess.refresh(tj_orm)

            # verify entity has an id
            self.assertIsNotNone(tj_orm.id)

            # verify entity has an id
            self.assertIsNotNone(tj_orm.traffic_participant)

            # try refetch obj
            obj = sess.get(GeoTrajectoryORM, tj_orm.id)

            # verify entity has an id
            self.assertIsNotNone(obj)

            self.assertEqual(obj, tj_orm)

            # try create pose from orm
            obj: GeoTrajectoryPublic = GeoTrajectoryPublic.from_orm(obj)

            # verify entity has an id
            self.assertIsNotNone(obj.traffic_participant)
            self.assertIsNotNone(obj.poses)
