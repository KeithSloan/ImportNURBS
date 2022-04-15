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
    """Import as new file."""
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith(".3dm"):
        process3DM(doc, filename)
    return doc


def insert(filename, docname):
    """Insert import into open document."""
    # groupname = os.path.splitext(os.path.basename(filename))[0]
    try:
        doc = FreeCAD.getDocument(docname)
    except NameError:
        doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith(".3dm"):
        process3DM(doc, filename)


def toFCvec(r3Dpnt):
    """Convert to FreeCAD Vector."""
    return FreeCAD.Vector(r3Dpnt.X, r3Dpnt.Y, r3Dpnt.Z)


def toFCangle(center, start):
    """Convert to FreeCAD Angle."""
    return math.atan((start.Y - center.Y) / (start.X - center.Y)) * math.pi / 180


class File3dm:
    """Main 3dm to FreeCAD converter."""

    def __init__(self, path, debug_level=1):
        """Init."""
        self.debug_level = debug_level
        self.path = path
        self.filename = os.path.basename(path)
        self.f3dm = r3.File3dm.Read(path)

    def log_l0(self, *args, **kwargs):
        """Log with level0."""
        if self.debug_level >= 0:
            print(*args, *kwargs)

    def log_l1(self, *args, **kwargs):
        """Log with level1."""
        if self.debug_level >= 1:
            print(*args, *kwargs)

    def log_l2(self, *args, **kwargs):
        """Log with level2."""
        if self.debug_level >= 2:
            print(*args, *kwargs)

    @staticmethod
    def print_class_attributes(obj, print_fn=print):
        """Print a list of all class attributes and ther values."""
        obj_attr_names = [a for a in dir(obj) if not a.startswith("__")]
        attr_name_length_max = len(max(obj_attr_names, key=len))
        attr_name_format = " {:>" + str(attr_name_length_max) + "} "
        for attr_name in obj_attr_names:
            value = getattr(obj, attr_name)
            if callable(value):
                try:
                    value = value()
                except Exception as e:
                    value = str(e)[:60] + " ..."
            print_fn(attr_name_format.format(attr_name), value)

    @staticmethod
    def get_obj_name(obj):
        """Get object name as string."""
        if obj and hasattr(obj, "Attributes"):
            obj_name = obj.Attributes.Name
        if not obj_name:
            obj_name = obj.Geometry.ObjectType.name
        return obj_name

    def print_curve_info(self, geo):
        """Print some Cuve Info."""
        self.log_l1("Curve Info")
        self.log_l1(dir(geo))
        self.log_l1("IsArc     : ", geo.IsArc())
        self.log_l1("IsCircle  : ", geo.IsCircle())
        self.log_l1("IsEllipse : ", geo.IsEllipse())
        self.log_l1(geo.CurvatureAt)
        self.log_l1(dir(geo.CurvatureAt))
        self.log_l1(geo.SegmentCount)
        self.log_l1(geo.SegmentCurve)
        self.log_l1(dir(geo.SegmentCurve))
        self.log_l1(geo.SegmentCurveParameter)
        self.log_l1(dir(geo.SegmentCurveParameter))
        self.log_l1(geo.SegmentIndex)
        self.log_l1(dir(geo.SegmentIndex))
        # cpc = geo.CreateControlPointCurve()
        # self.log_l2(dir(cpc))
        nurbs_curve = geo.ToNurbsCurve()
        self.log_l1(dir(nurbs_curve))

    # main import functions
    def parse_objects(self, doc=None):
        """Parse & load all Objects from self.f3dm."""
        if not doc:
            doc = FreeCAD.newDocument("3dm import")
        part = doc.addObject("App::Part", name=self.filename)
        # change to *Tree-Based* Group-Import or something similar. ?!?
        # https://mcneel.github.io/rhino3dm/python/api/File3dm.html
        # use f3dm.Groups?!
        for i in range(len(self.f3dm.Objects)):
            obj = self.f3dm.Objects[i]
            freecad_obj = self.import_object(doc, obj)
            self.log_l2("freecad_obj", freecad_obj)
            if freecad_obj:
                part.addObject(freecad_obj)
            self.log_l0()

    def import_object(self, doc, obj):
        """Import geometry and convert to FreeCAD object"""
        geo = obj.Geometry
        obj_name = File3dm.get_obj_name(obj)
        obj_type = obj.Geometry.ObjectType.name
        self.log_l0(
            "-----------------\n"
            "import_object: \n"
            " type: '{}' \n"
            " name: '{}' \n"
            "".format(obj_type, obj_name)
        )

        self.log_l2(" type", type(geo))
        self.log_l2("obj.Attributes:")
        File3dm.print_class_attributes(obj.Attributes, self.log_l2)
        self.log_l2("obj.Geometry:")
        File3dm.print_class_attributes(obj.Geometry, self.log_l2)

        # str(geo.ObjectType) == "ObjectType.Brep":
        if isinstance(geo, r3.Brep):
            self.log_l0("Brep object")
            self.log_l1("is solid : {}".format(geo.IsSolid))
            self.log_l1("is manifold : {}".format(geo.IsManifold))
            self.log_l1("is surface : {}".format(geo.IsSurface))
            self.log_l1("has {} faces".format(len(geo.Faces)))
            self.log_l1("has {} surfaces".format(len(geo.Surfaces)))
            self.log_l1("has {} edges".format(len(geo.Edges)))
            shapes = []
            for i in range(len(geo.Faces)):
                self.log_l1(geo.Faces[i])
                surface = self.create_surface(geo.Faces[i])
                self.log_l1(surface)
                shapes.append(surface.toShape())
                # self.log_l2("Face {} has {} edges".format(i, len(geo.Faces[i].Edges)))
            com = Part.Compound(shapes)
            obj = doc.addObject("Part::Feature", name=obj_name)
            obj.Label2 = "{} Faces".format(obj_type)
            obj.Shape = com
            # 	        	shapes = []
            # 			for i in range(len(geo.Edges)):
            # 				#log_l2geo.Faces[i])
            # 				c = self.create_curve(geo.Edges[i])
            # 				shapes.append(c.toShape())
            # 			com = Part.Compound(shapes)
            # 			obj = doc.addObject("Part::Feature","Edges")
            # 			obj.Shape = com
            return obj

        if isinstance(geo, r3.LineCurve):  # Must be before Curve
            self.log_l0("Line Curve")
            # log_l2(dir(geo))
            obj = doc.addObject("Part::Line", "Line Curve?")
            # log_l2(dir(obj))
            obj.X1 = geo.PointAtStart.X
            obj.Y1 = geo.PointAtStart.Y
            obj.Z1 = geo.PointAtStart.Z
            obj.X2 = geo.PointAtEnd.X
            obj.Y2 = geo.PointAtEnd.Y
            obj.Z2 = geo.PointAtEnd.Z
            obj.recompute()
            return

        if isinstance(geo, r3.NurbsCurve):  # Must be before Curve
            self.log_l0("NurbsCurve Object")
            # log_l2(dir(geo))
            obj = doc.addObject("Part::Feature", "NurbsCurve")
            obj.Shape = self.create_curve(geo).toShape()
            return obj

        if isinstance(geo, r3.ArcCurve):
            self.log_l0("Arc Curve Object")
            obj = doc.addObject("Part::Circle", "Arc")
            # log_l2type(geo.Arc.Center))
            obj.Placement.Base = toFCvec(geo.Arc.Center)
            obj.Radius = geo.Radius
            obj.Angle0 = startAngle = toFCangle(geo.Arc.Center, geo.PointAtStart)
            obj.Angle1 = startAngle + geo.Arc.AngleDegrees
            # log_l2(dir(geo))
            obj.recompute()
            return obj

        if isinstance(geo, r3.BezierCurve):
            self.log_l0("Bezier Curve Object")
            self.log_l1(dir(geo))
            obj = doc.addObject("Part::Feature", "Bezier")
            obj.Shape = self.create_curve(geo).toShape()
            obj.recompute()
            return

        if isinstance(geo, r3.PolylineCurve):
            self.log_l0("PolyLineCurve Object")
            self.log_l2("Polgon Line?")
            # self.log_l2(dir(geo))
            self.log_l2("Is Polyline : " + str(geo.IsPolyline()))
            self.log_l2("Point Count : " + str(geo.PointCount))
            # pl = geo.ToPolyline()
            # self.log_l2(pl)
            # self.log_l2(dir(pl))
            obj = doc.addObject("Part::Polygon", "PolyLine Curve?")
            # self.log_l2(dir(obj))
            pList = []
            for i in range(geo.PointCount):
                p = geo.Point(i)
                # self.log_l2(p.X)
                # self.log_l2(p.Y)
                # self.log_l2(p.Z)
                pList.append(FreeCAD.Vector(p.X, p.Y, p.Z))
            # self.log_l2(pList)
            # obj.Shape = Part.makePolygon(pList)
            obj.Nodes = pList
            obj.recompute()
            return

        if isinstance(geo, r3.PolyCurve):
            self.log_l0("PolyCurve Object")
            # self.print_curve_info(geo)
            obj = doc.addObject("Part::Feature", "PolyCurve")
            obj.Shape = self.create_curve(geo).toShape()
            obj.recompute()
            # log_l2(dir(geo))
            return

        if isinstance(geo, r3.Ellipse):
            self.log_l0("Ellipse Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Bitmap):
            self.log_l0("Bitmap Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Box):
            self.log_l0("Box Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Circle):
            self.log_l0("Circle Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Cone):
            self.log_l0("Cone Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Curve):
            self.log_l0("Curve object")
            self.print_curve_info(geo)
            self.log_l1(geo.ToNurbsCurve())
            # nc = geo.ToNurbsCurve()
            # self.log_l1(nc)
            # self.log_l1(dir(nc))
            # self.log_l1(nc.Degree)
            cpc = geo.CreateControlPointCurve()
            self.log_l1(dir(cpc))
            # obj = doc.addObject("Part::Feature","Curve")
            # obj.Shape = Part.makeself.create_curve(geo).toShape()
            # self.log_l1(inspect.getargspec(nc.CreateControlPointCurve))
            # self.log_l1(dir(nc.CreateControlPointCurve))
            return

        if isinstance(geo, r3.Cylinder):
            self.log_l0("Cylinder Object")
            self.log_l1(dir(geo))
            return

        if isinstance(geo, r3.Extrusion):
            self.log_l0("Extrusion")
            # self.log_l1(dir(geo))
            self.log_l1(" Is Cylinder : " + str(geo.IsCylinder()))
            self.log_l1(" NormalAt", geo.NormalAt)
            self.log_l1(" PathStart", geo.PathStart)
            self.log_l1(" PathEnd", geo.PathEnd)
            self.log_l1(" PathTangent", geo.PathTangent)
            self.log_l1(" PointAt", geo.PointAt)
            self.log_l1(" GetPathPlane", geo.GetPathPlane)
            self.log_l1(" Profile Count : " + str(geo.ProfileCount))
            for i in range(geo.ProfileCount):
                self.log_l1(" - {:>4}".format(i))
                c = geo.Profile3d(i, 0.0)
                self.log_l1("   ", c)
                self.log_l1("   IsCircle", c.IsCircle())
                self.log_l1("   Dimension", c.Dimension)
                if hasattr(c, "Radius"):
                    self.log_l1("   Radius", c.Radius)
            self.log_l1(" Profile3d", geo.Profile3d)
            if geo.IsCylinder() is True:
                self.log_l1(" create cylinder")
                height = geo.PathStart.Z - geo.PathEnd.Z
                self.log_l1("Height : ", height)
                c = geo.Profile3d(0, 0.0)
                radius = c.Radius
                self.log_l1("Radius : ", radius)
                obj = doc.addObject("Part::Cylinder", "Extruded Cylinder")
                obj.Height = height
                obj.Radius = radius
                obj.recompute()
            else:
                self.log_l0(" !!! NOT IMPLEMENTED YET !!!")
                File3dm.print_class_attributes(geo, self.log_l2)
            return

        if isinstance(geo, r3.Mesh):
            self.log_l0("Mesh Object")
            return self.create_mesh(doc, geo)

        if isinstance(geo, r3.NurbsSurface):
            self.log_l0("NurbsSurface Object")
            log_l2(dir(geo))
            return self.create_surface(geo)

        if isinstance(geo, r3.PointCloud):
            self.log_l0("PointCloud Object")
            log_l1(dir(geo))
            return

        if isinstance(geo, r3.Surface):
            self.log_l0("Surface Object")
            self.log_l1(geo.IsCylinder)
            self.log_l1(geo.IsSolid)
            self.log_l1(dir(geo))
            return

        self.log_l0("Not yet handled")
        self.log_l1(dir(geo))

    def create_curve(self, edge):
        nc = edge.ToNurbsCurve()
        # log_l1("{} x {}".format(nu.Degree(0), nu.Degree(1)))
        pts = []
        weights = []
        for u in range(len(nc.Points)):
            p = nc.Points[u]
            # self.log_l2(FreeCAD.Vector(p.X,p.Y,p.Z))
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
        pts = []
        weights = []
        self.log_l1("Degrees: {} x {}".format(nu.Degree(0), nu.Degree(1)))
        self.log_l1(
            "Control Points"
            " CountU : {}"
            " CountV : {}"
            "".format(nu.Points.CountU, nu.Points.CountV)
        )
        for u in range(nu.Points.CountU):
            row = []
            wrow = []
            for v in range(nu.Points.CountV):
                p = nu.Points[u, v]
                self.log_l2(FreeCAD.Vector(p.X, p.Y, p.Z))
                row.append(FreeCAD.Vector(p.X / p.W, p.Y / p.W, p.Z / p.W))
                wrow.append(p.W)
            pts.append(row)
            weights.append(wrow)
        self.log_l1("Knots")
        ku, mu = self.getFCKnots(nu.KnotsU)
        kv, mv = self.getFCKnots(nu.KnotsV)
        uperiodic = False  # mu[0] <= nu.Degree(0)
        vperiodic = False  # mv[0] <= nu.Degree(1)
        self.log_l1(list(nu.KnotsU))
        self.log_l1("ku mu")
        self.log_l1(ku, mu)
        self.log_l1("kv mv")
        self.log_l1(kv, mv)
        self.log_l1("Flat knots")
        vflatknots = list(nu.KnotsV)
        self.log_l1("{}\n{}".format(vflatknots, vflatknots))
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
        self.log_l1("Quad Count : " + str(r3mesh.Faces.QuadCount))
        self.log_l1("Triangle Count : " + str(r3mesh.Faces.TriangleCount))
        # FreeCAD only supports Triangles
        self.log_l1(r3mesh.Faces.ConvertQuadsToTriangles())
        self.log_l1(len(r3mesh.Faces))
        self.log_l1("Count : " + str(r3mesh.Faces.Count))
        self.log_l1("Quad Count : " + str(r3mesh.Faces.QuadCount))
        self.log_l1("Vertices Count : " + str(len(r3mesh.Vertices)))
        # log_l1(type(r3mesh.Faces))
        for m in range(r3mesh.Faces.TriangleCount):
            # log_l1('Face')
            mf = r3mesh.Faces[m]
            # log_l1(type(mf))
            # log_l1(dir(mf))
            fval = ()
            # 3dm files always have 4 vertex values even for triangles
            for r in range(0, 3):
                f = mf[r]
                # log_l1('X : '+str(r3mesh.Vertices[f].X)+ \
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

    fi = File3dm(filename, debug_level=0)
    fi.parse_objects(doc)
    FreeCADGui.SendMsgToActiveView("ViewFit")

    # pathName = os.path.dirname(os.path.normpath(filename))

    FreeCAD.Console.PrintMessage("3DM File Imported\n")
