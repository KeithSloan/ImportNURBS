# **************************************************************************
# *                                                                        *
# *   Copyright (c) 2020 Keith Sloan <keith@sloan-home.co.uk>              *
# *                                                                        *
# *   This program is free software; you can redistribute it and/or modify *
# *   it under the terms of the GNU Lesser General Public License (LGPL)   *
# *   as published by the Free Software Foundation; either version 2 of    *
# *   the License, or (at your option) any later version.                  *
# *   for detail see the LICENCE text file.                                *
# *                                                                        *
# *   This program is distributed in the hope that it will be useful,      *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of       *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        *
# *   GNU Library General Public License for more details.                 *
# *                                                                        *
# *   You should have received a copy of the GNU Library General Public    *
# *   License along with this program; if not, write to the Free Software  *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 *
# *   USA                                                                  *
# *                                                                        *
# *   Acknowledgements :                                                   *
# *                                                                        *
# *                                                                        *
# **************************************************************************

import FreeCAD 
import os, io, sys
import FreeCADGui
import Part, Draft, math

# try:
#  import rhino3dm as r3
#
# except:
#  FreeCAD.Console.PrintError("You must install rhino3dm first !")
#  exit(0)

import rhino3dm as r3

if open.__module__ == "__builtin__":
    pythonopen = (
        open  # to distinguish python built-in open function from the one declared here
    )


def open(filename):
    "called when freecad opens a file."
    global doc
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith(".3dm"):
        process3DM(doc, filename)
    return doc


def insert(filename, docname):
    "called when freecad imports a file"
    global doc
    groupname = os.path.splitext(os.path.basename(filename))[0]
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith(".3dm"):
        process3DM(doc, filename)


def toFCvec(r3Dpnt):
    return FreeCAD.Vector(r3Dpnt.X, r3Dpnt.Y, r3Dpnt.Z)


def toFCangle(center, start):
    return math.atan((start.Y - center.Y) / (start.X - center.Y)) * math.pi / 180


