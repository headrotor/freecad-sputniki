#import Part
#myPart = FreeCAD.ActiveDocument.addObject("Part::Feature","myPartName")
#cube = Part.makeBox(2,2,2)
#myPart.Shape = cube
import FreeCAD as App
import FreeCADGui as Gui
import Part,PartGui,Draft
import math
import sys

# vector math from https://wiki.freecadweb.org/FreeCAD_vector_math_library

def length(first):
    """lengh(Vector) - gives vector length"""
    if isinstance(first,FreeCAD.Vector):
        return math.sqrt(first.x*first.x + first.y*first.y + first.z*first.z)

######## size constants, in mm

# inner sphere diameter
sphere_diam = 40.0
icosa_pad = 8.0   # add this to sphere diameter to get (rough?) icosa "diam"
drill_diam = 1.8   # radius of drill holes
drill_depth = 2*icosa_pad
# separation of drill holes in mm
drill_sep = 5

# icosa ratio: multiply scale by this to get outside dimension
icosa_ratio = 48.53/25.0

########


# make triangular face from three corner vertex indexes, given list of verteces
def make_tri_face(v1, v2, v3, vlist):
    face_wire = Part.makePolygon([vlist[v1],vlist[v2],vlist[v3],vlist[v1]])
    return Part.Face(face_wire)

# make triangular face from three corner verteces
def make_tri_face_v(v1, v2, v3):
    face_wire = Part.makePolygon(v1, v2, v3, v1)
    return Part.Face(face_wire)


def make_edges(a, b, c):
    # return sorted pairwise permutations of vertex indexes
    elist = []
    elist.append((b, a) if b < a else (a, b))
    elist.append((c, b) if c < b else (b, c))
    elist.append((a, c) if a < c else (c, a))
    return elist

doc = App.newDocument()


obj = App.ActiveDocument.addObject("PartDesign::Body", "Body")
obj.Label = "dodeca body"

#obj.addProperty("App::PropertyLinkGlobal","Base","Draft","App::Property","The base object that must be duplicated")

vtex =[]
phi = (math.sqrt(5.) + 1.) / 2.0
scale = 1.0

# need to scale phi if scale is not 1.0

scale = (sphere_diam/2 + icosa_pad)/icosa_ratio
phi = phi*scale


vtex.append(FreeCAD.Vector(-scale, phi, 0))
vtex.append(FreeCAD.Vector(scale, phi, 0))
vtex.append(FreeCAD.Vector(-scale, -phi, 0))
vtex.append(FreeCAD.Vector(scale, -phi, 0))


vtex.append(FreeCAD.Vector(0, -scale, phi))
vtex.append(FreeCAD.Vector(0, scale, phi))
vtex.append(FreeCAD.Vector(0, -scale, -phi))
vtex.append(FreeCAD.Vector(0, scale, -phi))

vtex.append(FreeCAD.Vector(phi, 0, -scale))
vtex.append(FreeCAD.Vector(phi, 0, scale))
vtex.append(FreeCAD.Vector(-phi, 0, -scale))
vtex.append(FreeCAD.Vector(-phi, 0, scale))

# for rectangle "skeleton"
# test_wire = Part.makePolygon([vtex[0],vtex[1],vtex[2], vtex[3], vtex[0]])
# Part.show(test_wire)
# test_wire = Part.makePolygon([vtex[4],vtex[5],vtex[6], vtex[7], vtex[4]])
# Part.show(test_wire)
# test_wire = Part.makePolygon([vtex[8],vtex[9],vtex[10], vtex[11], vtex[8]])
# Part.show(test_wire)


# for i in range(len(vtex) - 1):
#     l=Part.LineSegment()
#     l.StartPoint=vtex[i]
#     l.EndPoint=vtex[i+1]

#     doc.addObject("Part::Feature","Line").Shape=l.toShape() 


# make list of faces, three vertex indexes per face
facelist = []

# 5 faces around point 0
facelist.append((0, 11, 5))
facelist.append((0, 5, 1))
facelist.append((0, 1, 7))
facelist.append((0, 7, 10))
facelist.append((0, 10, 11))

# 5 adjacent faces
facelist.append((5, 11, 4))
facelist.append((1, 5, 9))
facelist.append((7, 1, 8))
facelist.append((11, 10, 2))
facelist.append((10, 7, 6))

# 5 faces around point 3
facelist.append((3, 9, 4))
facelist.append((3, 4, 2))
facelist.append((3, 2, 6))
facelist.append((3, 6, 8))
facelist.append((3, 8, 9))

# 5 adjacent faces
facelist.append((4, 9, 5))
facelist.append((2, 4, 11))
facelist.append((6, 2, 10))
facelist.append((8, 6, 7))
facelist.append((9, 8, 1))



faces = []
edgelist = []

thefaces =[]

for i, f in enumerate(facelist):
    face = make_tri_face(f[0], f[1], f[2], vtex)
    faces.append(face)
    for e in make_edges(f[0], f[1], f[2]):
        if e not in edgelist:
            edgelist.append(e)

    facename =  "iface{}".format(i)
    myface = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature',facename)
    myface.Shape = face
    thefaces.append(myface)
    
