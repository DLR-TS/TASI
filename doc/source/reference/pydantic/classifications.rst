
Classifications
================

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.Classifications
    :parts: 1

The object type probability of a traffic participant. 


Factory methods
***************

.. autosummary::
   :toctree: api/

   ~Classifications.from_tasi
   ~Classifications.from_orm


Conversion
************

.. autosummary::
   :toctree: api/

   ~Classifications.as_dataframe
   ~Classifications.as_tasi
   ~Classifications.as_orm


Attributes
***********

.. autosummary::
   :toctree: api/

   ~Classifications.unknown
   ~Classifications.pedestrian
   ~Classifications.bicycle
   ~Classifications.motorbike
   ~Classifications.car
   ~Classifications.van
   ~Classifications.truck
   ~Classifications.other
