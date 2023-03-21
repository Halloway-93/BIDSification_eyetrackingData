BIDSification Data
=============================

This python package allows you to automatically organize your eye data in a BIDS format.

To install this package, please use the following command:

``pip install git+https://github.com/chloepasturel/BIDSification_eyetrackingData.git``

For more details, we recommend that you consult the BIDS documentation specific to Eye-Tracking.

The BIDSifier data looks like this:

| **dataset/**
|    **participants.tsv**
|    **sub-** ``<label>`` **/**
|       *[ ses-* ``<label>`` */ ]*
|          ``<datatype>`` **/**
|             |sub| |ses| |task| |acq| |run| **_eyetrack.** ``<datatype>``
|             |sub| |ses| |task| |acq| |run| **_eyetrack.json**
|             |sub| |ses| |task| |acq| |run| **_eyetrack.tsv**
|             |sub| |ses| |task| |acq| |run| **_events.json**
|             |sub| |ses| |task| |acq| |run| **_events.tsv**

.. |sub| replace:: **sub-** ``<label>``
.. |ses| replace:: *[* *_ses-* ``<label>`` *]*
.. |task| replace:: *[* *_task-* ``<label>`` *]*
.. |acq| replace:: *[* *_acq-* ``<label>`` *]*
.. |run| replace:: *[* *_run-* ``<index>`` *]*


To do this you will need to add two important files to your non-range raw data folder:

- :doc:`1_InfoFile` - containing information about the data files in the directory

- :doc:`2_SettingsFile` - containing the general settings for the task

you can then BIDify your data (see :doc:`3_BIDSification`)


.. toctree::
   :hidden:
   
   1_InfoFile
   2_SettingsFile
   3_BIDSification
   
   
