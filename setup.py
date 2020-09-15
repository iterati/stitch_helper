#!/usr/bin/env python3

import glob
import os

from setuptools import setup, find_packages

setup(
    name="stitch-helper",
    version="0.0.1",
    description="Stitch Helper",
    author="John Miller",
    py_modules=["stitch_helper"],
    install_requires=[
        "boto3==1.11.7",
        "libtmux==0.8.1",
    ],
    packages=["stitch_helper"],
    entry_points="""
    [console_scripts]
    sd=stitch_helper:main
    """,
)
