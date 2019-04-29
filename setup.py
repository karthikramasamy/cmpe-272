#!/usr/bin/env python

from distutils.core import setup
from glob import glob

from setuptools import find_packages

setup(name='bookstore',
      version='1.0',
      description='Python Distribution Utilities',
      author='Karthik Ramasamy',
      packages=find_packages('bookstore'),
      package_dir={'': 'bookstore'},
      py_modules=[splitext(basename(path))[0] for path in glob('bookstore/*.py')],
     )