from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from pydantic import field_serializer, field_validator
from shapely import to_geojson, wkt
from sqlalchemy import Column, func
from sqlmodel import Field, Relationship

from tasi.io.base.trajectory import TrajectoryORMBase
from tasi.io.orm.pose import GeoPoseORM, PoseORM, TrafficParticipantORM

__all__ = ["TrajectoryORM", "GeoTrajectoryORM"]


class TrajectoryORM(TrajectoryORMBase, table=True):

    poses: list[PoseORM] = Relationship(back_populates="trajectory")

    traffic_participant: TrafficParticipantORM = Relationship(  # type: ignore
        back_populates="trajectory",
    )


class GeoTrajectoryORM(TrajectoryORMBase, table=True):

    poses: list["GeoPoseORM"] = Relationship(back_populates="trajectory")

    geometry: str = Field(sa_column=Column(Geometry("LINESTRING", srid=32632)))

    traffic_participant: TrafficParticipantORM = Relationship(  # type: ignore
        back_populates="geotrajectory",
    )

    @field_validator("geometry", mode="before")
    def convert_geom_to_geojson(cls, v):
        if v is None:
            # Probably unnecessary if field is not nullable
            return None
        elif isinstance(v, WKBElement):
            # e.g. session.get results in a `WKBElement`
            v = func.ST_AsGeoJSON(v)
        return to_geojson(wkt.loads(v))

    @field_serializer("geometry")
    def convert_geometry_to_geojson(self, geometry: WKBElement | str):
        import json

        try:
            json.loads(geometry)  # type: ignore

            return geometry
        except:
            return to_geojson(to_shape(geometry))  # type: ignore


MODELS = [TrajectoryORM, GeoTrajectoryORM]
