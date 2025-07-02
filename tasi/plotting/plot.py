from typing import Tuple

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap
from tilemapbase.mapping import Plotter

from tasi.dataset import TrajectoryDataset
from tasi.plotting.wms import BoundingboxTiles


class BoundingboxPlotter(Plotter):
    """
    A specialization of the `tilemapbase.Plotter` to show tiles given a region as a boundingbox in UTM coordinates.
    """

    def __init__(
        self, extent: np.ndarray, tile_provider: BoundingboxTiles, padding: int = 0
    ):
        """
        Create a plotter for the given `extend` and using the provided `tile_provider`

        Args:
            extent (np.ndarray): A 2*2 matrix as the 2-point definition of the region to plot.
            tile_provider (ClassVar[BoundingboxTiles]): The tile provider to use for fetching tiles
            padding (int, optional): An additional padding in meters around the given extend. Defaults to 0.
        """

        self._extent = extent
        self._original_extent = extent
        self._tile_provider = tile_provider

        self._padding = padding

    def plot(
        self,
        ax: plt.Axes,
        position: Tuple[float, float] = None,
        zoom: float = 1,
        show_attribution: bool = True,
        attribution_kwargs=None,
        **kwargs
    ):
        """
        Draw the tile for the position position given by ``position`` within the current extend and and zoom into the tile according to `zoom`.

        Args:
            ax (plt.Axes): The axes to plot onto.
            position (Tuple[float, float]): The plotting position
            zoom (float): The zoom value
            show_attribution (bool): To thow the attribution information. Defaults to True.

        Raises:
            ValueError: If the zoom value is not within (0,1).

        """

        if zoom == 0 or zoom > 1:
            raise ValueError("The zoom value needs to be within (0,1).")

        # get the tile for the current extend
        tile = self._tile_provider.get_tile(
            self.xtilemin, self.ytilemin, self.xtilemax, self.ytilemax
        )

        # get the size of the extend
        dx = self.xtilemax - self.xtilemin
        dy = self.ytilemax - self.ytilemin

        # draw the tile on the axes and specify the extend in the given coordinate system
        ax.imshow(
            tile,
            interpolation="lanczos",
            extent=[
                int(self.xtilemin),
                int(self.xtilemax),
                int(self.ytilemin),
                int(self.ytilemax),
            ],
            **kwargs,
        )
        if position is None:
            position = [self.xtilemin + (dx / 2), self.ytilemin + (dy / 2)]

        # set the limit of the axes according to the given extend and zoom value
        ax.set(
            xlim=[position[0] - (dx / 2) * zoom, position[0] + (dx / 2) * zoom],
            ylim=[position[1] - (dy / 2) * zoom, position[1] + (dy / 2) * zoom],
        )

        if show_attribution:

            default_config = {
                "fontsize": 5,
                "transform": ax.transAxes,
                "s": self._tile_provider.ATTRIBUTION,
            }

            attribution_kwargs = (
                attribution_kwargs if attribution_kwargs is not None else {}
            )

            if dx > dy:

                default_config.update(
                    {"x": 1, "y": 1.01, "ha": "right", "va": "bottom"}
                )

                default_config.update(attribution_kwargs)

                ax.text(**default_config)

            else:

                default_config.update(
                    {"x": 1.02, "y": 0.01, "rotation": 90, "ha": "left", "va": "bottom"}
                )

                default_config.update(attribution_kwargs)

                ax.text(**default_config)

    @property
    def extent(self):
        """
        The region in 2-point definition

        Returns:
            np.ndarray: A 2*2 matrix
        """
        return self._original_extent

    @property
    def xtilemin(self) -> int:
        """
        The smallest x-coordinate in tilespace

        Returns:
            int: Minimum easting
        """
        return int(np.min(self._extent[:, 0])) - self._padding

    @property
    def xtilemax(self) -> int:
        """
        The greatest x-coordinate in tilespace

        Returns:
            int: Maximum easting
        """
        return int(np.max(self._extent[:, 0])) + self._padding

    @property
    def ytilemin(self) -> int:
        """
        The smallest y-coordinate in tilespace

        Returns:
            int: Minimum northing
        """
        return int(np.min(self._extent[:, 1])) - self._padding

    @property
    def ytilemax(self) -> int:
        """
        The greatest y-coordinate in tilespace

        Returns:
            int: Maximum northing
        """
        return int(np.max(self._extent[:, 1])) + self._padding


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
        color: str = None,
        ax: Axes = None,
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
