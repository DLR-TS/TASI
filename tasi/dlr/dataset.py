import logging
import os
import tarfile
import zipfile
from enum import Enum, IntEnum
from io import TextIOWrapper
from pathlib import Path
from typing import List, Tuple, Union

import pandas as pd
import requests
from tqdm import tqdm

from tasi.base import PandasBase
from tasi.dataset import (
    AirQualityDataset,
    RoadConditionDataset,
    TrafficLightDataset,
    TrafficVolumeDataset,
    TrajectoryDataset,
    WeatherDataset,
)
from tasi.io.zenodo import ZenodoConnector
from tasi.tests import DATA_PATH

__all__ = [
    "DLRDatasetManager",
    "DLRUTVersion",
    "DLRUTDatasetManager",
    "ObjectClass",
    "DLRTrajectoryDataset",
    "DLRUTTrafficLightDataset",
    "DLRHTVersion",
    "DLRHTDatasetManager",
    "DLRWeatherDataset",
    "DLRAirQualityDataset",
    "DLRRoadConditionDataset",
    "download",
    "DLRUTConnector",
    "DLRHTConnector",
]


DLRUTConnector = ZenodoConnector("DLR Urban Traffic dataset", parent_id=11396371)
DLRHTConnector = ZenodoConnector("DLR Highway Traffic dataset", parent_id=14012005)


class DLRDatasetManager:
    """A base class for DLR dataset management

    Attributes:
        BASE_URI: The base URI for all DLR datasets on zenodo
    """

    BASE_URI: str = "https://zenodo.org/records"
    """str: The base URI of all DLR datasets
    """

    DATA_TYPES = {
        "air_quality": "raw_data",
        "road_condition": "raw_data",
        "traffic_lights": "raw_data",
        "trajectories": "raw_data",
        "weather": "raw_data",
        "traffic_volume": "meta_data",
        "openscenario": "meta_data",
    }
    VERSION_ENUM = None

    @property
    def archivename(self):
        """The base name of the archive"""
        return self.ARCHIVE[self.version]

    @property
    def filename(self):
        """The full name of the archive including the version"""
        return f"{self.archivename}_{self.version.replace('.', '-')}.zip"

    @property
    def url(self):
        """The URL to download the dataset from"""
        return f"{self.BASE_URI}/{self.VERSION[self.version]}/files/{self.filename}"

    @property
    def version(self):
        """The dataset version"""
        return self._version

    @property
    def name(self):

        # fix name of DLR UT v1.0.1 dataset
        if self.version == DLRUTVersion.v1_0_1.value:
            return "DLR-UT_v1-0-0"

        return f"{self.archivename}_{self.version.replace('.', '-')}"

    def __init__(
        self,
        version: str,
        path: str = DATA_PATH,
        download_chunk_size: int = 1024,
        **kwargs,
    ):

        if version == "latest":
            version = self.VERSION_ENUM.latest

        self._version = version.value if isinstance(version, Enum) else version

        self._path = path

        self._chunk_size = download_chunk_size

        super().__init__(**kwargs)

    def download(self, file: TextIOWrapper) -> int:

        logging.info(f"Downloading dataset from {self.url}")

        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get("content-length", 0))

        with tqdm(
            total=total_size, unit="B", unit_scale=True, desc=f"Downloading {self.name}"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=self._chunk_size):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))
        return total_size

    def extract(self, file: Path, path: Path):

        logging.info("Extract files from archive")

        if file.name.endswith(".zip"):

            with zipfile.ZipFile(file) as f:
                file_list = f.namelist()
                total_files = len(file_list)

                with tqdm(total=total_files, unit="file", desc="Extracting") as pbar:
                    for file_info in f.infolist():
                        pbar.update(1)
                        f.extract(file_info, path=path.absolute())

        elif file.name.endswith(".tar.bz2"):

            with tarfile.open(file) as f:
                file_list = [m for m in f.getmembers() if m.isfile()]
                total_files = len(file_list)

                with tqdm(total=total_files, unit="file", desc="Extracting") as pbar:
                    for member in file_list:
                        f.extract(member, path)
                        pbar.update(1)

    def load(self, path: Path = None) -> str:
        """
        Download a specified DLR dataset.

        Args:
            path (Path, optional): The destination path where the dataset will be saved.

        Returns:
            str: The path of the exported dataset.
        """

        if path is None:
            path = self._path

        # ensure format of path
        path = path if isinstance(path, Path) else Path(path)

        # define final path
        archive_path = path.joinpath(self.filename)
        export_path = path.joinpath(self.name)

        # check if dataset exists
        logging.info(
            "Checking if dataset already downloaded %s", export_path.absolute()
        )
        if export_path.exists():
            logging.info(f"Dataset already available at {export_path}")
        else:
            # check if compressed dataset exists
            if not archive_path.exists():

                # download it since it is not available
                with open(archive_path, "wb") as f:
                    _ = self.download(f)

            self.extract(archive_path, path)

        return export_path

    def _dataset(self, variant: str, path: Path = None) -> List[str]:
        """Searches for files in the dataset specified at ``path`` for dataset information ``variant``

        Args:
            path (Path): The path of the dataset.
            variant (str): The dataset information to search for

        Returns:
            List[str]: The files found in the dataset for the specified dataset information
        """
        raise NotImplementedError("This method is implemented in child classes.")

    def trajectory(self, path: Path = None) -> List[str]:
        """List of files with trajectory data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with trajectory data
        """
        return self._dataset("trajectories", path)

    def weather(self, path: Path = None) -> List[str]:
        """List of files with weather data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with weather data
        """
        return self._dataset("weather", path)

    def road_condition(self, path: Path = None) -> List[str]:
        """List of files with road condition information.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with road condition data
        """
        return self._dataset("road_condition", path)

    def traffic_volume(self, path: Path = None) -> List[str]:
        """List of files with traffic volume data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with traffic volume data
        """
        return self._dataset("traffic_volume", path)

    def openscenario(self, path: Path = None) -> List[str]:
        """List of files with OpenSCENARIO data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with OpenSCENARIO data
        """
        return self._dataset("openscenario", path)


