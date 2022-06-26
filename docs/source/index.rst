.. Home + Control documentation master file, created by
   sphinx-quickstart on Fri Dec  4 17:50:56 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _index:

Documentation of Home + Control by Legrand
==========================================

**Legrand has deprecated the Legrand Home + Control API and migrated to the Netatmo Connect platform. This library has been updated to support the new Netatmo Connect API.**

This is a basic Python library that interacts with the *Netatmo Connect Home + Control* API. It is 
primarily intended for integration into Smart Home platforms such as Home Assistant.

More information of the API can be found here: https://dev.netatmo.com/apidocumentation/control

The library currently supports 4 types of Legrand (not Smarther) modules:

1) Plugs (power outlets)
2) Lights (connected switches)
3) Remotes (wireless switches)
4) Automations (shutters/covers) [of the iDiamant/Bubbendorf product line]

The first two - plugs and lights - are modeled as basic switches that can be interacted with to set their status to *on* or *off*.

Remotes are presented as passive modules that only have a battery level attribute.

Automations can be issued commands to open or close to their full positions and to be stopped during the motion.

A 'home' is represented by a *plant* which presents all of its corresponding modules in a topology. A *plant* is basically a Home+ Control gateway.

The status of each module in the *plant* can be accessed through a single *status* call to the *plant* or through individual *status* calls to each module.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   authentication
   quickstart
   testing
   api
   
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

