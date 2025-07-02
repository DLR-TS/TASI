from typing import Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from pydantic import field_serializer, field_validator
from shapely import to_geojson, wkt
from sqlalchemy import Column, UniqueConstraint, func
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship

from tasi.io.base.pose import PoseBase
from tasi.io.env import DEFAULT_DATABASE_SETTINGS
from tasi.io.orm.base import (
    AccelerationORM,
    BoundingBoxORM,
    ClassificationsORM,
    DimensionORM,
    IdPrimaryKeyMixing,
    ORMBase,
    PositionORM,
    VelocityORM,
)
from tasi.io.orm.traffic_participant import TrafficParticipantORM


class PoseORMBase(PoseBase, ORMBase, IdPrimaryKeyMixing):

    @declared_attr  # type: ignore
    def __table_args__(cls):
        return (
            UniqueConstraint(
                "timestamp",
                "id_traffic_participant",
                name="uniq_pose_per_trajectory_scene" + cls.__tablename__,
            ),
            {"schema": DEFAULT_DATABASE_SETTINGS.CONTEXT},
        )

    # The dimension of the traffic participant at that time
    id_dimension: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.dimension.id"
    )

    id_traffic_participant: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trafficparticipant.id",
    )

    id_velocity: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.velocity.id"
    )

    id_acceleration: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.acceleration.id",
    )

    id_boundingbox: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.boundingbox.id",
    )

    id_classification: int | None = Field(
        default=None,
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.classifications.id",
    )


class PoseORM(PoseORMBase, table=True):

    dimension: DimensionORM = Relationship()

    # The position in local UTM coordinates
    id_position: int | None = Field(
        default=None,
        description="The position in local UTM coordinates",
        foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.position.id",
    )
    position: PositionORM = Relationship()

    id_trajectory: int | None = Field(
        default=None, foreign_key=f"{DEFAULT_DATABASE_SETTINGS.CONTEXT}.trajectory.id"
    )

    trajectory: Optional["TrajectoryORM"] = Relationship(  # type: ignore
        back_populates="poses",
        sa_relationship_kwargs={"foreign_keys": "[PoseORM.id_trajectory]"},
    )  # type: ignore

    traffic_participant: TrafficParticipantORM = Relationship()

    velocity: VelocityORM = Relationship()

    acceleration: AccelerationORM = Relationship()

    boundingbox: BoundingBoxORM = Relationship()

    classifications: ClassificationsORM = Relationship()


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


MODELS = [PoseORM, GeoPoseORM]
