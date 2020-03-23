__title__ = "ImportNURBS"
__author__ = "Keith Sloan (KeithSloan52)"
__license__ = "LGPL 2.1"
__doc__ = "FreeCAD workbench to add importer of 3DM Files"

import FreeCAD
FreeCAD.addImportType("3DM (*.3dm)","freecad.importNURBS.import3DM")
