from typing import Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from pydantic import field_serializer, field_validator
from shapely import to_geojson, wkt
from sqlalchemy import Column, func
from sqlmodel import Field, Relationship

from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    TrafficParticipantORM,
    VelocityORM,
)

from .base import PoseORMBase

__all__ = ["GeoPoseORM"]


class GeoPoseORM(PoseORMBase, table=True):

    dimension: DimensionORM = Relationship()

    # The position in local UTM coordinates
    position: str = Field(sa_column=Column(Geometry("POINT", srid=31467)))

    id_trajectory: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.geotrajectory.id",
    )

    trajectory: Optional["GeoTrajectoryORM"] = Relationship(  # type: ignore
        back_populates="poses"
    )  # type: ignore

    traffic_participant: TrafficParticipantORM = Relationship()

    velocity: VelocityORM = Relationship()

    acceleration: AccelerationORM = Relationship()

    boundingbox: BoundingBoxORM = Relationship()

    classifications: ClassificationsORM = Relationship()

    @field_validator("position", mode="before")
    def convert_geom_to_geojson(cls, v):
        if v is None:
            # Probably unnecessary if field is not nullable
            return None
        elif isinstance(v, WKBElement):
            # e.g. session.get results in a `WKBElement`
            v = func.ST_AsGeoJSON(v)
        return to_geojson(wkt.loads(v))

    @field_serializer("position")
    def convert_geometry_to_geojson(self, position: WKBElement | str):
        import json

        try:
            json.loads(position)  # type: ignore

            return position
        except:
            return to_geojson(to_shape(position))  # type: ignore


MODELS = [GeoPoseORM]
