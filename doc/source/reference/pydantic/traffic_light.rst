.. _api.public.TrafficLight:

TrafficLight
========================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.TrafficLight
    :parts: 1

A `TrafficLight` represents the state of traffic light entity for a specific
point in time.



Factory methods
****************

.. autosummary::
   :toctree: api/

   TrafficLight.from_tasi
   TrafficLight.model_validate


Conversion
************

.. autosummary::
   :toctree: api/

   TrafficLight.as_tasi

Attributes
***********

.. autosummary::
   :toctree: api/

   TrafficLight.timestamp
   TrafficLight.flashing
   TrafficLight.state
   TrafficLight.index
   

