#import Part
#myPart = FreeCAD.ActiveDocument.addObject("Part::Feature","myPartName")
#cube = Part.makeBox(2,2,2)
#myPart.Shape = cube
import FreeCAD as App
import FreeCADGui as Gui
import Part,PartGui,Draft
import math
import os


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

for i, f in enumerate(facelist):
    face = make_tri_face(f[0], f[1], f[2], vtex)
    faces.append(face)
    for e in make_edges(f[0], f[1], f[2]):
        if e not in edgelist:
            edgelist.append(e)

    #facename =  "iface{}".format(i)
    #myface = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign#::Feature',facename)
    
    
myShell = Part.makeShell(faces)   
mySolid = Part.makeSolid(myShell)


myPart = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature','dodeca')
myPart.Shape = mySolid
#myPart.Shape = myShell


App.ActiveDocument.recompute()

# now have a list of edge vertexes in edgelist -- a list of two-vertex tuples for each edge.

# make a list  of vectors that are face midpoints

midpts = []
#orthov = []
for edge in edgelist:
   midpts.append((vtex[edge[0]] + vtex[edge[1]])/2) 


# scale direction vector 
vscale = (1.5, 0.75, 1)


    
spikes = []
spikeu = None
#for i, face in enumerate(facelist):
#
#    pt0 = vtex[face[0]]
#    pt1 = vtex[face[1]]
#    pt2 = vtex[face[2]]
    # vector normal to face
#    midpt = (pt0 + pt1 + pt2)/3. 

# make drill circles for each vertex
# dcircles = []
# for i, v in enumerate(midpts):
#     vname = "circle{}".format(i)
#     myPart = App.ActiveDocument.addObject("Part::Feature", vname)
#     myPart.Shape = Part.makeCircle(0.1,1.1*v, v)
#     #the workaround by directly altering the property
#     dcircles.append(myPart)

# App.ActiveDocument.Body.Group = App.ActiveDocument.Body.Group + dcircles
# App.ActiveDocument.recompute()

# drill holes

#>>> App.getDocument('Unnamed').getObject('Hole').Profile = App.getDocument('Unnamed').getObject('vertex11')
#>>> App.ActiveDocument.recompute()

# holes = []
# for i, d  in enumerate(dcircles):
#     hname = "hole{}".format(i)
#     hole  = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Hole',hname)
#     #hole = App.ActiveDocument.addObject('PartDesign::Hole','Hole')
#     hole.Profile = d
#     hole.Diameter = drill_diam
#     hole.Depth = drill_depth
#     holes.append(hole)



#for midpt in midpts:
spikes = []

# make rotattion quaternion
#22 +/- 1.3
rot = App.Rotation(App.Vector(0,1,0), 20.7)

#for i, midpt in enumerate(midpts):
for i, midpt in enumerate(vtex):

    if True:


        #W = Part.Wire(faces[i].Edges)
        #P = W.extrude(midpt)
        #P = faces[i].extrude(midpt)
        #S = makeCone(radius1,radius2,height,[pnt,dir,angle])


        # vector to tip of cone
        cone_tip = 3*scale * midpt/length(midpt)

        #rotate so center of "tripod" is in Z-direction
        cone_tip = rot.multVec(cone_tip)
        
        # scale this vector so result is elliptical w maj axis in Z
        cone_tip.scale(1.0, 0.7, 1.3)

        cone_length = length(cone_tip)

        # if we start at origin geometrey crashes, so offset cone
        # slightly
        S = Part.makeCone(5, 1, cone_length,  .05*cone_tip, cone_tip )

        #Part.Show(S)
        sname = "spike{}".format(i)

        # make deelybopper for this spike
        #makeSphere(radius,[center_pnt, axis_dir, V_startAngle, V_endAngle, U_angle])
        D = Part.makeSphere(0.2*scale, 1.1*cone_tip)

        spikeu =  S.fuse(D)

        
        myPart = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature',sname)
        myPart.Shape = spikeu
        myPart.Label = "spike{}".format(i)

        #myPart.Placement=


        
        spikes.append(myPart)


