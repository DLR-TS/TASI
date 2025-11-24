from unittest import TestCase


class TestModuleImport(TestCase):

    def load_dataset(self):
        from tasi.dataset.base import Dataset

    def load_traffic_light_dataset(self):
        from tasi.dataset.base import TrafficLightDataset

    def load_weather_dataset(self):
        from tasi.dataset.base import WeatherDataset

    def load_trajectory_dataset(self):
        from tasi.dataset.base import TrajectoryDataset
