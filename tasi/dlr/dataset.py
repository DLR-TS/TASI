import logging
import tempfile
import zipfile
from enum import IntEnum
from pathlib import Path

import requests

from tasi.dataset import TrajectoryDataset

DLR_FOKR_DATASET_URL = 'https://zenodo.org/records/13907201/files/DLR-Urban-Traffic-dataset_v1-0-1.zip'


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
