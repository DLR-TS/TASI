
Position
=============

.. currentmodule:: tasi.io

.. inheritance-diagram:: tasi.io.Position
    :parts: 1

A traffic participant's position represented in the `UTM
<https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system>`_
coordinate system.


Factory methods
***************

.. autosummary::
   :toctree: api/

   ~Position.from_tasi
   ~Position.from_orm
   ~Position.from_wkt

Conversion
************

.. autosummary::
   :toctree: api/

   ~Position.as_dataframe
   ~Position.as_tasi
   ~Position.as_orm

Attributes
***********

.. autosummary::
   :toctree: api/

   ~Position.easting
   ~Position.northing
   ~Position.altitude
