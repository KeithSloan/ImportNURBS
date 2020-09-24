# ImportNURBS

  Add Import of 3DM files to FreeCAD
  
# Requirements 

* rhino3dm - Open Python Rhino 3dm library - Which seems to require Python 3.7 
  
# Installation - Add on Manager

 * The workbench is available via the FreeCAD AddonManager
 * However users may have to install rhino3dm depending on OS.
 * One suggestion
     - Start FreeCAD
     - In python console
        - import sys
        - print(sys.path)
         
     - Select one the the directories listed
     
       pip3 install rhino3dm -t [directory path]
     
     - restart FreeCAD

# Alternate Installation ( Linux )

 * sudo apt install python3-pip
 * pip3 install --user rhino3dm
 * Change directory to .FreeCAD/Mod   
   i.e. with a dot
 * git clone  https://github.com/KeithSloan/ImportNURBS.git
 * start or restart FreeCAD
 
# Sample Rhino files

  Can be downloaded from https://www.rhino3d.com/download/opennurbs/6/opennurbs6samples 

# Acknowledgements

  * Icon design by Freepik

# Developers 
  
 * Chris Grellier
 * Keith Sloan
  
