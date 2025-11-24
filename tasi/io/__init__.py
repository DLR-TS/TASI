from tasi.utils import has_extra

EXTRA = has_extra("io")

if not EXTRA:
    raise ImportError(
        "The io extra is missing but required for the io interface. Please install tasi[io] to get access to it."
    )

from .public import *
