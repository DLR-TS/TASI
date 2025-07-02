.. _api.public.PosePublic:

PosePublic
========================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.PosePublic
    :parts: 1

A ``Pose`` specialized for trajectory data representing the state of a traffic
participant for a specific point in time.


Factory methods
****************

.. autosummary::
   :toctree: api/

   PosePublic.from_orm
   PosePublic.from_tasi
   PosePublic.model_validate


Conversion
************

.. autosummary::
   :toctree: api/

   PosePublic.as_orm
   PosePublic.as_tasi

Attributes
***********

.. autosummary::
   :toctree: api/

   PosePublic.timestamp
   PosePublic.dimension
   PosePublic.classifications
   PosePublic.position
   PosePublic.velocity
   PosePublic.acceleration
   PosePublic.boundingbox
   PosePublic.traffic_participant

