#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="pycnc",
    version="0.1",
    packages=find_packages(),
    scripts=['pycnc'],

    # metadata for upload to PyPI
    author="Nikolay Khabarov",
    author_email="2xl@mail.ru",
    description="CNC machine controller",
    license="MIT",
    keywords="CNC 3D printer robot raspberry pi",
    url="https://github.com/Nikolay-Kha/PyCNC",
)