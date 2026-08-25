from typing import List, Union

import pycountry
import reverse_geocode
from pyproj import Transformer

from tasi import Trajectory, TrajectoryDataset
from tasi.io import PosePublic, TrafficParticipant, TrajectoryPublic


def resolve_countrycode(
    obj: Union[
        TrajectoryDataset,
        List[TrajectoryPublic],
        List[Trajectory],
        TrajectoryPublic,
        Trajectory,
        PosePublic,
    ],
    epsg=32632,
) -> int:

    transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)

    # ensure non list
    if isinstance(obj, list):
        obj = obj[0]

    if isinstance(obj, (TrajectoryDataset, Trajectory)):
        pose = PosePublic.from_tasi(
            obj.iloc[0], tp=TrafficParticipant.from_tasi(obj.iloc[0])
        )
    elif isinstance(obj, PosePublic):
        pose = obj
    elif isinstance(obj, TrajectoryPublic):
        pose = obj.poses[0]

    # Output: Longitude, Latitude
    lon, lat = transformer.transform(pose.position.easting, pose.position.northing)

    country = pycountry.countries.get(
        alpha_2=reverse_geocode.get([lat, lon])["country_code"].upper()
    )

    return int(country.numeric)  # pyright: ignore[reportOptionalMemberAccess]