class DLRUTDatasetManager(DLRDatasetManager):
    """A manager to load the DLR UT dataset from zenodo"""

    try:

        VERSION_ENUM = DLRUTConnector.get_version_enum()
        VERSION = DLRUTConnector.get_dois()
        """Dict[str, int]: An internal mapping between version and the zenodo id
        """

        ARCHIVE = dict(
            **{
                v: "DLR-Urban-Traffic-dataset"
                for v in [
                    key
                    for key in VERSION
                    if key != DLRUTConnector.get_version_enum().v1_0_0.value
                ]
            },
            **{DLRUTConnector.get_version_enum().v1_0_0.value: "DLR-UT"},
        )
    except requests.exceptions.RequestException:
        VERSION_ENUM = None
        VERSION = None

    @classmethod
    def area(cls):
        return "urban"

    def _dataset(self, variant: str, path: Path = None) -> List[str]:
        """Searches for files in the dataset specified at ``path`` for dataset information ``variant``

        Args:
            path (Path): The path of the dataset.
            variant (str): The dataset information to search for

        Returns:
            List[str]: The files found in the dataset for the specified dataset information
        """
        if path is None:
            path = self._path

        if not isinstance(path, Path):
            path = Path(path)

        # join dataset path and name
        path = path.joinpath(self.name)

        # add type of data
        if self.version not in [
            self.VERSION_ENUM.v1_0_0.value,
            self.VERSION_ENUM.v1_0_1.value,
            self.VERSION_ENUM.v1_1_0.value,
        ]:
            path = path.joinpath(self.DATA_TYPES[variant])

        # add variant of data
        path = path.joinpath(variant)

        # return file pathes of variant
        return [os.path.join(path, p) for p in sorted(os.listdir(path))]

    def traffic_lights(self, path: Path = None) -> List[str]:
        """List of files with traffic light data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with traffic light data
        """
        return self._dataset("traffic_lights", path)

    def air_quality(self, path: Path = None) -> List[str]:
        """List of files with air quality data.

        Args:
            path (Path): The path of the dataset

        Returns:
            List[str]: The files with air quality data
        """
        return self._dataset("air_quality", path)


class ObjectClass(IntEnum):
    """
    The supported object classes
    """

    pedestrian = 0
    bicycle = 1
    motorbike = 2
    car = 3
    van = 4
    truck = 5


class DLRTrajectoryDataset(TrajectoryDataset):

    @property
    def pedestrians(self):
        """
        Return the pedestrians of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all pedestrians.
        """
        return self.get_by_object_class(ObjectClass.pedestrian.name)

    @property
    def bicycles(self):
        """
        Return the bicycles of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all bicycles.
        """
        return self.get_by_object_class(ObjectClass.bicycle.name)

    @property
    def motorbikes(self):
        """
        Return the motorbikes of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all motorbikes.
        """
        return self.get_by_object_class(ObjectClass.motorbike.name)

    @property
    def cars(self):
        """
        Return the cars of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all cars.
        """
        return self.get_by_object_class(ObjectClass.car.name)

    @property
    def vans(self):
        """
        Return the vans of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all vans.
        """
        return self.get_by_object_class(ObjectClass.van.name)

    @property
    def trucks(self):
        """
        Return the trucks of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all trucks.
        """
        return self.get_by_object_class(ObjectClass.truck.name)

    @property
    def mru(self):
        """
        Return the motorized road user of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all motorized objects.
        """
        return self.get_by_object_class(
            [
                ObjectClass.motorbike.name,
                ObjectClass.car.name,
                ObjectClass.van.name,
                ObjectClass.truck.name,
            ]
        )

    @property
    def vru(self):
        """
        Return the vulnerable road user of the dataset.

        Returns:
            DLRTrajectoryDataset: Dataset of all motorized objects.
        """
        return self.get_by_object_class(
            [ObjectClass.pedestrian.name, ObjectClass.bicycle.name]
        )

    def to_tasi(self) -> TrajectoryDataset:
        return super().from_attributes(
            position=self.position,
            velocity=self.velocity,
            acceleration=self.acceleration,
            heading=self.yaw,
            classifications=self.classifications,
            dimension=self.dimension,
        )

    @classmethod
    def from_csv(cls, file, indices: Tuple = (), **kwargs):
        return (
            super()
            .from_csv(file, indices, seperator="_", **kwargs)
            .rename(columns={"center": "position"})
        )


