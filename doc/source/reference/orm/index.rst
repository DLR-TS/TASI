.. _api.orm_models:

Object Relation Mapper models
===============================

.. currentmodule:: tasi.io.orm


To save traffic data into the database, the following models can be used.

.. note::

    Please use the `pydantic` models instead of creating instances of the
    attributes below. All of the `pydantic` entities implement the ``as_orm``
    method that can be used to convert every entity to its ORM-based
    representation.

Attributes 
***********

The following attributes are the basic attributes of the entities defined below.
They may help to convert data into the internal ``TASI`` data format.


.. autosummary::
   :toctree: api/

    AccelerationORM
    BoundingBoxORM
    ClassificationsORM
    DimensionORM
    PositionORM
    VelocityORM
    TrafficLightStateORM

Entities
**********

.. autosummary::
   :toctree: api/

    PoseORM
    GeoPoseORM
    TrajectoryORM
    GeoTrajectoryORM
    TrafficParticipantORM
    TrafficLightORM

