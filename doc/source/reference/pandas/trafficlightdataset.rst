.. _api.datasets.trafficlightdataset:

TrafficLightDataset
========================

.. currentmodule:: tasi

A ``Dataset`` specialized for traffic light data.


Constructor
************

.. autosummary::
   :toctree: api/

   TrafficLightDataset


Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   TrafficLightDataset.from_csv


Analysis
**********

.. autosummary::
   :toctree: api/

   TrafficLightDataset.synchronize

Attributes
***********

.. autosummary::
   :toctree: api/

   TrafficLightDataset.attributes
   TrafficLightDataset.ids
   TrafficLightDataset.interval
   TrafficLightDataset.timestamps

.. note::

    All ``pandas`` ``DataFrame`` methods are also available.