#!/usr/bin/env python3
"""Installation script."""

import os
import sys

from setuptools import setup

sys.path.append(os.path.dirname(__file__))

import versioneer

setup(
    name="tasi",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)