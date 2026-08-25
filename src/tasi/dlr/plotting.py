from tasi.dlr.dataset import ObjectClass
from tasi.plotting.plot import TrajectoryPlotter


class DLRTrajectoryPlotter(TrajectoryPlotter):
    """
    Plot DLR trajectories using ``matplotlib``
    """

    OBJECT_CLASS_COLORS = {i.name: i.value for i in ObjectClass}
