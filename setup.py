"""
Hello World app for running Python apps on Bluemix
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vvs-delay-dataset',
    version='1.0.0',
    description='VVS is a public transport organization located in and around Stuttgart, Germany. We are trying to create a dataset which contains data about delays that appeared over time. Furthermore a neural network shall be trained to predict delays.',
    long_description=long_description,
    url='https://github.com/jhertfe/vvs-delay',
    license='MIT'
)
