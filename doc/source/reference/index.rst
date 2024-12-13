.. _api:

API reference
#################

The API reference provides an overview of all public objects, functions and methods implemented in ``tasi``. All classes and function exposed in ``tasi.*`` namespace plus those listed in the reference are public.


Basic models
**************

Traffic data is represented with different ``Dataset`` variants that are available via ``tasi.*`` or ``tasi.dataset.*``. 

.. toctree::
   :maxdepth: 2
   
   datasets/index


DLR specific models 
********************

There are some specific classes that may help to work with the DLR datasets that are available via ``tasi.dlr.*``.

.. toctree::
   :maxdepth: 2

   dlr/index

Visualization 
**************

`tasi` provides various tools that may help with visualization traffic data.


.. toctree::
   :maxdepth: 2

   plotting/index
