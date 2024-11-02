from . import _version
from .dataset import Dataset, TrajectoryDataset, TrafficLightDataset, AirQualityDataset, RoadConditionDataset, WeatherDataset

__version__ = _version.get_versions()['version']

from .logging import init_logger

init_logger()