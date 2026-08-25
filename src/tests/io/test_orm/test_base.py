from datetime import datetime

from sqlalchemy.orm import Session

from tasi.io import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    PosePublic,
    Position,
    TrafficParticipant,
    Velocity,
)
from tests.io.test_orm import DBTestCase


class TestBaseInit(DBTestCase):

    def test_dimension(self):
        Dimension(width=1, height=1, length=1).as_orm()

    def test_position(self):
        Position(easting=50000, northing=50000, altitude=1).as_orm()

    def test_velocity(self):
        Velocity(x=1, y=1, z=0).as_orm()

    def test_boundingbox(self):
        dimension = Dimension(width=1, height=1, length=1)
        position = Position(easting=50000, northing=50000, altitude=1)

        BoundingBox.from_dimension(dimension, relative_to=position).as_orm()

    def test_classifications(self):
        Classifications(pedestrian=1).as_orm()
