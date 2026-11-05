from tasi.utils import has_extra

if not has_extra("download"):
    raise ImportError(
        "The download extra is missing but required for the DLR datasets. Please install tasi[download] to get access to it."
    )

from .dataset import (
    DLRDatasetManager,
    DLRHTVersion,
    DLRTrajectoryDataset,
    DLRUTTrafficLightDataset,
    DLRUTVersion,
    ObjectClass,
)

try:
    from .dataset import DLRHTDatasetManager, DLRUTDatasetManager
except ImportError:
    pass
