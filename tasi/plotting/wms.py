import io as _io
import urllib
from copy import copy

import PIL.Image as _Image
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
