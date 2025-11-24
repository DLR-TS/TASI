from tasi.utils import has_extra

EXTRA = has_extra("wms")

if not EXTRA:
    raise ImportError("Please install tasi[wms] for visualization of WMS layers.")

import io as _io
import urllib
from copy import copy
from typing import Tuple

import numpy as np
import PIL.Image as _Image
from matplotlib.axes import Axes
from tilemapbase.mapping import Plotter
from tilemapbase.tiles import Tiles


class BoundingboxTiles(Tiles):
    """
    A base class to provide tiles from an URL given a region as a boundingbox
    """

    DEFAULT_PARAMS = dict(
        width=512,
        height=512,
        crs="EPSG:25833",
        format="image/png",
        request="GetMap",
        layers="",
        version="",
        styles="",
    )
    """Dict: The default parameter to query a WMS server (GET parameters)"""

    WMS = None
    """str: The WMS URL to query"""

    SOURCE_NAME = None
    """str: The source name"""

    ATTRIBUTION = ""
    """str: Attribution to the WMS layer"""

    def __init__(self, width: float = None, height: float = None, *args, **kwargs):

        self.params = copy(self.DEFAULT_PARAMS)

        for key, value in kwargs.items():
            self.params[key] = value

        self._width = self.params.get("width", None) if width is None else width
        self._height = self.params.get("height", None) if height is None else height

        for attr in ["width", "height"]:
            if attr in self.params:
                del self.params[attr]

        if self.width is None and self.height is None:
            raise ValueError("Either specify a tile width or height")

        # This is a mandatory argument to the `Tiles` class, though we don't use it.
        kwargs["request_string"] = ""
        kwargs["source_name"] = self.SOURCE_NAME

        super().__init__(*args, **kwargs)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def _request_string(self, x1, y1, x2, y2):
        """Encodes the tile coords and name into a string for the query."""

        dx = x2 - x1
        dy = y2 - y1

        width = self.width
        height = self.height

        if width is not None:
            height = int(width / dx * dy)
        elif height is not None:
            width = int(height / dy * dx)

        return (
            f"{self.WMS.format(XMIN=int(x1), YMIN=int(y1), XMAX=int(x2), YMAX=int(y2))}"
            f"&{urllib.parse.urlencode({**self.params, **dict(width=width, height=height)})}"
        )

    def _request_http(self, request_string):
        return request_string

    def get_tile(self, x1, y1, x2, y2):
        tile = self._get_cache().fetch(self._request_string(x1, y1, x2, y2))

        if tile is None:
            return None
        try:
            fp = _io.BytesIO(tile)
            return _Image.open(fp)
        except BaseException:
            raise RuntimeError(
                "Failed to decode data for {} - @ {} extent".format(
                    self.name, [x1, y1, x2, y2]
                )
            )


class LowerSaxonyOrthophotoTile(BoundingboxTiles):
    """Tile that provides access to the WMS server of the LGLN."""

    WMS = "https://opendata.lgln.niedersachsen.de/doorman/noauth/dop_wms?bbox={XMIN},{YMIN},{XMAX},{YMAX}"

    DEFAULT_PARAMS = dict(
        width=512,
        height=512,
        service="WMS",
        crs="EPSG:25832",
        format="image/png",
        request="GetMap",
        layers="ni_dop20",
        styles="",
        version="1.3.0",
    )

    SOURCE_NAME = "LGLN"

    ATTRIBUTION = "(C) GeoBasis-DE/LGLN 2024 CC-BY 4.0"


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
        ax: Axes,
        position: Tuple[float, float] | None = None,
        zoom: float = 1,
        show_attribution: bool = True,
        attribution_kwargs=None,
        **kwargs,
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
            tile,  # type: ignore
            interpolation="lanczos",
            extent=(
                int(self.xtilemin),
                int(self.xtilemax),
                int(self.ytilemin),
                int(self.ytilemax),
            ),
            **kwargs,
        )
        if position is None:
            position = (self.xtilemin + (dx / 2), self.ytilemin + (dy / 2))

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
