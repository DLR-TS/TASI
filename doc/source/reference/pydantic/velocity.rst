
Velocity
=============

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.Velocity
    :parts: 1

A traffic participant's velocity as a three-dimensional vector measured in
:math:`\frac{m}{s}`. 


Factory methods
***************

.. autosummary::
   :toctree: api/

   ~Velocity.from_tasi
   ~Velocity.from_orm

Conversion
************

.. autosummary::
   :toctree: api/

   ~Velocity.as_dataframe
   ~Velocity.as_tasi
   ~Velocity.as_orm

Attributes
***********

.. autosummary::
   :toctree: api/

   ~Velocity.x
   ~Velocity.y
   ~Velocity.magnitude
