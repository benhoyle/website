# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='website',
    version='0.0.1',
    description='My website.',
    long_description=readme,
    author='Ben Hoyle',
    author_email='benjhoyle@gmail.com',
    url='https://github.com/benhoyle/website',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
    #packages=['patentdata']
)