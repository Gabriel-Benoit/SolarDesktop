from setuptools import setup, find_packages
import os
requirementPath = os.path.dirname(
    os.path.realpath(__file__)) + '/requirements.txt'
requirements = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        requirements = f.read().splitlines()


setup(name='solar_gui', version='1.0', packages=find_packages(),
      install_requires=requirements)
