from setuptools import setup
__version__ = '0.1'

import os

def mysetup(requires) :
   setup(name='ImportNURBS_Workbench',
      version=str(__version__),
      packages=['freecad','rhino3dm'],
      maintainer="keithsloan52",
      maintainer_email="keith@sloan-home.co.uk",
      url="https://github.com/KeithSloan/ImportNURBS",
      description="Workbench to add support for import of 3DM Files to FreeCAD",
      install_requires=[requires],
      include_package_data=True)

# Still not clear if under linux one can just install lxml with pip
# or sudo apt-get install python3-lxml

mysetup('rhino3dm')
#import os
#if 'posix' in os.name:
#    mysetup('lxml')
#
#else:
#    mysetup('python3-lxml')