class DLRUTTrafficLightDataset(TrafficLightDataset):

    def signal(self, signal_id: int):
        """
        Filter the dataset by a signal id.

        Args:
            signal_id (int): The id of the signal.

        Returns:
            `DLRUTTrafficLightDataset`: The data from the signal
        """
        return self.xs(signal_id, level=1)

    def signal_state(self, signal_state: int):
        """
        Filter the dataset by an signal state.

        Args:
            signal_state (int): The signal state used for filtering.

        Returns:
            `DLRUTTrafficLightDataset`: The data with the user defined signal state.
        """
        return self.loc[self["state"] == signal_state]


class DLRHTDatasetManager(DLRDatasetManager):
    """A manager to load the DLR HT dataset from zenodo"""

    try:
        VERSION_ENUM = DLRHTConnector.get_version_enum()
        VERSION = DLRHTConnector.get_dois()
        """Dict[str, int]: An internal mapping between version and the zenodo id
        """
    except requests.exceptions.RequestException:
        VERSION_ENUM = None
        VERSION = None

    @classmethod
    def area(cls):
        return "highway"

    @property
    def archivename(self):
        """The base name of the archive"""
        return "DLR-Highway-Traffic-dataset"

    def _dataset(self, variant: str, path: Path = None) -> List[str]:
        """Searches for files in the dataset specified at ``path`` for dataset information ``variant``

        Args:
            path (Path): The path of the dataset.
            variant (str): The dataset information to search for

        Returns:
            List[str]: The files found in the dataset for the specified dataset information
        """
        if path is None:
            path = self._path

        if not isinstance(path, Path):
            path = Path(path)

        # join dataset path and name, type and variant
        path = (
            path.joinpath(self.name)
            .joinpath(self.DATA_TYPES[variant])
            .joinpath(variant)
        )

        # return file pathes of variant
        return [os.path.join(path, p) for p in sorted(os.listdir(path))]


class AddIndexFromCSVMixin:

    @classmethod
    def from_csv(cls, file: str, indices: Union[List, str] = (), **kwargs):

        # hack to add an index to match TASI format
        df = pd.DataFrame(PandasBase.from_csv(file, indices, **kwargs))

        df[cls.ID_COLUMN] = "DLR"
        df.set_index(cls.ID_COLUMN, append=True, inplace=True)

        return cls(df)


class DLRWeatherDataset(AddIndexFromCSVMixin, WeatherDataset):

    pass


class DLRAirQualityDataset(AddIndexFromCSVMixin, AirQualityDataset):
    pass


class DLRRoadConditionDataset(AddIndexFromCSVMixin, RoadConditionDataset):
    pass


class DLRTrafficVolumeDataset(AddIndexFromCSVMixin, TrafficVolumeDataset):
    pass


DLRHTVersion = DLRHTDatasetManager.VERSION_ENUM
DLRUTVersion = DLRUTDatasetManager.VERSION_ENUM


def download():

    from tasi.logging import init_logger

    init_logger()

    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="dlr-downloader")
    parser.add_argument("--name", choices=["urban", "highway"], type=str, required=True)
    parser.add_argument("--version", type=str, required=True)
    parser.add_argument("--path", type=str, required=True)
    arguments = parser.parse_args(sys.argv[1:])

    # choose required dataset
    if arguments.name.lower() == "urban":
        dataset_cls = DLRUTDatasetManager
    elif arguments.name.lower() == "highway":
        dataset_cls = DLRHTDatasetManager

    # ensure valid format of version
    version = arguments.version.replace("-", ".").replace("_", ".")
    if not version.startswith("v") and version != "latest":
        version = "v" + version

    dataset = dataset_cls(version=version)
    dataset.load(path=Path(arguments.path))


if __name__ == "__main__":

    download()
