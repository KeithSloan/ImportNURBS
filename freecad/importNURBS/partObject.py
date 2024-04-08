import Part

class BSplineSurface():

    def __init__(self, obj, UDegree, VDegree, MaxDegree, UKnots, VKnots):
        super().__init__(obj)
        obj.addProperty("App::PropertyInteger", "UDegree", "BSplineSurface", \
               "UDegree").UDegree = UDegree
        obj.addProperty("App::PropertyInteger", "VDegree", "BSplineSurface", \
               "VDegree").VDegree = VDegree
        obj.addProperty("App::PropertyInteger", "MaxDegree", "BSplineSurface", \
               "MaxDegree").MaxDegree = MaxDegree
        obj.Proxy = self


    def onChanged(self, fp, prop):
        """Do something when a property has changed"""
        # print(fp.Label+" State : "+str(fp.State)+" prop : "+prop)
        # Changing Shape in createGeometry will redrive onChanged
        if "Restore" in fp.State:
            return

        if prop in ["UDegree", "VDegree", "MAxDegree"]:
            self.createGeometry(fp)


    def createGeometry(self,sp):
        fp.Shape = Part.Shape()


    def scale(self, fp):
        print(f"Rescale : {fp.scale}")
        mat = FreeCAD.Matrix()
        mat.scale(fp.scale)
        fp.Shape = fp.Shape.transformGeometry(mat)


    def execute(self,fp)
        self.createGeometry(fp)
