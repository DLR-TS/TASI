.. _api.pose.Pose:

Pose
========================

.. currentmodule:: tasi

A ``Pose`` specialized for trajectory data representing the state of a traffic participant for a specific point in time.



Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   Pose.from_csv
   Pose.as_geo

Attributes
***********

.. autosummary::
   :toctree: api/

   Pose.id
   Pose.timestamp

.. note::

    All ``pandas`` ``DataFrame`` methods are also available.