import logging
import tempfile
import zipfile
from enum import Enum, IntEnum
from pathlib import Path

import requests

from tasi.dataset import TrajectoryDataset


class DLRDatasetManager():

    BASE_URI = 'https://zenodo.org/records'

    @property 
    def archivename(self):
        """The base name of the archive"""
        return self.ARCHIVE[self.version]

    @property
    def name(self):
        """The name of the directory within the dataset's archive"""
        raise NotImplementedError('The name of the directory within the archive')

    @property
    def filename(self):
        """The full name of the archive including the version"""
        return f'{self.archivename}_{self.version.replace('.', '-')}.zip'

    @property
    def url(self):
        """The URL to download the dataset from"""
        return f"{self.BASE_URI}/{self.VERSION[self.version]}/files/{self.filename}"

    @property
    def version(self):
        return self._version

    def __init__(self, version: str, **kwargs):

        self._version = version.value if isinstance(version, Enum) else version

        super().__init__(**kwargs)

    def load(self, path: Path) -> str:
        """
        Download a specified DLR dataset.

        Args:
            path (Path): The destination path where the dataset will be saved.

        Returns:
            str: The path of the exported dataset.
        """

        path = path if isinstance(path, Path) else Path(path)

        # define final path
        export_path = path.joinpath(self.name)

        logging.info('Checking if dataset already downloaded %s', export_path.absolute())
        if not export_path.exists():

            logging.info(f'Downloading dataset from {self.url}')

            with tempfile.NamedTemporaryFile('w+b') as f:

                # download the zip file
                f.write(requests.get(self.url).content)

                # extract the zip file
                with zipfile.ZipFile(f) as tempzip:
                    tempzip.extractall(path.absolute())

            logging.info(f'Downloaded dataset to {export_path}')

        else:
            logging.info(f'Dataset already available at {export_path}')

        return export_path


class DLRUTDatasetManager(DLRDatasetManager):

    class VERSIONS(Enum):
        v1_0_0 = "v1.0.0"
        v1_0_1 = "v1.0.1"

    VERSION = {
        VERSIONS.v1_0_0.value : 11396372,
        VERSIONS.v1_0_1.value : 13907201
    }
        
    ARCHIVE = {
        VERSIONS.v1_0_0.value : "DLR-UT",
        VERSIONS.v1_0_1.value : "DLR-Urban-Traffic-dataset",
    }

    @classmethod
    def area(cls):
        return 'urban'

    @property
    def name(self):

        # fix name of DLR UT v1.0.1 dataset
        if self.version == self.VERSIONS.v1_0_1.value:
            return f'DLR-UT_v1-0-0'

        return f'{self.archivename}_{self.version.replace('.', '-')}'


class ObjectClass(IntEnum):
    """
    The supported object classes
    """
    unknown = 0
    background = 1
    pedestrian = 2
    bicycle = 3
    narrow_vehicle = 4
    car = 5
    van = 6
    truck = 7


class FokrTrajectoryDataset(TrajectoryDataset):

    @property
    def pedestrians(self):
        """
        Return the pedestrians of the dataset.

        Returns:
            ObjectDataset: Dataset of all pedestrians.
        """
        return self.get_by_object_class(ObjectClass.pedestrian)

    @property
    def bicycles(self):
        """
        Return the bicycles of the dataset.

        Returns:
            ObjectDataset: Dataset of all bicycles.
        """
        return self.get_by_object_class(ObjectClass.bicycle)

    @property
    def narrow_vehicle(self):
        """
        Return the motorbikes of the dataset.

        Returns:
            ObjectDataset: Dataset of all motorbikes.
        """
        return self.get_by_object_class(ObjectClass.motorbike)

    @property
    def cars(self):
        """
        Return the cars of the dataset.

        Returns:
            ObjectDataset: Dataset of all cars.
        """
        return self.get_by_object_class(ObjectClass.car)

    @property
    def vans(self):
        """
        Return the vans of the dataset.

        Returns:
            ObjectDataset: Dataset of all vans.
        """
        return self.get_by_object_class(ObjectClass.van)

    @property
    def trucks(self):
        """
        Return the trucks of the dataset.

        Returns:
            ObjectDataset: Dataset of all trucks.
        """
        return self.get_by_object_class(ObjectClass.truck)

    @property
    def unknown(self):
        """
        Return the unknown objects of the dataset.

        Returns:
            ObjectDataset: Dataset of all unknown objects.
        """
        return self.get_by_object_class(ObjectClass.unknown)

    @property
    def background(self):
        """
        Return the background objects of the dataset.

        Returns:
            ObjectDataset: Dataset of all background objects.
        """
        return self.get_by_object_class(ObjectClass.background)

    @property
    def mru(self):
        """
        Return the motorized road user of the dataset.

        Returns:
            ObjectDataset: Dataset of all motorized objects.
        """
        return self.get_by_object_class([ObjectClass.motorbike, ObjectClass.car, ObjectClass.van, ObjectClass.truck])

    @property
    def vru(self):
        """
        Return the vulnerable road user of the dataset.

        Returns:
            ObjectDataset: Dataset of all motorized objects.
        """
        return self.get_by_object_class([ObjectClass.pedestrian, ObjectClass.bicycle])


def download():
    
    from tasi.logging import init_logger

    init_logger()

    import argparse
    import sys

    parser = argparse.ArgumentParser(prog='dlr-downloader')
    parser.add_argument('--name', choices=['urban'], type=str, required=True)
    parser.add_argument('--version', type=str, required=True)
    parser.add_argument('--path', type=str, required=True)
    arguments = parser.parse_args(sys.argv[1:])

    # choose required dataset
    if arguments.name.lower() == 'urban':
        dataset_cls = DLRUTDatasetManager

    # ensure valid format of version
    version = arguments.version.replace('-', '.').replace('_', '.')
    if not version.startswith('v'):
        version = 'v' + version

    dataset = dataset_cls(version=version)
    dataset.load(path=Path(arguments.path))


if __name__ == '__main__':

    download()