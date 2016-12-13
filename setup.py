# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='wordpress_converter',
    version='0.0.1',
    description='A tool to convert a Wordpress.com export file into a Flask app.',
    long_description=readme,
    author='Ben Hoyle',
    author_email='benjhoyle@gmail.com',
    url='https://github.com/benhoyle/wordpress_converter',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
    #packages=['patentdata']
)