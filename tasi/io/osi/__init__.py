from tasi.utils import has_extra

# publish if osi module is active
EXTRA = has_extra("osi")

if not EXTRA:
    raise ImportError(
        "The osi extra is missing but required for the osi interface. Please install tasi[osi] to get access to it."
    )

from .core import (
    convert,
    convert_ground_truth,
    convert_ground_truths,
    convert_moving_object,
    convert_trajectories,
    read,
    write,
)

__all__ = [
    "convert",
    "read",
    "write",
    "convert_ground_truth",
    "convert_ground_truths",
    "convert_moving_object",
    "convert_trajectories",
]
