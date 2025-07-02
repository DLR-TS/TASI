.. _api:

.. currentmodule:: tasi

API reference
#################

The API reference provides an overview of all public objects, functions and
methods implemented in ``TASI``. All classes and function exposed in ``tasi.*``
namespace plus those listed in the reference are public.


Datasets
**************

Traffic data is represented with different :py:class:`Dataset` variants that are
available via ``tasi.*`` or ``tasi.dataset.*``.

.. toctree::
   :maxdepth: 2

   datasets/index


Trajectory data
****************

While a :py:class:`Dataset` allows to represent traffic data, ``TASI`` contains
additional models to represent trajectory data. For that purpose, an
hierarchical view is used and combined with a the tabular representation used by
``pandas``.


Numerical representation
--------------------------

When working with trajectory data in  ``TASI``, you will encounter the following
three representation formats:

.. toctree::
   :maxdepth: 2

   pandas/index

The :py:class:`TrajectoryDataset` is a specific variant of a :py:class:`Dataset`
with trajectory specific functions. In fact, it is a collection of
:py:class:`Trajectory` objects. A :py:class:`Trajectory` is, as the name
indicates, the representation of a traffic participant's trajectory. A
trajectory is also a collection as the :py:class:`Dataset`, but instead of
trajectories it contains :py:class:`Pose` objects. That is, a :py:class:`Pose`
is the traffic participant's representation for a specific point in time. This
distinction enables to provide additional functionality that is specific to the
different representation variants.

Geospatial representation
--------------------------

The models above are all based on ``pandas`` and positional information is
typically encoded in two columns using UTM coordinates. Since trajectory data
always contains positional information, ``TASI`` also provides models that
allows to represent this information as ``GeoObjects``. To achieve this, the
three following models use ``geopandas`` instead of ``pandas``:

.. toctree::
   :maxdepth: 2

   geopandas/index


This ``geopandas`` based representation of trajectory data allows to use the
wonderful library ``shapely`` for computational geometry.


Pydantic representation
--------------------------

To exchange data between ``TASI`` and other tools, ``TASI`` comes shipped with a
representation layer that is build on `pydantic
<https://docs.pydantic.dev/latest/>`_ and that enables conversion between
different data formats. The models are available via `tasi.io.public` package.


.. toctree::
   :maxdepth: 2

   pydantic/index

Object-Relational Mapper models
-------------------------------

The representation level based on `pydantic` is levereged to convert ``TASI``
entities to other data formats. Moreover, since `SQLModel
<https://sqlmodel.tiangolo.com/>`_ is used for defining the attributes above,
all the entities can be saved into a database using both `SQLModel
<https://sqlmodel.tiangolo.com/>`_ and `SQLAlchemy
<https://www.sqlalchemy.org/>`_. The models are available via `tasi.io.orm` package.


.. toctree::
   :maxdepth: 2

   orm/index

DLR specific models
********************

There are some specific classes that may help to work with the DLR datasets that
are available via ``tasi.dlr.*``.

.. toctree::
   :maxdepth: 2

   dlr/index

Visualization
**************

``TASI`` provides various tools that may help with visualization traffic data.


.. toctree::
   :maxdepth: 2

   plotting/index
