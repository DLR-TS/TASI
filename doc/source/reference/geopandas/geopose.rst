.. _api.pose.GeoPose:

GeoPose
========================

.. currentmodule:: tasi

A ``Pose`` specialized for trajectory data representing the state of a traffic participant for a specific point in time
but with position information encoded as `GeoObject` using `shapely <https://shapely.readthedocs.io/en/stable/manual.html>`_.

.. inheritance-diagram:: tasi.GeoPose
    :top-classes: pandas.core.frame.DataFrame, tasi.pose:Pose, geopandas.geodataframe.GeoDataFrame
    :parts: 1


Attributes
***********

.. autosummary::
   :toctree: api/

   GeoPose.id
   GeoPose.timestamp

.. note::

    All ``geopandas`` ``GeoDataFrame`` methods are also available.