App.ActiveDocument.recompute()
App.activeDocument().addObject("Part::MultiFuse","Fusion")
App.activeDocument().Fusion.Shapes = spikes




App.ActiveDocument.recompute()

#scale = FreeCAD.Vector(1.5, 0.75, 1)
#clone = Draft.scale(myPart, scale, copy=False)

App.ActiveDocument.addObject("Part::Cylinder","chopcyl")
FreeCAD.getDocument('Unnamed').getObject('chopcyl').Radius = 4*scale 
FreeCAD.getDocument('Unnamed').getObject('chopcyl').Height = 5*scale 

top = True

if top:
    rot = 0
else:
    rot =180
    
FreeCAD.getDocument('Unnamed').getObject('chopcyl').Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,1,0),rot))

App.activeDocument().addObject("Part::Cut","half")
App.activeDocument().half.Base = App.activeDocument().Fusion
App.activeDocument().half.Tool = App.activeDocument().chopcyl
#Gui.runCommand('PartDesign_MoveTip',0)

App.ActiveDocument.recompute()

App.ActiveDocument.addObject("Part::Cylinder","hole")
FreeCAD.getDocument('Unnamed').getObject('hole').Radius = 1
FreeCAD.getDocument('Unnamed').getObject('hole').Height = 60

align1 = App.ActiveDocument.addObject("Part::Cylinder","align1")
align1.Radius = 1.75/2
align1.Height = 6

align2 =App.ActiveDocument.addObject("Part::Cylinder","align2")
align2.Radius = 1.75/2
align2.Height = 6 

App.ActiveDocument.recompute()


if top:
    rot = 180
else:
    rot = 0

FreeCAD.getDocument('Unnamed').getObject('hole').Placement = App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(0,1,0),rot))

align1.Placement = App.Placement(App.Vector(5,0,0),App.Rotation(App.Vector(0,1,0),rot))
align2.Placement = App.Placement(App.Vector(-5,0,0),App.Rotation(App.Vector(0,1,0),rot))

App.activeDocument().addObject("Part::Cut","poke")
App.activeDocument().poke.Base = App.activeDocument().half
App.activeDocument().poke.Tool = App.activeDocument().hole

App.activeDocument().addObject("Part::Cut","a1")
App.activeDocument().a1.Base = App.activeDocument().poke
App.activeDocument().a1.Tool = App.activeDocument().align1

App.activeDocument().addObject("Part::Cut","final")
App.activeDocument().final.Base = App.activeDocument().a1
App.activeDocument().final.Tool = App.activeDocument().align2

App.ActiveDocument.recompute()



#App.ActiveDocument.Body.Group = App.ActiveDocument.Body.Group + [feature] #the workaround by directly altering the property

# drill two alignment holes using cylinders

#Gui.Selection.addSelection('Unnamed','Body','dodeca.')
#Gui.runCommand('Std_ToggleVisibility',0)
# myPart = App.ActiveDocument.addObject("Part::Feature", "align1")
# myPart.Shape = Part.makeCircle(0.1, App.Vector(0,0,0),  App.Vector(0,0,1))
# myPart.Placement = App.Placement(App.Vector(5,0,0),
#                                  App.Rotation(App.Vector(0,0,1),0))

# hole = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Hole', 'Align')
# hole.Profile = myPart
# hole.Diameter = 1.8
# hole.Depth = 5


# get cwd. This is tricksy becayse os.cwd is path to executable :(
p=os.path.realpath(__file__)
p=os.path.dirname(p)

import Mesh
if top:
    stl_name = os.path.join(p, u"top12spikes.stl")
    fc_name = os.path.join(p, u"top12spikes.FCStd")

else:
    stl_name = os.path.join(p, u"bot12spikes.stl")
    fc_name = os.path.join(p, u"bot12spikes.FCStd")

App.getDocument("Unnamed").saveAs(fc_name)
    
part=[]
part.append(FreeCAD.getDocument("Unnamed").getObject("final"))
Mesh.export(part, stl_name)



print(u"wrote STL file {}".format(stl_name))

App.ActiveDocument.recompute()