myShell = Part.makeShell(faces)   
mySolid = Part.makeSolid(myShell)


#myPart = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature','dodeca')
#myPart.Shape = mySolid




App.ActiveDocument.recompute()

# now have a list of edge vertexes in edgelist -- a list of two-vertex tuples for each edge.

# make a list  of vectors that are face midpoints

midpts = []
#orthov = []

# get face centers of icosahedron
for i, face in enumerate(facelist):

    pt0 = vtex[face[0]]
    pt1 = vtex[face[1]]
    pt2 = vtex[face[2]]
    # vector normal to face
    midpt = (pt0 + pt1 + pt2)/3. 
    midpts.append(midpt)

# scale direction vector 
vscale = (1.5, 0.75, 1)

### App.getDocument('Unnamed').getObject('Body').newObject('Sketcher::SketchObject','Sketch')
### App.getDocument('Unnamed').getObject('Sketch').Support = (App.getDocument('Unnamed').getObject('dodeca'),['Face12',])
### App.getDocument('Unnamed').getObject('Sketch').MapMode = 'FlatFace'
### App.ActiveDocument.recompute()
### Gui.getDocument('Unnamed').setEdit(App.getDocument('Unnamed').getObject('Body'),0,'Sketch.')
### ActiveSketch = App.getDocument('Unnamed').getObject('Sketch')
### App.getDocument('Unnamed').getObject('Sketch').addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),6.920364),False)

def make_loft(face1, face2, n):
    # given two faces, create new body, two new sketches,
    #two new circles, and loft between them. Rturn body
    strut = 1 # diameter of strut
    bname = "Body{:02}".format(n)
    snameA = "sketch{:02}A".format(n)
    snameB = "sketch{:02}B".format(n)
    lname = "loft{:02}B".format(n)
    obj = App.ActiveDocument.addObject("PartDesign::Body", bname)
    obj.Label = "body{:02}".format(n)

    sketchA = obj.newObject('Sketcher::SketchObject',snameA)
    #App.getDocument('Unnamed').getObject('Sketch').Support = (App.getDocument('Unnamed').getObject('dodeca'),['Face12',])

    
    # App.getDocument('Unnamed').getObject(snameA).Support = face1
    # App.getDocument('Unnamed').getObject(snameA).MapMode = 'FlatFace'
    # App.ActiveDocument.recompute()
    # App.getDocument('Unnamed').getObject(snameA).addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
    # App.getDocument('Unnamed').getObject(snameA).addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    # App.getDocument('Unnamed').getObject(snameA).addConstraint(Sketcher.Constraint('Diameter',0,5)) 
    sketchA.Support = face1
    sketchA.MapMode = 'FlatFace'
    App.ActiveDocument.recompute()
    sketchA.addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
    sketchA.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    sketchA.addConstraint(Sketcher.Constraint('Diameter',0,strut)) 
    App.ActiveDocument.recompute()

    sketchB = obj.newObject('Sketcher::SketchObject',snameB)
    App.getDocument('Unnamed').getObject(snameB).Support = face2
    App.getDocument('Unnamed').getObject(snameB).MapMode = 'FlatFace'
    App.ActiveDocument.recompute()
    App.getDocument('Unnamed').getObject(snameB).addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
    App.getDocument('Unnamed').getObject(snameB).addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    App.getDocument('Unnamed').getObject(snameB).addConstraint(Sketcher.Constraint('Diameter',0,strut)) 
    App.ActiveDocument.recompute()


    loft = App.getDocument('Unnamed').getObject(bname).newObject('PartDesign::AdditiveLoft',lname)
    App.getDocument('Unnamed').getObject(lname).Profile = App.getDocument('Unnamed').getObject(snameA)
    App.getDocument('Unnamed').getObject(lname).Sections += [App.getDocument('Unnamed').getObject(snameB)]
    App.ActiveDocument.recompute()
    return loft
    
spikes = []
spikeu = None

for i, face in enumerate(facelist):

    pt0 = vtex[face[0]]
    pt1 = vtex[face[1]]
    pt2 = vtex[face[2]]
    #vector normal to face
    midpt = (pt0 + pt1 + pt2)/3. 
    print(face)


lofts = []

count = 0
#for i, f1 in enumerate(thefaces[:-2]):
for i, f1 in enumerate(thefaces[:-1]):
    for j, f2 in enumerate(thefaces[i+1:]):
        print("making bone {} {} {}".format(i,j,count))
        lofts.append(make_loft(f1, f2, count))
        App.ActiveDocument.recompute()
        count += 1
#lofts.append(make_loft(thefaces[0], thefaces[5], 1))
#App.ActiveDocument.recompute()
#lofts.append(make_loft(thefaces[0], thefaces[11], 2))

#cube1 bodies:
cube1= ['Body117', 'Body147', 'Body102', 'Body99', 'Body172', 'Body150', 'Body184', 'Body15', 'Body67', 'Body02', 'Body05', 'Body57']

