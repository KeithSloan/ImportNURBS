
##
## Being replaced by ImportExport_3DM which adds export
## https://github.com/KeithSloan/ImportExport_3DM
##

# ImportNURBS

  Add Import of 3DM files to FreeCAD

##########################################################
# Some coded added lots more to do.                      #
# Please report any problems as Issues - Thanks          #
##########################################################
  
# Requirements 

* rhino3dm - Open Python Rhino 3dm library 

You need to use the same version and level of Python that FreeCAD is using to
install rhino3dm. 

You can find out the version FreeCAD is using by using
 
    FreeCAD | About freecad | Libraries 
or
    Looking at the heading in FreeCAD python console   

# Installing for FreeCAD 1.1 on MacOS

* FreeCAD 1.1 on Mac uses Python 3.11

```bash
python3.11 -m pip install rhino3dm --no-cache -t '/Applications/FreeCAD_1.1.app/Contents/Resources/lib/python3.11/site-packages'
```

# Installing for FreeCAD 1.0.0 on MacOS

* FreeCAD 1.0.0 on Mac uses Python 3.11

```bash
python3.11 -m pip install rhino3dm --no-cache -t '/Applications/FreeCAD 1.0.0.app/Contents/Resources/lib/python3.11/site-packages'
```

# Installation - Add on Manager

 * The workbench is available via the FreeCAD AddonManager
 * However users may have to install rhino3dm depending on OS.
 * One suggestion
     - Start FreeCAD
     - In python console
        - import sys
        - print(sys.path)
         
     - Select one of the directories listed and run:
     
       python3.11 -m pip install rhino3dm --no-cache -t [directory path]
     
     - restart FreeCAD

# Alternate Installation ( Linux )

 * sudo apt install python3-pip
 * pip3 install --user rhino3dm
 * Change directory to .FreeCAD/Mod   
   i.e. with a dot
 * git clone  https://github.com/KeithSloan/ImportNURBS.git
 * start or restart FreeCAD

# Blender NURBS Export Pipeline

A companion Blender extension for exporting NURBS surfaces directly to 3DM
is available at https://github.com/KeithSloan/Blender_Export_3DM

This enables a lossless Blender → 3DM → FreeCAD NURBS pipeline without
tessellation.

## What's detected on import

The importer reports geometry type diagnostics in the Report View:

- **NurbsSurface** — degree, CV count, rational flag, knot counts
- **SubD** — topology probe (flags if NURBS was not preserved by exporter)
- **Mesh** — quad/triangle/vertex counts (flags if NURBS was not preserved)

# Sample Rhino files

  Can be downloaded from https://www.rhino3d.com/download/opennurbs/6/opennurbs6samples 

# Acknowledgements

  * Icon design by Freepik
  * 3dm testCases kindly supplied by Jonne Neva (cheezebreeze)

# Developers 
  
 * Chris Grellier
 * Keith Sloan
