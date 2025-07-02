from unittest import TestCase

import numpy as np

from tasi.io.public.base import BoundingBox, Dimension, Position


class TestBoundingbox(TestCase):

    def test_boundingbox_from_dimension(self):
        dimension = Dimension(width=1, height=1, length=2)

        bbox = BoundingBox.from_dimension(
            dimension, relative_to=Position(easting=0, northing=0, altitude=0)
        )

        positions = [
            [-1, 0],
            [-1, 0.5],
            [0, 0.5],
            [1, 0.5],
            [1, 0],
            [1, -0.5],
            [0, -0.5],
            [-1, -0.5],
        ]

        attrs = [
            "rear",
            "rear_left",
            "left",
            "front_left",
            "front",
            "front_right",
            "right",
            "rear_right",
        ]
        for posi, (x, y) in zip(attrs, positions):
            self.assertEqual(
                getattr(bbox, posi).easting, x, f"Failed with {posi}.easting"
            )
            self.assertEqual(
                getattr(bbox, posi).northing, y, f"Failed with {posi}.northing"
            )

    def test_boundingbox_from_dimension_and_relative_position(self):
        dimension = Dimension(width=1, height=1, length=2)

        bbox = BoundingBox.from_dimension(
            dimension, relative_to=Position(easting=2, northing=1, altitude=0)
        )

        positions = [
            [1, 1],
            [1, 1.5],
            [2, 1.5],
            [3, 1.5],
            [3, 1],
            [3, 0.5],
            [2, 0.5],
            [1, 0.5],
        ]

        attrs = [
            "rear",
            "rear_left",
            "left",
            "front_left",
            "front",
            "front_right",
            "right",
            "rear_right",
        ]
        for posi, (x, y) in zip(attrs, positions):
            self.assertEqual(
                getattr(bbox, posi).easting, x, f"Failed with {posi}.easting"
            )
            self.assertEqual(
                getattr(bbox, posi).northing, y, f"Failed with {posi}.northing"
            )

    def test_boundingbox_from_dimension_and_relative_position_and_orientation(self):
        dimension = Dimension(width=1, height=1, length=2)

        bbox = BoundingBox.from_dimension(
            dimension,
            relative_to=Position(easting=2, northing=1, altitude=0),
            orientation=np.pi / 2,
        )

        positions = [
            [2, 0],  # rear
            [1.5, 0],  # rear-left
            [1.5, 1],  # left
            [1.5, 2],  # front_left
            [2, 2],  # front
            [2.5, 2],  # front_right
            [2.5, 1],  # right
            [2.5, 0],  # rear_right
        ]

        attrs = [
            "rear",
            "rear_left",
            "left",
            "front_left",
            "front",
            "front_right",
            "right",
            "rear_right",
        ]
        for posi, (x, y) in zip(attrs, positions):
            self.assertEqual(
                getattr(bbox, posi).easting, x, f"Failed with {posi}.easting"
            )
            self.assertEqual(
                getattr(bbox, posi).northing, y, f"Failed with {posi}.northing"
            )
