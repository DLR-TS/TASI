.. _api.datasets.geotrajectorydataset:

GeoTrajectoryDataset
========================

.. currentmodule:: tasi

A ``Dataset`` specialized for trajectory data with position information encoded as `GeoObject` using `shapely <https://shapely.readthedocs.io/en/stable/manual.html>`_.

.. inheritance-diagram:: tasi.GeoTrajectoryDataset
    :top-classes: pandas.core.frame.DataFrame, tasi.dataset.Dataset, geopandas.geodataframe.GeoDataFrame
    :parts: 1


Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   GeoTrajectoryDataset.from_csv

Indexing
*********

.. autosummary::
   :toctree: api/

   GeoTrajectoryDataset.atid

Filtering
***********

.. autosummary::
   :toctree: api/

   GeoTrajectoryDataset.during


Attributes
***********

.. autosummary::
   :toctree: api/

   GeoTrajectoryDataset.attributes
   GeoTrajectoryDataset.ids
   GeoTrajectoryDataset.interval
   GeoTrajectoryDataset.timestamps

.. note::

    All ``pandas`` ``DataFrame`` methods are also available.