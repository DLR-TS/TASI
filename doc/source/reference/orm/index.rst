.. _api.orm_models:

Object Relation Mapper models
===============================


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

    tasi.io.orm.AccelerationORM
    tasi.io.orm.BoundingBoxORM
    tasi.io.orm.ClassificationsORM
    tasi.io.orm.DimensionORM
    tasi.io.orm.PositionORM
    tasi.io.orm.VelocityORM
    tasi.io.orm.TrafficLightStateORM

Entities
**********

.. autosummary::
   :toctree: api/

    tasi.io.orm.PoseORM
    tasi.io.orm.TrajectoryORM
    tasi.io.orm.TrafficParticipantORM
    tasi.io.orm.TrafficLightORM


Geo Entities
**************


.. autosummary::
   :toctree: api/

    tasi.io.orm.geo.GeoPoseORM
    tasi.io.orm.geo.GeoTrajectoryORM

