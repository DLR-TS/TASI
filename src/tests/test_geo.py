import geopandas as gpd

from tasi import GeoPose, GeoTrajectory, GeoTrajectoryDataset

from . import DatasetTestCase


class GeoConversionTestCase(DatasetTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ds = cls.ds.to_tasi()

    def test_to_geo_pose(self):

        geopose = self.ds.iloc[0].as_geo()

        self.assertIsInstance(geopose, gpd.GeoDataFrame)
        self.assertIsInstance(geopose, GeoPose)

    def test_to_geo_trajectory(self):

        geotrajectory = self.ds.trajectory(self.ds.ids[0]).as_geo()

        self.assertIsInstance(geotrajectory, gpd.GeoDataFrame)
        self.assertIsInstance(geotrajectory, GeoTrajectory)

    def test_to_geo_trajectory_position(self):

        geotrajectory = self.ds.trajectory(self.ds.ids[0]).as_geo(position="position")

        self.assertIsInstance(geotrajectory, gpd.GeoDataFrame)
        self.assertIsInstance(geotrajectory, GeoTrajectory)

    def test_to_geo_trajectory_front(self):

        geotrajectory = self.ds.trajectory(self.ds.ids[0]).as_geo(
            position=("boundingbox", "front")
        )

        self.assertIsInstance(geotrajectory, gpd.GeoDataFrame)
        self.assertIsInstance(geotrajectory, GeoTrajectory)

    def test_to_geo_trajectory_front_and_position(self):

        geotrajectory = self.ds.trajectory(self.ds.ids[0]).as_geo(
            position=[("boundingbox", "front"), "position"]
        )

        self.assertIn("position", geotrajectory)
        self.assertIn("front", geotrajectory)

        self.assertIsInstance(geotrajectory, gpd.GeoDataFrame)
        self.assertIsInstance(geotrajectory, GeoTrajectory)

    def test_to_geo_dataset(self):

        geodataset = self.ds.as_geo()

        self.assertIsInstance(geodataset, gpd.GeoDataFrame)
        self.assertIsInstance(geodataset, GeoTrajectoryDataset)
