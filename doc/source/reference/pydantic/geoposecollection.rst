.. _api.public.GeoPoseCollectionPublic:

GeoPoseCollectionPublic
========================

.. currentmodule:: tasi.io.geo

.. inheritance-diagram:: tasi.io.geo.GeoPoseCollectionPublic
    :parts: 1
    
A collection of ``Pose`` specialized for trajectory data representing the state
of a traffic participants a particular point in time with position information encoded as `GeoObject` using the *GeoJSON* format.



Factory methods
****************

.. autosummary::
   :toctree: api/

   GeoPoseCollectionPublic.model_validate


Attributes
***********

.. autosummary::
   :toctree: api/

   GeoPoseCollectionPublic.timestamp
   GeoPoseCollectionPublic.poses
