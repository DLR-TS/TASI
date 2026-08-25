from tasi.utils import has_extra

EXTRA = has_extra("visualization")

if EXTRA:
    from .plot import TrajectoryPlotter

    __all__ = ["TrajectoryPlotter"]
else:
    raise ImportError(
        "Please install tasi[visualization] for visualization capabilities."
    )
