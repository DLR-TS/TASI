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