#cube2
cube2 = [ 'Body87','Body189', 'Body89', 'Body146', 'Body127', 'Body167', 'Body58', 'Body68', 'Body20', 'Body36', 'Body153', 'Body22']

cube3 = ['Body82', 
         'Body159',
         'Body70', 
         'Body178', 
         
         'Body38', 
         'Body85', 
         'Body40',
         'Body90',

         'Body156',
         'Body106',
         'Body187',
         'Body52']      

cube4 = ['Body138',
         'Body155',
         'Body126',
         'Body124',

         'Body43' ,
         'Body174',
         'Body53' ,
         'Body01' ,

         'Body183',
         'Body14' ,
         'Body07' ,
         'Body157']

cube5= ['Body113',
        'Body74' ,
        'Body21' ,
        'Body24' ,

        'Body81' ,
        'Body32' ,
        'Body180',
        'Body175',

        'Body165',
        'Body163',
        'Body137',
        'Body118']

dodec = [ 'Body158', 'Body131', 'Body132', 'Body166', 'Body154',
'Body148', 'Body149', 'Body94', 'Body04', 'Body03', 'Body54',
'Body59', 'Body143', 'Body173', 'Body169', 'Body162', 'Body145',
'Body95', 'Body73', 'Body142', 'Body179', 'Body123', 'Body41',
'Body37', 'Body19', 'Body23', 'Body111', 'Body107', 'Body00',
'Body122']


cubestruts = []

for strutname in cube1:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Cube1")
App.activeDocument().Cube1.Links = cubestruts
App.ActiveDocument.recompute()

cubestruts = []
for strutname in cube2:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Cube2")
App.activeDocument().Cube2.Links = cubestruts
App.ActiveDocument.recompute()

cubestruts = []
for strutname in cube3:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Cube3")
App.activeDocument().Cube3.Links = cubestruts
App.ActiveDocument.recompute()

cubestruts = []
for strutname in cube4:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Cube4")
App.activeDocument().Cube4.Links = cubestruts
App.ActiveDocument.recompute()

cubestruts = []
for strutname in cube5:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Cube5")
App.activeDocument().Cube5.Links = cubestruts
App.ActiveDocument.recompute()

cubestruts = []
for strutname in dodec:
    cubestruts.append(App.getDocument('Unnamed').getObject(strutname))

App.activeDocument().addObject("Part::Compound","Dodec")
App.activeDocument().Dodec.Links = cubestruts
App.ActiveDocument.recompute()



tetras = []
#0
tetras.append([ 'Body130', 'Body128', 'Body170','Body47', 'Body42', 'Body49'])
#1
tetras.append(['Body119', 'Body72', 'Body116', 'Body164', 'Body80', 'Body77'])
#2
tetras.append(['Body51', 'Body177', 'Body48', 'Body96', 'Body39', 'Body93'])
#3
tetras.append(['Body91', 'Body62', 'Body55', 'Body98', 'Body69', 'Body168'])
#4
tetras.append([ 'Body110', 'Body71', 'Body83', 'Body76', 'Body160','Body103'])
#5
tetras.append([ 'Body125', 'Body27', 'Body25', 'Body35', 'Body133','Body152'])
#6
tetras.append([ 'Body31', 'Body26', 'Body139', 'Body33','Body176', 'Body141'])
#7
tetras.append([ 'Body08', 'Body10', 'Body161', 'Body136', 'Body144', 'Body18'])
#8
#9
tetras.append([ 'Body06', 'Body09', 'Body16', 'Body114','Body121', 'Body151'])
#10
tetras.append([ 'Body56', 'Body63', 'Body66', 'Body105', 'Body108', 'Body171'])

for i, t in enumerate(tetras):
    tname = "tetra{}".format(i)
    print("making: " + tname)
    tstruts = []
    for strut in t:
        tstruts.append(App.getDocument('Unnamed').getObject(strut))

    tetra = App.activeDocument().addObject("Part::Compound",tname)
    tetra.Links = tstruts
    App.ActiveDocument.recompute()

cstar_struts = [ 'Body120', 'Body79', 'Body12', 'Body134', 'Body140',
          'Body60', 'Body109', 'Body29', 'Body45', 'Body97']

struts = []
for strutname in cstar_struts:
    struts.append(App.getDocument('Unnamed').getObject(strutname))

part = App.activeDocument().addObject("Part::Compound","central_star")
part.Links = struts
App.ActiveDocument.recompute()

stella_struts = [ 'Body185', 'Body28', 'Body135', 'Body75', 'Body44',
           'Body61', 'Body115', 'Body11', 'Body46', 'Body92', 'Body181',
           'Body129', 'Body112', 'Body100', 'Body186', 'Body86', 'Body88',
           'Body182', 'Body65', 'Body50', 'Body64', 'Body17', 'Body101',
           'Body34', 'Body78', 'Body30', 'Body84', 'Body13', 'Body104',
           'Body188']

struts = []
for strutname in stella_struts:
    struts.append(App.getDocument('Unnamed').getObject(strutname))

part = App.activeDocument().addObject("Part::Compound","stella")
part.Links = struts
App.ActiveDocument.recompute()

    
exit(0)






