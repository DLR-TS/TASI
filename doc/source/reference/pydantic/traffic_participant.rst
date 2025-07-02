
TrafficParticipant
===================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.TrafficParticipant
    :parts: 1

A representation of a traffic participant. 

.. note::
    Please note that there is no ``TASI`` internal representation of a traffic participant. 


Factory methods
***************

.. autosummary::
   :toctree: api/

   ~TrafficParticipant.from_tasi
   ~TrafficParticipant.from_orm

Conversion
************

.. autosummary::
   :toctree: api/

   ~TrafficParticipant.as_dataframe
   ~TrafficParticipant.as_tasi
   ~TrafficParticipant.as_orm

Attributes
***********

.. autosummary::
   :toctree: api/

   ~TrafficParticipant.start_time
   ~TrafficParticipant.end_time
   ~TrafficParticipant.id_object
   ~TrafficParticipant.dimension
   ~TrafficParticipant.classifications
