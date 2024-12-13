from tasi.plotting.plot import TrajectoryPlotter
from tasi.dlr.dataset import ObjectClass


class DLRTrajectoryPlotter(TrajectoryPlotter):
    """
    Plot DLR trajectories using ``matplotlib``
    """

    OBJECT_CLASS_COLORS = {i.name: i.value for i in ObjectClass}