class File3dm:
    def __init__(self, path):
        self.f3dm = r3.File3dm.Read(path)

    def parse_objects(self, doc=None):
        if not doc:
            doc = FreeCAD.newDocument("3dm import")
        part = doc.addObject("App::Part", "Part")
        for i in range(len(self.f3dm.Objects)):
            obj_fullname = "{}".format(self.f3dm.Objects[i].Geometry)
            first_split = obj_fullname.split(".")
            second_split = first_split[-1].split(" ")
            print("-----------------\n{}".format(second_split[0]))
            obj = self.import_geometry(doc, self.f3dm.Objects[i].Geometry)
            if obj:
                part.addObject(obj)

    def import_geometry(self, doc, geo):
        print("Geometry type")
        print(type(geo))

        if isinstance(geo, r3.Brep):  # str(geo.ObjectType) == "ObjectType.Brep":
            print("Brep object")
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
                # print("Face {} has {} edges".format(i,len(geo.Faces[i].Edges)))
            com = Part.Compound(shapes)
            obj = doc.addObject("Part::Feature", "Faces")
            obj.Shape = com
            # 	        	shapes = []
            # 			for i in range(len(geo.Edges)):
            # 				#print(geo.Faces[i])
            # 				c = self.create_curve(geo.Edges[i])
            # 				shapes.append(c.toShape())
            # 			com = Part.Compound(shapes)
            # 			obj = doc.addObject("Part::Feature","Edges")
            # 			obj.Shape = com
            return obj

        if isinstance(geo, r3.LineCurve):  # Must be before Curve
            print("Line Curve")
            # print(dir(geo))
            obj = doc.addObject("Part::Line", "Line Curve?")
            # print(dir(obj))
            obj.X1 = geo.PointAtStart.X
            obj.Y1 = geo.PointAtStart.Y
            obj.Z1 = geo.PointAtStart.Z
            obj.X2 = geo.PointAtEnd.X
            obj.Y2 = geo.PointAtEnd.Y
            obj.Z2 = geo.PointAtEnd.Z
            obj.recompute()
            return

        if isinstance(geo, r3.NurbsCurve):  # Must be before Curve
            print("NurbsCurve Object")
            # print(dir(geo))
            obj = doc.addObject("Part::Feature", "NurbsCurve")
            obj.Shape = self.create_curve(geo).toShape()
            return obj

        if isinstance(geo, r3.ArcCurve):
            print("Arc Curve Object")
            obj = doc.addObject("Part::Circle", "Arc")
            # print(type(geo.Arc.Center))
            obj.Placement.Base = toFCvec(geo.Arc.Center)
            obj.Radius = geo.Radius
            obj.Angle0 = startAngle = toFCangle(geo.Arc.Center, geo.PointAtStart)
            obj.Angle1 = startAngle + geo.Arc.AngleDegrees
            # print(dir(geo))
            obj.recompute()
            return obj

        if isinstance(geo, r3.BezierCurve):
            print("Bezier Curve Object")
            print(dir(geo))
            obj = doc.addObject("Part::Feature", "Bezier")
            obj.Shape = self.create_curve(geo).toShape()
            obj.recompute()
            return

        if isinstance(geo, r3.PolylineCurve):
            print("PolyLineCurve Object")
            print("Polgon Line?")
            # print(dir(geo))
            print("Is Polyline : " + str(geo.IsPolyline()))
            print("Point Count : " + str(geo.PointCount))
            # pl = geo.ToPolyline()
            # print(pl)
            # print(dir(pl))
            obj = doc.addObject("Part::Polygon", "PolyLine Curve?")
            # print(dir(obj))
            pList = []
            for i in range(geo.PointCount):
                p = geo.Point(i)
                # print(p.X)
                # print(p.Y)
                # print(p.Z)
                pList.append(FreeCAD.Vector(p.X, p.Y, p.Z))
            # print(pList)
            # obj.Shape = Part.makePolygon(pList)
            obj.Nodes = pList
            obj.recompute()
            return

        if isinstance(geo, r3.PolyCurve):
            print("PolyCurve Object")
            # self.printCurveInfo(geo)
            obj = doc.addObject("Part::Feature", "PolyCurve")
            obj.Shape = self.create_curve(geo).toShape()
            obj.recompute()
            # print(dir(geo))
            return

        if isinstance(geo, r3.Ellipse):
            print("Ellipse Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Bitmap):
            print("Bitmap Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Box):
            print("Box Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Circle):
            print("Circle Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Cone):
            print("Cone Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Curve):
            print("Curve object")
            self.printCurveInfo(geo)
            print(geo.ToNurbsCurve())
            # nc = geo.ToNurbsCurve()
            # print(nc)
            # print(dir(nc))
            # print(nc.Degree)
            cpc = geo.CreateControlPointCurve()
            print(dir(cpc))
            # obj = doc.addObject("Part::Feature","Curve")
            # obj.Shape = Part.makeself.create_curve(geo).toShape()
            # print(inspect.getargspec(nc.CreateControlPointCurve))
            # print(dir(nc.CreateControlPointCurve))
            return

        if isinstance(geo, r3.Cylinder):
            print("Cylinder Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Extrusion):
           print("Extrusion")
           print(dir(geo))
           print('Is Cylinder : '+str(geo.IsCylinder()))
           print(geo.NormalAt)
           print(geo.PathStart)
           print(geo.PathEnd)
           print(geo.PathTangent)
           print(geo.PointAt)
           print(geo.GetPathPlane)
           print('Profile Count : '+str(geo.ProfileCount))
           # Create Part ToShape from profile
           # Create new Shape from Extrude of ToShape
           # Create Part::PythonFeature & Return
           height = geo.PathStart.Z - geo.PathEnd.Z
           print(f'Height : {height}')
           for i in range(geo.ProfileCount) :
               print(i)
               c = geo.Profile3d(i,0.0)
               print(f'Object type : {c.ObjectType}')
               print(c)
               print(c.ObjectType)
               if isinstance(c, r3.Curve):
                  self.printCurveInfo(c)
               # Need to create FreeCAD TopoShape depending on type
               print('Tests')
               if c.IsArc() == True :
                  print('Arc')
                  print('Not yet Handled')
               elif c.IsCircle() == True :
                  print('Circle')
                  print(c.Radius)
                  print('Not yet Handled')
               elif c.IsEllipse() == True :
                  print('Ellipse')
                  print('Not yet Handled')
               elif c.IsPolyline() == True :
                  # Call ToLine and create FreeCAD TopoShape from Line
                  print('Polyline')
                  print(dir(c))
                  l = c.ToPolyline()
                  print(dir(l))
                  print(l.SegmentCount)
                  points = []
                  for i in range(0,l.SegmentCount):
                      print(l.PointAt(i))
                      print(dir(l.PointAt(i)))
                      p = l.PointAt(i)
                      points.append((p.X, p.Y, p.Z))
                  points.append(points[0])
                  #wire = Draft.make_wire(points, closed=True, placement=None, \
                  #       face=True, support=None)
                  
                  obj = doc.addObject("Part::FeaturePython","Extrusion")
                  poly = Part.makePolygon(points)
                  obj.Shape = poly
                  #face = Part.Face(Part.Wire(poly))
                  #obj.Shape = face.extrude(FreeCAD.Vector(0.0, 0.0, height))
                  return
             
             
           print(geo.Profile3d)
           if geo.IsCylinder() == True :
              height = geo.PathStart.Z - geo.PathEnd.Z
              print('Height : '+str(height))
              c = geo.Profile3d(0,0.0)
              radius = c.Radius
              print('Radius : '+str(radius))
              obj = doc.addObject("Part::Cylinder","Extruded Cylinder")
              obj.Height = height
              obj.Radius = radius
              obj.recompute()
           #print(dir(geo))
           return

        if isinstance(geo, r3.Mesh):
            print("Mesh Object")
            return self.create_mesh(doc, geo)

        if isinstance(geo, r3.NurbsSurface):
            print("NurbsSurface Object")
            print(dir(geo))
            return self.create_surface(geo)

        if isinstance(geo, r3.PointCloud):
            print("PointCloud Object")
            print(dir(geo))
            return

        if isinstance(geo, r3.Surface):
            print("Surface Object")
            print(geo.IsCylinder)
            print(geo.IsSolid)
            print(dir(geo))
            return

        print("Not yet handled")
        print(dir(geo))

    def printCurveInfo(self, geo):
        print("Curve Info")
        print(dir(geo))
        print('IsArc     : ',geo.IsArc())
        print('IsCircle  : ',geo.IsCircle())
        print('IsEllipse : ',geo.IsEllipse())
        print('IsPolyline : ',geo.IsPolyline())
        print(geo.CurvatureAt)
        print(dir(geo.CurvatureAt))
        if hasattr(geo,'SegmentCount') :
           print(geo.SegmentCount)
           print(geo.SegmentCurve)
           print(dir(geo.SegmentCurve))
           print(geo.SegmentCurveParameter)
           print(dir(geo.SegmentCurveParameter))
           print(geo.SegmentIndex)
           print(dir(geo.SegmentIndex))
        #cpc = geo.CreateControlPointCurve()
        #print(dir(cpc))
        nc = geo.ToNurbsCurve()
        print(dir(nc))

    def create_curve(self, edge):
        nc = edge.ToNurbsCurve()
        # print("{} x {}".format(nu.Degree(0), nu.Degree(1)))
        pts = []
        weights = []
        for u in range(len(nc.Points)):
            p = nc.Points[u]
            # print(FreeCAD.Vector(p.X,p.Y,p.Z))
            pts.append(FreeCAD.Vector(p.X / p.W, p.Y / p.W, p.Z / p.W))
            weights.append(p.W)
        ku, mu = self.getFCKnots(nc.Knots)
        periodic = False  # mu[0] <= nu.Degree(0)
        bs = Part.BSplineCurve()
        bs.buildFromPolesMultsKnots(pts, mu, ku, periodic, nc.Degree, weights)
        if mu[0] < (nc.Degree + 1):
            bs.setPeriodic()
        return bs

    def create_surface(self, surf):
        nu = surf.ToNurbsSurface()
        print("{} x {}".format(nu.Degree(0), nu.Degree(1)))
        pts = []
        weights = []
        print("Control Points")
        print("CountU : " + str(nu.Points.CountU))
        print("CountV : " + str(nu.Points.CountV))
        for u in range(nu.Points.CountU):
            row = []
            wrow = []
            for v in range(nu.Points.CountV):
                p = nu.Points[u, v]
                print(FreeCAD.Vector(p.X, p.Y, p.Z))
                row.append(FreeCAD.Vector(p.X / p.W, p.Y / p.W, p.Z / p.W))
                wrow.append(p.W)
            pts.append(row)
            weights.append(wrow)
        print("Knots")
        ku, mu = self.getFCKnots(nu.KnotsU)
        kv, mv = self.getFCKnots(nu.KnotsV)
        uperiodic = False  # mu[0] <= nu.Degree(0)
        vperiodic = False  # mv[0] <= nu.Degree(1)
        print(list(nu.KnotsU))
        print("ku mu")
        print(ku, mu)
        print("kv mv")
        print(kv, mv)
        print("Flat knots")
        vflatknots = list(nu.KnotsV)
        print("{}\n{}".format(vflatknots, vflatknots))
        bs = Part.BSplineSurface()
        bs.buildFromPolesMultsKnots(
            pts,
            mu,
            mv,
            ku,
            kv,
            uperiodic,
            vperiodic,
            nu.Degree(0),
            nu.Degree(1),
            weights,
        )
        if mu[0] < (nu.Degree(0) + 1):
            bs.setUPeriodic()
        if mv[0] < (nu.Degree(1) + 1):
            bs.setVPeriodic()
        return bs

    def getFCKnots(self, fknots):
        k = list(fknots)
        mults = []
        knots = list(set(k))
        knots.sort()
        for kn in knots:
            mults.append(k.count(kn))
        mults[0] += 1
        mults[-1] += 1
        return knots, mults

    def create_mesh(self, doc, r3mesh):
        # Return Object Mesh
        import Mesh

        fcMesh = Mesh.Mesh()
        obj = doc.addObject("Mesh::Feature")
        obj.Mesh = Mesh.Mesh()
        print("Quad Count : " + str(r3mesh.Faces.QuadCount))
        print("Triangle Count : " + str(r3mesh.Faces.TriangleCount))
        # FreeCAD only supports Triangles
        print(r3mesh.Faces.ConvertQuadsToTriangles())
        print(len(r3mesh.Faces))
        print("Count : " + str(r3mesh.Faces.Count))
        print("Quad Count : " + str(r3mesh.Faces.QuadCount))
        print("Vertices Count : " + str(len(r3mesh.Vertices)))
        # print(type(r3mesh.Faces))
        for m in range(r3mesh.Faces.TriangleCount):
            # print('Face')
            mf = r3mesh.Faces[m]
            # print(type(mf))
            # print(dir(mf))
            fval = ()
            # 3dm files always have 4 vertex values even for triangles
            for r in range(0, 3):
                f = mf[r]
                # print('X : '+str(r3mesh.Vertices[f].X)+ \
                #     ' Y : '+str(r3mesh.Vertices[f].Y)+ \
                #     ' Z : '+str(r3mesh.Vertices[f].Z))
                fval = fval + (
                    float(r3mesh.Vertices[f].X),
                    float(r3mesh.Vertices[f].Y),
                    float(r3mesh.Vertices[f].Z),
                )
            fcMesh.addFacet(*fval)
        obj.Mesh = fcMesh


def process3DM(doc, filename):
    FreeCAD.Console.PrintMessage("Import 3DM file : " + filename + "\n")
    FreeCAD.Console.PrintMessage("Import3DM Version 0.01\n")

    att = [
        "ApplicationName",
        "ApplicationUrl",
        "ApplicationDetails",
        "CreatedBy",
        "LastEditedBy",
        "Revision",
    ]

    fi = File3dm(filename)
    fi.parse_objects(doc)
    FreeCADGui.SendMsgToActiveView("ViewFit")

    # pathName = os.path.dirname(os.path.normpath(filename))

    FreeCAD.Console.PrintMessage("3DM File Imported\n")
