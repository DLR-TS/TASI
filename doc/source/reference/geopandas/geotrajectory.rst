.. _api.Geotrajectory.GeoTrajectory:

GeoTrajectory
========================

.. currentmodule:: tasi

A :py:class:`GeoTrajectory` specialized for trajectory data representing the evolution of a traffic participant but with
position information enoded as `GeoObject` using `shapely <https://shapely.readthedocs.io/en/stable/manual.html>`_. A
Geotrajectory is a collection of :py:class:`tasi.GeoPose`.


.. inheritance-diagram:: tasi.GeoTrajectory
    :top-classes: pandas.core.frame.DataFrame, tasi.trajectory:Trajectory, geopandas.geodataframe.GeoDataFrame
    :parts: 1

Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   GeoTrajectory.from_csv

Indexing
*********

.. autosummary::
   :toctree: api/

   GeoTrajectory.att

Filtering
***********

.. autosummary::
   :toctree: api/

   GeoTrajectory.during

Analysis
**********

.. autosummary::
   :toctree: api/

   GeoTrajectory.most_likely_class

Attributes
***********

.. autosummary::
   :toctree: api/

   GeoTrajectory.attributes
   GeoTrajectory.id
   GeoTrajectory.interval
   GeoTrajectory.timestamps


.. note::

    All ``pandas`` ``DataFrame`` methods are also available.