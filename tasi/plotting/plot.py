from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap

from tasi.dataset.base import TrajectoryDataset


class TrajectoryPlotter:
    """
    Plot trajectories using ``matplotlib``
    """

    OBJECT_CLASS_COLORS = None

    def __init__(self, color_palette: str = "tab10"):

        self.palette = plt.cm.get_cmap(color_palette)

        if not isinstance(self.palette, ListedColormap):
            raise TypeError(
                "Argument 'color_palette' is not of type 'matplotlib.colors.ListedColormap'"
            )

    def plot(
        self,
        dataset: TrajectoryDataset,
        color: str | None = None,
        ax: Axes | None = None,
        trajectory_kwargs=None,
        **kwargs
    ):
        """
        Plot trajectories using `matplotlib`

        Args:
            dataset (TrajectoryDataset): The dataset of trajectories to visualize.
            color (str, optional): The color of the trajectories. Defaults to None.
            ax (Axes, optional): The matplotlib axes. Defaults to None.
            trajectory_kwargs (Dict, optional): A mapping of traffic participant id to trajectory-specific plotting attributes. Defaults to None.
        """
        if ax is None:
            ax = plt.gca()

        trajectory_kwargs = trajectory_kwargs if trajectory_kwargs is not None else {}

        # get the classes for each trajectory
        tj_classes = dataset.most_likely_class().sort_index()

        # get mapping of classes to colors
        if self.OBJECT_CLASS_COLORS is None:
            object_class_colors = {c: i for i, c in enumerate(tj_classes.unique())}
        else:
            object_class_colors = self.OBJECT_CLASS_COLORS

        for tj_class, tj_id in zip(tj_classes, dataset.ids.sort_values()):

            # get the trajectory of the id
            tj = dataset.trajectory(tj_id)

            # get additional plotting arguments of this trajectory
            tj_kwargs = trajectory_kwargs.get(tj_id, {})

            if "c" not in tj_kwargs and "color" not in tj_kwargs:

                # color for this trajectory is not defined
                if color is None:

                    # set default color
                    tj_kwargs["color"] = self.palette(object_class_colors[tj_class])

                else:

                    # use color of all trajectories
                    tj_kwargs["color"] = color

            if "label" not in tj_kwargs:
                tj_kwargs["label"] = tj_class

            # use the position attribute since it is the default
            ax.plot(
                tj.position.easting,
                tj.position.northing,
                **tj_kwargs,
                **kwargs,
            )

        if len(trajectory_kwargs) == 0:

            # all object classes have the same color -> show legend of unique labels
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys())
