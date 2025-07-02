:html_theme.sidebar_secondary.remove:

.. tasi documentation master file, based on the (geo)pandas master file

TASI |version|
###############

``TASI`` is a library to provide high-performance, easy-to-use data structures and data analysis
tools for `Python`_ based traffic situation analysis applications. ``TASI`` extends `Pandas`_ with 
custom models to represent traffic data and utilizes `Matplotlib`_ for visualization. 

.. _pandas: https://pandas.pydata.org
.. _python: https://www.python.org/
.. _matplotlib: https://matplotlib.org


.. toctree::
   :hidden:

   Home <self>
   About <about>
   Getting started <getting_started/index>
   User guide <user_guide/index>
   API <reference/index>
   Contribute <development/index>

.. container:: button

    :doc:`Getting started <getting_started/index>` :doc:`User guide <user_guide/index>`
    :doc:`About TASI <about>` :doc:`Contribute <development/index>`

.. note::
    This is first release version and ``TASI`` and currently focus on providing tools that enables you to work with the traffic datasets provided by members of the DLR  `TS`_ members. We will consecutively extend ``TASI`` to a Python library for traffic data management and analysis, situation visualization, situation criticality analysis and scenario creation, while providing access to common traffic datasets. Stay tuned |:grin:|

Useful links
***************

`Binary Installers (PyPI) <https://pypi.org/project/tasi/>`_ | `Source Repository (GitHub) <https://github.com/dlr-ts/tasi>`_ | `Issues & Ideas <https://github.com/dlr-ts/tasi/issues>`_ | `Q&A Support <https://stackoverflow.com/questions/tagged/tasi>`_

|pypi| |Developed by DLR-TS| |zenodo|

.. |pypi| image:: https://img.shields.io/pypi/v/tasi.svg
   :target: https://pypi.python.org/pypi/tasi/
.. |Developed by DLR-TS| image:: https://img.shields.io/badge/developed%20by-DLR%20TS-orange.svg?style=flat&colorA=E1523D&colorB=007D8A
   :target: https://www.dlr.de/en/ts/about-us/the-institute-of-transportation-systems
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14034644.svg
   :target: https://doi.org/10.5281/zenodo.14034644
.. |DLR TS| image:: _static/logos/DLR_TS_Logo_EN_schwarz.svg
    :target: https://www.dlr.de/en/ts/about-us/the-institute-of-transportation-systems

.. _TS: https://www.dlr.de/en/ts/about-us/the-institute-of-transportation-systems