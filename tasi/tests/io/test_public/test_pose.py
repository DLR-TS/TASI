from datetime import datetime
from unittest import TestCase

import pandas as pd
from pydantic import ValidationError

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


class TestPoseInit(TestCase):

    def test_init(self):

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        p = PosePublic(
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

    def test_init_invalid_orientation(self):

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        with self.assertRaises(ValidationError):

            p = PosePublic(
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
                orientation=90,
            )


class PoseConversion(TestCase):

    @classmethod
    def setUpClass(cls):

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        cls.pose = PosePublic(
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

    def test_to_geopose(self):

        geo = self.pose.as_geo()

        self.assertEqual(geo.position.coordinates.latitude, self.pose.position.easting)
        self.assertEqual(
            geo.position.coordinates.longitude, self.pose.position.northing
        )

        self.assertEqual(geo.orientation, self.pose.orientation)

    def test_to_orm(self):

        orm = self.pose.as_orm()

        self.assertEqual(orm.position.easting, self.pose.position.easting)
        self.assertEqual(orm.position.northing, self.pose.position.northing)

        self.assertEqual(orm.velocity.x, self.pose.velocity.x)
        self.assertEqual(orm.velocity.y, self.pose.velocity.y)

        for p, bbox_position in self.pose.boundingbox.model_dump().items():
            self.assertEqual(
                getattr(orm.boundingbox, p).easting, bbox_position["easting"]
            )
            self.assertEqual(
                getattr(orm.boundingbox, p).northing, bbox_position["northing"]
            )

    def test_to_tasi(self):

        tasi = self.pose.as_tasi()

        self.assertEqual(1, len(tasi))
        self.assertIn("timestamp", tasi.index.names)
        self.assertIn("id", tasi.index.names)

        self.assertIsInstance(tasi.index, pd.MultiIndex)
        self.assertIn(self.pose.traffic_participant.id_object, tasi.index[0])
        self.assertIn(self.pose.timestamp, tasi.index[0])


class GeoPoseConversion(TestCase):

    @classmethod
    def setUpClass(cls):

        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=0, northing=0, altitude=0)

        cls.pose = PosePublic(
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

    def test_to_pose_conversion(self):
        self.pose.as_pose()
