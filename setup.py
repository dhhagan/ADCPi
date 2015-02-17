'''
	Python library for using the Delta Sigma ADC expansion board from ABElectronics UK
	This entire library is adapted from ABElectronics UK.
	Adapted by David H Hagan. February 2015. e: david@davidhhagan.com
'''

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name = 'ADCPi',
	version = '0.1.1',
	description = "Simple python library for raspberry pi interaction with the Delta Sigma ADC expansion board.",
	url = 'https://github.com/dhhagan/ADCPi',
	author = 'David H Hagan',
	author_email = 'david@davidhhagan.com',
	license = 'MIT',
	keywords = ['ADC', 'ABElectronics', 'Delta Sigma'],
	packages = ['ADCPi'],
	zip_safe = False)