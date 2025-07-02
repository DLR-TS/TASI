
Acceleration
=============

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.Acceleration
    :parts: 1

A traffic participant's acceleration as a three-dimensional vector measured in
:math:`\frac{m}{s^2}`. 


Factory methods
***************

.. autosummary::
   :toctree: api/

   ~Acceleration.from_tasi
   ~Acceleration.from_orm

Conversion
************

.. autosummary::
   :toctree: api/

   ~Acceleration.as_dataframe
   ~Acceleration.as_tasi
   ~Acceleration.as_orm

Attributes
***********

.. autosummary::
   :toctree: api/

   ~Acceleration.x
   ~Acceleration.y
   ~Acceleration.magnitude
