__title__ = "import3DM"
__author__ = "Keith Sloan (keithsloan52) : Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "import of 3DM file"

import FreeCAD 
import os, io, sys
import FreeCADGui 
import Part

try:
    import rhino3dm as r3

except ModuleNotFoundError:
    FreeCAD.Console.PrintError("You must install rhino3dm first !")
    exit()

#print(dir(r3))

if open.__module__ == '__builtin__':
    pythonopen = open # to distinguish python built-in open function from the one declared here

def open(filename):
    "called when freecad opens a file."
    global doc
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith('.3dm'):
        process3DM(doc,filename)
    return doc

def insert(filename,docname):
    "called when freecad imports a file"
    global doc
    groupname = os.path.splitext(os.path.basename(filename))[0]
    try:
        doc=FreeCAD.getDocument(docname)
    except NameError:
        doc=FreeCAD.newDocument(docname)
    if filename.lower().endswith('.3dm'):
        process3DM(doc,filename)

class File3dm:

    def __init__(self, path):
        self.f3dm = r3.File3dm.Read(path)

    def parse_objects(self, doc=None):
        if not doc:
            doc = FreeCAD.newDocument("3dm import")
        part = doc.addObject('App::Part','Part')
        for i in range(len(self.f3dm.Objects)):
            obj_fullname = "{}".format(self.f3dm.Objects[i].Geometry)
            first_split = obj_fullname.split(".")
            second_split = first_split[-1].split(" ")
            print("-----------------\n{}".format(second_split[0]))
            obj = self.import_geometry(doc, self.f3dm.Objects[i].Geometry)
            if obj:
               part.addObject(obj)

    def import_geometry(self, doc, geo):
        print('Geometry type')
        print(type(geo))

        if isinstance(geo, r3.Brep): #str(geo.ObjectType) == "ObjectType.Brep":
            #print("Brep object")
            print("is solid : {}".format(geo.IsSolid))
            print("is manifold : {}".format(geo.IsManifold))
            print("is surface : {}".format(geo.IsSurface))
            print("has {} faces".format(len(geo.Faces)))
            print("has {} surfaces".format(len(geo.Surfaces)))
            print("has {} edges".format(len(geo.Edges)))
            shapes = []
            for i in range(len(geo.Faces)):
                print(geo.Faces[i])
                s = self.create_surface(geo.Faces[i])
                print(s)
                shapes.append(s.toShape())
                #print("Face {} has {} edges".format(i,len(geo.Faces[i].Edges)))
            com = Part.Compound(shapes)
            obj = doc.addObject("Part::Feature","Faces")
            obj.Shape = com
#	        	shapes = []
#			for i in range(len(geo.Edges)):
#				#print(geo.Faces[i])
#				c = self.create_curve(geo.Edges[i])
#				shapes.append(c.toShape())
#			com = Part.Compound(shapes)
#			obj = doc.addObject("Part::Feature","Edges")
#			obj.Shape = com
            return obj
        if isinstance(geo, r3.BezierCurve):
            print("Bezier Curve Object")

        if isinstance(geo, r3.Bitmap):
            print("Bitmap Object")

        if isinstance(geo, r3.Box):
            print("Box Object")

        if isinstance(geo, r3.Circle):
            print("Circle Object")

        if isinstance(geo, r3.Cone):
            print("Cone Object")

        if isinstance(geo, r3.Curve):
            print("Curve Object")

        if isinstance(geo, r3.Cylinder):
            print("Cylinder Object")

        if isinstance(geo, r3.Ellipse):
            print("Ellipse Object")

        if isinstance(geo, r3.Mesh):
            print("Mesh Object")

        if isinstance(geo, r3.NurbsSurface):
            print("NurbsSurface Object")

        if isinstance(geo, r3.PointCloud):
            print("PointCloud Object")

        if isinstance(geo, r3.Surface):
            print("Surface Object")


    def create_curve(self, edge):
        nc = edge.ToNurbsCurve()
        #print("{} x {}".format(nu.Degree(0), nu.Degree(1)))
        pts = []
        weights = []
        for u in range(len(nc.Points)):
            p = nc.Points[u]
            #print(FreeCAD.Vector(p.X,p.Y,p.Z))
            pts.append(FreeCAD.Vector(p.X,p.Y,p.Z))
            weights.append(p.W)
        ku, mu = self.getFCKnots(nc.Knots)
        periodic = False #mu[0] <= nu.Degree(0)
        bs = Part.BSplineCurve()
        bs.buildFromPolesMultsKnots(pts, mu, ku, periodic, \
            nc.Degree, weights)
        if mu[0] < (nc.Degree+1):
            bs.setPeriodic()
            return bs

    def create_surface(self, surf):
        nu = surf.ToNurbsSurface()
        #print("{} x {}".format(nu.Degree(0), nu.Degree(1)))
        pts = []
        weights = []
        for u in range(nu.Points.CountU):
            row = []
            wrow = []
            for v in range(nu.Points.CountV):
                p = nu.Points[u,v]
                #print(FreeCAD.Vector(p.X,p.Y,p.Z))
                row.append(FreeCAD.Vector(p.X,p.Y,p.Z))
                wrow.append(p.W)
            pts.append(row)
            weights.append(wrow)
        ku, mu = self.getFCKnots(nu.KnotsU)
        kv, mv = self.getFCKnots(nu.KnotsV)
        uperiodic = False #mu[0] <= nu.Degree(0)
        vperiodic = False #mv[0] <= nu.Degree(1)
#		print(list(nu.KnotsU))
#		print(ku, mu)
#		print(kv, mv)
#		vflatknots = list(nu.KnotsV)
#		print("{}\n{}".format(uflatknots, vflatknots))
        bs = Part.BSplineSurface()
        bs.buildFromPolesMultsKnots(pts, mu, mv, ku, kv, \
                uperiodic, vperiodic, nu.Degree(0), nu.Degree(1), weights)
        if mu[0] < (nu.Degree(0)+1):
            bs.setUPeriodic()
        if mv[0] < (nu.Degree(1)+1):
            bs.setVPeriodic()
        return bs

    def getFCKnots(self,fknots):
        k = list(fknots)
        mults = []
        knots = list(set(k))
        knots.sort()
        for kn in knots:
            mults.append(k.count(kn))
        mults[0] += 1
        mults[-1] += 1
        return knots, mults

def process3DM(doc, filename) :
    FreeCAD.Console.PrintMessage('Import 3DM file : '+filename+'\n')
    FreeCAD.Console.PrintMessage('Import3DM Version 0.01\n')

    att = ["ApplicationName",
        "ApplicationUrl",
        "ApplicationDetails",
        "CreatedBy",
        "LastEditedBy",
        "Revision"]

    fi = File3dm(filename)
    fi.parse_objects(doc)
    FreeCADGui.SendMsgToActiveView("ViewFit")

    #pathName = os.path.dirname(os.path.normpath(filename))

    FreeCAD.Console.PrintMessage('3DM File Imported\n')

