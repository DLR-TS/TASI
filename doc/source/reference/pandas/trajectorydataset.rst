.. _api.datasets.trajectorydataset:

TrajectoryDataset
========================

.. currentmodule:: tasi

A ``Dataset`` specialized for trajectory data.


Constructor
************

.. autosummary::
   :toctree: api/

   TrajectoryDataset.from_attributes
   TrajectoryDataset.from_trajectories


Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   TrajectoryDataset.from_csv
   TrajectoryDataset.as_geo

Indexing
*********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.att
   TrajectoryDataset.atid
   TrajectoryDataset.trajectory

Filtering
***********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.get_by_object_class
   TrajectoryDataset.during

Analysis
**********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.most_likely_class
   TrajectoryDataset.roi

Attributes
***********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.attributes
   TrajectoryDataset.ids
   TrajectoryDataset.interval
   TrajectoryDataset.timestamps

.. note::

    All ``pandas`` ``DataFrame`` methods are also available.