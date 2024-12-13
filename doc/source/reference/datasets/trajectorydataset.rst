.. _api.datasets.trajectorydataset:

TrajectoryDataset
========================

.. currentmodule:: tasi 

A ``Dataset`` specialized for trajectory data.


Constructor
************

.. autosummary::
   :toctree: api/

   TrajectoryDataset


Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   TrajectoryDataset.from_csv

Indexing
*********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.trajectory

Filtering
***********

.. autosummary::
   :toctree: api/

   TrajectoryDataset.most_likely_class
   TrajectoryDataset.get_by_object_class

All ``pandas`` ``DataFrame`` methods are also available.