.. _api.public.TrajectoryPublic:

TrajectoryPublic
========================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.TrajectoryPublic
    :parts: 1

A `Trajectory` specialized for trajectory data representing the state of a traffic
participant over a period of time.



Factory methods
****************

.. autosummary::
   :toctree: api/

   TrajectoryPublic.from_orm
   TrajectoryPublic.from_tasi
   TrajectoryPublic.model_validate


Conversion
************

.. autosummary::
   :toctree: api/

   TrajectoryPublic.as_orm
   TrajectoryPublic.as_tasi
   TrajectoryPublic.as_geo

Attributes
***********

.. autosummary::
   :toctree: api/

   TrajectoryPublic.poses
   TrajectoryPublic.traffic_participant

