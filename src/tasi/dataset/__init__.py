import os

from tasi.utils import has_extra

from .base import *

GEO_EXTRA = has_extra("geo")


DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

__all__ = [
    "Dataset",
    "TrajectoryDataset",
    "WeatherDataset",
    "AirQualityDataset",
    "RoadConditionDataset",
    "TrafficLightDataset",
    "TrafficVolumeDataset",
    "DATA_PATH",
]

if GEO_EXTRA:
    from .geo import *

    __all__.append(
        "GeoTrajectoryDataset",
    )
