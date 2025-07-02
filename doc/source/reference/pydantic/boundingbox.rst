
BoundingBox
=============

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.BoundingBox
    :parts: 1

A collection of various reference points of a traffic participant.


Positions
***********

.. autosummary::
   :toctree: api/

   ~BoundingBox.front_left
   ~BoundingBox.front
   ~BoundingBox.front_right
   ~BoundingBox.right
   ~BoundingBox.rear_right
   ~BoundingBox.rear
   ~BoundingBox.rear_left
   ~BoundingBox.left

Factory methods
***************

.. autosummary::
   :toctree: api/

   ~BoundingBox.from_tasi
   ~BoundingBox.from_orm
   ~BoundingBox.from_dimension

Conversion
***********

.. autosummary::
   :toctree: api/

   ~BoundingBox.as_tasi
   ~BoundingBox.as_orm