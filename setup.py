'''
	Python library for using the ADC expansion board from ABElectronics UK
'''

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(name = 'ADCPi',
	version = '0.0.1',
	description = "Simple python library for raspberry pi interaction with the ADC expansion board.",
	url = 'https://github.com/dhhagan/ADCPi',
	author = 'David H Hagan',
	author_email = 'david@davidhhagan.com',
	license = 'MIT',
	keywords = ['ADC', 'ABElectronics'],
	packages = ['ADCPi'],
	zip_safe = False)