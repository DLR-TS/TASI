.. _api.trajectory.Trajectory:

Trajectory
========================

.. currentmodule:: tasi

A :py:class:`Trajectory` specialized for trajectory data representing the evolution of a traffic participant. A
trajectory is a collection of :py:class:`Pose`s.



Serialization / IO / conversion
************************************

.. autosummary::
   :toctree: api/

   Trajectory.from_csv
   Trajectory.as_geo

Indexing
*********

.. autosummary::
   :toctree: api/

   Trajectory.att
   TrajectoryDataset.trajectory

Filtering
***********

.. autosummary::
   :toctree: api/

   Trajectory.during

Analysis
**********

.. autosummary::
   :toctree: api/

   Trajectory.most_likely_class

Attributes
***********

.. autosummary::
   :toctree: api/

   Trajectory.attributes
   Trajectory.id
   Trajectory.interval
   Trajectory.timestamps


.. note::

    All ``pandas`` ``DataFrame`` methods are also available.