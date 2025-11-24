from tasi.utils import has_extra

from .base import *

GEO_EXTRA = has_extra("geo")

__all__ = ["Trajectory"]

if GEO_EXTRA:
    from .geo import *

    __all__.append("GeoTrajectory")
