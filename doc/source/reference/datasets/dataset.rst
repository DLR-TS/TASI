.. _api.datasets.dataset:

Dataset
========

.. currentmodule:: tasi 

A ``Dataset`` is a tabular ``pandas`` data structure to manage time-series data.


Constructor
************

.. autosummary::
   :toctree: api/

   Dataset

Attributes
************

.. autosummary::
   :toctree: api/

   Dataset.attributes
   Dataset.ids
   Dataset.interval

Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   Dataset.from_csv

Indexing
*********

.. autosummary::
   :toctree: api/

   Dataset.att
   Dataset.atid

Filtering
***********

.. autosummary::
   :toctree: api/

   Dataset.during

All ``pandas`` ``DataFrame`` methods are also available.