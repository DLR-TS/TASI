from unittest import TestCase


class TestModuleImport(TestCase):

    def load_dataset(self):
        from tasi.dataset import Dataset

    def load_traffic_light_dataset(self):
        from tasi.dataset import TrafficLightDataset

    def load_weather_dataset(self):
        from tasi.dataset import WeatherDataset

    def load_trajectory_dataset(self):
        from tasi.dataset import TrajectoryDataset
