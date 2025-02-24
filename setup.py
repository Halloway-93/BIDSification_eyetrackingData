#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import BIDSification_eyetrackingData

setup(
    name='BIDSification_eyetrackingData',
    version=BIDSification_eyetrackingData.version__,
    packages=find_packages(),
    author="",
    author_email="",
    description="allows automatic arrangement of eye data in BIDS format",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='',
    classifiers=[
        "Programming Language :: Python",
    ],
)
