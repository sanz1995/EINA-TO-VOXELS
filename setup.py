# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='EINA-TO-VOXELS',
    version='0.1.0',
    description='Package for minecraft worlds creation',
    long_description=readme,
    author='Jorge Sanz',
    author_email='jorge.sanz.alcaine@gmail.com',
    url='https://github.com/sanz1995/EINA-TO-VOXELS',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)