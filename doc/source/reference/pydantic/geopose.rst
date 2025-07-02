.. _api.public.GeoPosePublic:

GeoPosePublic
========================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.GeoPosePublic
    :parts: 1
    
A ``Pose`` specialized for trajectory data representing the state of a traffic participant for a specific point in time
but with position information encoded as `GeoObject` using the *GeoJSON* format.



Factory methods
****************

.. autosummary::
   :toctree: api/

   GeoPosePublic.from_orm
   GeoPosePublic.from_tasi
   GeoPosePublic.from_pose
   GeoPosePublic.model_validate


Conversion
************

.. autosummary::
   :toctree: api/

   GeoPosePublic.as_orm
   GeoPosePublic.as_tasi
   GeoPosePublic.as_pose

Attributes
***********

.. autosummary::
   :toctree: api/

   GeoPosePublic.timestamp
   GeoPosePublic.dimension
   GeoPosePublic.classifications
   GeoPosePublic.position
   GeoPosePublic.velocity
   GeoPosePublic.acceleration
   GeoPosePublic.boundingbox
   GeoPosePublic.traffic_participant
