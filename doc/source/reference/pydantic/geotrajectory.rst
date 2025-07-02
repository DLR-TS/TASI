.. _api.public.GeoTrajectoryPublic:

GeoTrajectoryPublic
========================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.GeoTrajectoryPublic
    :parts: 1

A ``GeoTrajectory`` specialized for trajectory data representing the state of a
traffic participant over a period of time but with position information encoded
as `GeoObject` using the *GeoJSON* format.


Factory methods
****************

.. autosummary::
   :toctree: api/

   GeoTrajectoryPublic.from_orm
   GeoTrajectoryPublic.from_tasi
   GeoTrajectoryPublic.from_trajectory
   GeoTrajectoryPublic.model_validate


Conversion
************

.. autosummary::
   :toctree: api/

   GeoTrajectoryPublic.as_orm
   GeoTrajectoryPublic.as_tasi
   GeoTrajectoryPublic.as_trajectory

Attributes
***********

.. autosummary::
   :toctree: api/

   GeoTrajectoryPublic.poses
   GeoTrajectoryPublic.traffic_participant
   GeoTrajectoryPublic.geometry

