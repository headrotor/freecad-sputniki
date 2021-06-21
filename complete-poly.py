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


if False:
    obj = App.ActiveDocument.addObject("PartDesign::Body", "frame")
    obj.Label = "frame"


    wire = Part.makePolygon([vtex[0],vtex[1],vtex[3], vtex[2], vtex[0]])
    #wire = Part.makePolygon([vtex[0],vtex[1],vtex[2], vtex[3], vtex[0]])
    frame1 = App.getDocument('Unnamed').getObject('frame').newObject('PartDesign::Feature','frame1')
    frame1.Shape = wire


    #wire = Part.makePolygon([vtex[4],vtex5],vtex[6], vtex[7], vtex[4]])
    wire = Part.makePolygon([vtex[5],vtex[4],vtex[6], vtex[7], vtex[5]])
    frame2 = App.getDocument('Unnamed').getObject('frame').newObject('PartDesign::Feature','frame2')
    frame2.Shape = wire


    wire = Part.makePolygon([vtex[8],vtex[9],vtex[11], vtex[10], vtex[8]])
    frame3 = App.getDocument('Unnamed').getObject('frame').newObject('PartDesign::Feature','frame3')
    frame3.Shape = wire

    App.activeDocument().addObject("Part::Compound","Frame")
    App.activeDocument().Frame.Links = [frame1, frame2, frame3]
    App.ActiveDocument.recompute()




#Part.show(test_wire)


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




obj = App.ActiveDocument.addObject("PartDesign::Body", "Icosa")
obj.Label = "Body"



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
    myface = obj.newObject('PartDesign::Feature',facename)
    myface.Shape = face
    thefaces.append(myface)
    
myShell = Part.makeShell(faces)   
mySolid = Part.makeSolid(myShell)






myPart = obj.newObject('PartDesign::Feature','icosa-shell')
#myPart.Shape = mySolid
myPart.Shape = myShell
App.ActiveDocument.recompute()

myPart = obj.newObject('PartDesign::Feature','icosa-solid')
#myPart.Shape = mySolid
myPart.Shape = mySolid
App.ActiveDocument.recompute()



# make wire dodeca 
#comp = App.getDocument('Unnamed').getObject('Body').newObject("Part::Compound","icosa_wire")
#comp.Links = thefaces
#App.ActiveDocument.recompute()


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


# connect midpoints of faces to get full connectivity:

hairball = []
lengths = []
uniq_lengths = []
count = 0
for i, p1 in enumerate(midpts[:-1]):
    for j, p2 in enumerate(midpts[i+1:]):
        name = "wire{:02d}-{:02d}C{:03}".format(i,j,count)
        print(name)
        name = "Body{}".format(count)
        #wire = Part.Line(p1, p2)
        #wire = Part.LineSegment(p1, p2)
        #hairball.append(wire)
        wire = Part.makeLine(p1, p2)
        edge = Part.Edge(wire)
        print("{} len: {}".format(name, str(edge.Length)))
        hairball.append(edge)
        lengths.append(edge.Length)
        if edge.Length not in uniq_lengths:
            uniq_lengths.append(edge.Length)
        #myPart = App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Feature','hairball')

        feat = obj.newObject('PartDesign::Feature',name)
        feat.Shape = edge
        count += 1

App.ActiveDocument.recompute()

tetras = []
#0
tetras.append([ hairball[130], hairball[128], hairball[170],hairball[47], hairball[42], hairball[49]])
#1
tetras.append([hairball[119], hairball[72], hairball[116], hairball[164], hairball[80], hairball[77]])
# #2
tetras.append([hairball[51], hairball[177], hairball[48], hairball[96], hairball[39], hairball[93]])
# #3
tetras.append([hairball[91], hairball[62], hairball[55], hairball[98], hairball[69], hairball[168]])
#4
tetras.append([ hairball[110], hairball[71], hairball[83], hairball[76], hairball[160],hairball[103]])
#5
tetras.append([ hairball[125], hairball[27], hairball[25], hairball[35], hairball[133],hairball[152]])
#6
tetras.append([ hairball[31], hairball[26], hairball[139], hairball[33],hairball[176], hairball[141]])
#7
tetras.append([ hairball[8], hairball[10], hairball[161], hairball[136], hairball[144], hairball[18]])
#8
#9
tetras.append([ hairball[6], hairball[9], hairball[16], hairball[114],hairball[121], hairball[151]])
#10
tetras.append([ hairball[56], hairball[63], hairball[66], hairball[105], hairball[108], hairball[171]])

stella_struts = [ hairball[185], hairball[28], hairball[135],
                  hairball[75], hairball[44], hairball[61],
                  hairball[115], hairball[11], hairball[46],
                  hairball[92], hairball[181], hairball[129],
                  hairball[112], hairball[100], hairball[186],
                  hairball[86], hairball[88], hairball[182],
                  hairball[65], hairball[50], hairball[64],
                  hairball[17], hairball[101], hairball[34],
                  hairball[78], hairball[30], hairball[84],
                  hairball[13], hairball[104], hairball[188]]


#cube1 bodies:
cube1= [hairball[117], hairball[147], hairball[102], hairball[99], hairball[172],
        hairball[150], hairball[184], hairball[15], hairball[67], hairball[2], hairball[5],
        hairball[57]]

#cube2
cube2 = [ hairball[87],hairball[189], hairball[89], hairball[146], hairball[127],
          hairball[167], hairball[58], hairball[68], hairball[20], hairball[36], hairball[153],
          hairball[22]]

cube3 = [hairball[82], hairball[159], hairball[70], hairball[178], hairball[38], hairball[85],
         hairball[40], hairball[90], hairball[156], hairball[106], hairball[187],
         hairball[52]]      

cube4 = [hairball[138], hairball[155], hairball[126], hairball[124], hairball[43],
         hairball[174], hairball[53], hairball[1], hairball[183], hairball[14],
         hairball[7], hairball[157]]

cube5= [hairball[113], hairball[74], hairball[21], hairball[24],
        hairball[81], hairball[32], hairball[180], hairball[175],
        hairball[165], hairball[163], hairball[137], hairball[118]]

dodec = [ hairball[158], hairball[131], hairball[132], hairball[166], hairball[154],
          hairball[148], hairball[149], hairball[94], hairball[4], hairball[3], hairball[54],
          hairball[59], hairball[143], hairball[173], hairball[169], hairball[162], hairball[145],
          hairball[95], hairball[73], hairball[142], hairball[179], hairball[123], hairball[41],
          hairball[37], hairball[19], hairball[23], hairball[111], hairball[107], hairball[0],
          hairball[122]]





tetras = Part.getSortedClusters(stella_struts)
#tetras = Part.getSortedClusters(dodec)

stellaparts = []
for i, t in enumerate(tetras):
    tname = "tetra{:02d}".format(i)
    print("making: " + tname)

    # tetra = App.activeDocument().addObject("Part::Compound",tname)
    # tetra.Links = tstruts
    tetra = App.ActiveDocument.addObject("PartDesign::Body", tname)
    App.ActiveDocument.recompute()

    wires = Part.Wire(t)
    
    skel = tetra.newObject('PartDesign::Feature',tname+"wires")
    skel.Shape = wires
    App.ActiveDocument.recompute()
    
    diam = 25.4/16.  # 1/16 inch diameter
    struts = []
    for j, strut in enumerate(t):
    
        #sname = tname + "edge{}".format(j+1)
        sname = tname + "wire{:02d}".format(j)
        edge = tetra.newObject('PartDesign::Feature',sname)
        edge.Shape =  Part.Wire(strut)


        #wire = Part.Wire(strut)
        #edge = tetra.newObject('PartDesign::Feature',sname)
        #edge.Shape = wire
        #App.ActiveDocument.recompute()

        #App.getDocument('Unnamed').getObject('sketch054').Support = [(App.getDocument('Unnamed').getObject('tetra9001'),'Edge1')]
        # make sketch normal to this edge
        sketchA = tetra.newObject('Sketcher::SketchObject',"sketch")
        #[(App.getDocument('Unnamed').getObject('tetra9001'),'Edge1')]
        ename = 'Edge{}'.format(j+1)
#       sketchA.Support = [(App.getDocument('Unnamed').getObject('tetra9001'),'Edge1')]
        #sketchA.Support = [(App.getDocument('Unnamed').getObject('tetra'),'ename')]
        sketchA.Support = [(App.ActiveDocument.getObject(tname+"wires"),ename)]
        #App.ActiveDocument.recompute()
        sketchA.MapMode =  'NormalToEdge'
        #App.ActiveDocument.recompute()


        # App.ActiveDocument.recompute()
        sketchA.addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
        sketchA.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
        sketchA.addConstraint(Sketcher.Constraint('Diameter',0,diam)) 
        #App.ActiveDocument.recompute()
        pipe = tetra.newObject('PartDesign::AdditivePipe','AdditivePipe')
        pipe.Profile = sketchA
        #App.ActiveDocument.recompute()
        #pipe.Spine = [(App.getDocument('Unnamed').getObject(tname+"wires"),ename)]
        pipe.Spine = FreeCAD.getDocument('Unnamed').getObject(sname)
        App.ActiveDocument.recompute()
        struts.append(pipe)

    binder= tetra.newObject('PartDesign::SubShapeBinder','SubShapeBinder')
    #App.ActiveDocument.recompute()
    binder.Support = struts
    App.ActiveDocument.recompute()

    
     #App.getDocument('Unnamed').getObject('stella').newObjectAt('PartDesign::Boolean','Boolean', FreeCADGui.Selection.getSelection())
     #App.getDocument('Unnamed').getObject('stella').newObject('PartDesign::SubShapeBinder','Reference')
     #App.getDocument('Unnamed').getObject('Boolean').addObjects([App.getDocument('Unnamed').getObject('Reference'),])

    #fuse  = tetra.newObject('PartDesign::Boolean','fuse')
    print("here")
    fuse  = tetra.newObjectAt('PartDesign::Boolean', binder.Label )
    fuse.addObjects([binder,])
    App.ActiveDocument.recompute()

    stellaparts.extend(struts)



    
stella = App.ActiveDocument.addObject("PartDesign::Body", "stella")
binder= stella.newObject('PartDesign::SubShapeBinder','SubShapeBinder')
#binder.Support = struts
binder.Support = stellaparts
App.ActiveDocument.recompute()
fuse  = stella.newObjectAt('PartDesign::Boolean', binder.Label )
fuse.addObjects([binder,])
App.ActiveDocument.recompute()


for v in midpts:


    # make sphere body
    spherebody = App.ActiveDocument.addObject("PartDesign::Body", "bulb")
    # XY plane wll be the fourth element of the origin, whuich is the first element in new bod
    orgname = spherebody.OutList[0].OutList[3].Name
    print("found origin " + orgname)
    sphere = spherebody.newObject('PartDesign::AdditiveSphere','endbulb')
    #sphere.MapReversed = False
    sphere.Support = [(App.ActiveDocument.getObject(orgname),'')]
    #sphere.Support = [(App.ActiveDocument.getObject('XY_Plane005'),'')]
    #sphere.MapPathParameter = 0.000000
    sphere.MapMode = 'FlatFace'
    sphere.Radius = 6
    App.ActiveDocument.recompute()
    sphere.AttachmentOffset = App.Placement(v,  App.Rotation(0., 0.0, 0.0))
    App.ActiveDocument.recompute()

    binder= spherebody.newObject('PartDesign::SubShapeBinder','SubShapeBinder')
    #binder.Support = struts
    binder.Support = stellaparts
    App.ActiveDocument.recompute()
    #fuse  = spherebody.newObjectAt('PartDesign::Boolean', binder.Label )
    fuse  = spherebody.newObject('PartDesign::Boolean', 'thefuse' )
    fuse.addObjects([sphere, binder,])
    fuse.Type = 'Cut'
    fuse.NewSolid = True
    App.ActiveDocument.recompute()


print("you will need {} end bobbles".format(len(midpts)))
print("you will need {} struts".format(len(stellaparts)))
exit(0)

    #cut = spherebody.newObject('PartDesign::AdditiveSphere','endbulb')        



# myShell = Part.makeShell(wires)   
    # mySolid = Part.makeSolid(myShell)
    # App.ActiveDocument.recompute()
    # myPart = tetra.newObject('PartDesign::Feature','tetra-shell')
    # myPart.Shape = myShell
    # myPart = tetra.newObject('PartDesign::Feature','tetra-solid')
    # myPart.Shape = mySolid



### ### Begin command PartDesign_NewSketch
### App.getDocument('Unnamed').getObject('tetra9').newObjectAt('Sketcher::SketchObject', 'Sketch001', FreeCADGui.Selection.getSelection())
### import Show
### from Show.Containers import isAContainer
### _tv_Sketch001 = Show.TempoVis(App.ActiveDocument, tag= 'PartGui::TaskAttacher')
### tvObj = App.getDocument('Unnamed').getObject('Sketch001')
### dep_features = _tv_Sketch001.get_all_dependent(App.getDocument('Unnamed').getObject('tetra9'), 'Sketch001.')
### dep_features = [o for o in dep_features if not isAContainer(o)]
### if tvObj.isDerivedFrom('PartDesign::CoordinateSystem'):
### 	visible_features = [feat for feat in tvObj.InList if feat.isDerivedFrom('PartDesign::FeaturePrimitive')]
### 	dep_features = [feat for feat in dep_features if feat not in visible_features]
### 	del(visible_features)
### _tv_Sketch001.hide(dep_features)
### _tv_Sketch001.show(tvObj)
### del(dep_features)
### if not tvObj.isDerivedFrom('PartDesign::CoordinateSystem'):
### 		if len(tvObj.Support) > 0:
### 			_tv_Sketch001.show([lnk[0] for lnk in tvObj.Support])
### del(tvObj)
### ### End command PartDesign_NewSketch
### # Gui.Selection.addSelection('Unnamed','tetra9','Sketch001.')
### # Gui.Selection.clearSelection()
### # Gui.Selection.addSelection('Unnamed','tetra9','tetra9001.Edge1',-1.01733,12.5876,-1.01733)
### App.getDocument('Unnamed').getObject('Sketch001').AttachmentOffset = App.Placement(App.Vector(0.0000000000, 0.0000000000, 0.0000000000),  App.Rotation(0.0000000000, 0.0000000000, 0.0000000000))
### App.getDocument('Unnamed').getObject('Sketch001').MapReversed = False
### App.getDocument('Unnamed').getObject('Sketch001').Support = [(App.getDocument('Unnamed').getObject('tetra9001'),'Edge1')]
### App.getDocument('Unnamed').getObject('Sketch001').MapPathParameter = 0.000000
### App.getDocument('Unnamed').getObject('Sketch001').MapMode = 'NormalToEdge'
### App.ActiveDocument.recompute()
### Gui.getDocument('Unnamed').resetEdit()
### _tv_Sketch001.restore()
### del(_tv_Sketch001)
### # Gui.Selection.clearSelection()
### # Gui.Selection.addSelection('Unnamed','tetra9','Sketch001.')
### Gui.getDocument('Unnamed').setEdit(FreeCAD.getDocument('Unnamed').getObject('tetra9'),0,u'Sketch001.')
### ActiveSketch = App.getDocument('Unnamed').getObject('Sketch001')
### tv = Show.TempoVis(App.ActiveDocument, tag= ActiveSketch.ViewObject.TypeId)
### ActiveSketch.ViewObject.TempoVis = tv
### if ActiveSketch.ViewObject.EditingWorkbench:
###   tv.activateWorkbench(ActiveSketch.ViewObject.EditingWorkbench)
### if ActiveSketch.ViewObject.HideDependent:
###   tv.hide(tv.get_all_dependent(App.getDocument('Unnamed').getObject('tetra9'), 'Sketch001.'))
### if ActiveSketch.ViewObject.ShowSupport:
###   tv.show([ref[0] for ref in ActiveSketch.Support if not ref[0].isDerivedFrom("PartDesign::Plane")])
### if ActiveSketch.ViewObject.ShowLinks:
###   tv.show([ref[0] for ref in ActiveSketch.ExternalGeometry])
### tv.hide(ActiveSketch.Exports)
### tv.hide(ActiveSketch)
### del(tv)
### 
### import PartDesignGui
### ActiveSketch = App.getDocument('Unnamed').getObject('Sketch001')
### if ActiveSketch.ViewObject.RestoreCamera:
###   ActiveSketch.ViewObject.TempoVis.saveCamera()
###     

# all e
print(uniq_lengths)

ddq_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[0]) < 0.0001:
        print("adding dod edge {}".format(i))
        ddq_edges.append(hairball[i])
        
wire = Part.Wire(ddq_edges)
dod = App.ActiveDocument.addObject("PartDesign::Body", "dod")
face = dod.newObject('PartDesign::Feature','Dod')
face.Shape = wire
App.ActiveDocument.recompute()


cube1_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[1]) < 0.0001:
        print("adding cube1 edge {}".format(i))
        cube1_edges.append(hairball[i])
        
wire = Part.Wire(cube1_edges)
cubes1 = App.ActiveDocument.addObject("PartDesign::Body", "cubes1")
face = cubes1.newObject('PartDesign::Feature','Cubes1')
face.Shape = wire
App.ActiveDocument.recompute()


tet_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[3]) < 0.0001:
        print("adding tet edge {}".format(i))
        tet_edges.append(hairball[i])
        
wire = Part.Wire(tet_edges)
tet = App.ActiveDocument.addObject("PartDesign::Body", "tet")
face = tet.newObject('PartDesign::Feature','Tets')
face.Shape = wire
App.ActiveDocument.recompute()

tet2_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[4]) < 0.0001:
        print("adding tet2 edge {}".format(i))
        tet2_edges.append(hairball[i])
        
wire = Part.Wire(tet2_edges)
tet2 = App.ActiveDocument.addObject("PartDesign::Body", "tet2")
face = tet2.newObject('PartDesign::Feature','Tet2')
face.Shape = wire
App.ActiveDocument.recompute()


star_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[5]) < 0.0001:
        print("adding star edge {}".format(i))
        star_edges.append(hairball[i])
        
wire = Part.Wire(tet_edges)
star = App.ActiveDocument.addObject("PartDesign::Body", "star")
face = star.newObject('PartDesign::Feature','Star')
face.Shape = wire
App.ActiveDocument.recompute()



giant_edges = []
for i, e in enumerate(hairball):
    if abs(e.Length - uniq_lengths[5]) < 0.0001:
        print("adding giant edge {}".format(i))
        giant_edges.append(hairball[i])
        
wire = Part.Wire(tet_edges)
giant = App.ActiveDocument.addObject("PartDesign::Body", "giant")
face = giant.newObject('PartDesign::Feature','Giant')
face.Shape = wire
App.ActiveDocument.recompute()






#App.activeDocument().addObject("Part::Compound","Hairball")
#App.activeDocument().Hairball.Links = hairball





exit(0)
    
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
    strut = 3 # diameter of strut
    bname = "Body{:02}".format(n)
    snameA = "sketch{:02}A".format(n)
    snameB = "sketch{:02}B".format(n)
    lname = "loft{:02}B".format(n)
    obj = App.ActiveDocument.addObject("PartDesign::Body", bname)
    obj.Label = "body{:02}".format(n)

    sketchA = obj.newObject('Sketcher::SketchObject',snameA)
    sketchA.Support = face1
    sketchA.MapMode = 'FlatFace'
    App.ActiveDocument.recompute()
    sketchA.addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
    sketchA.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    sketchA.addConstraint(Sketcher.Constraint('Diameter',0,strut)) 
    #App.ActiveDocument.recompute()

    sketchB = obj.newObject('Sketcher::SketchObject',snameB)
    sketchB.Support = face2
    sketchB.MapMode = 'FlatFace'
    App.ActiveDocument.recompute()
    sketchB.addGeometry(Part.Circle(App.Vector(-0.000000,0.000000,0),App.Vector(0,0,1),7.858573),False)
    sketchB.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    sketchB.addConstraint(Sketcher.Constraint('Diameter',0,strut)) 
    App.ActiveDocument.recompute()


    loft = App.getDocument('Unnamed').getObject(bname).newObject('PartDesign::AdditiveLoft',lname)
    #loft.Profile = App.getDocument('Unnamed').getObject(snameA)
    #loft.Sections += [App.getDocument('Unnamed').getObject(snameB)]
    loft.Profile = sketchA
    loft.Sections = [sketchB]
    App.ActiveDocument.recompute()

    #fillet = App.getDocument('Unnamed').getObject(bname).newObjectAt('PartDesign::Fillet','Fillet', FreeCADGui.Selection.getSelection())
    ##App.getDocument('Unnamed').getObject('Fillet').Radius = 1.000000
    ##App.getDocument('Unnamed').getObject('Fillet').Base = (App.getDocument('Unnamed').getObject(lname),["Face1",])
    #fillet.Radius = 1.000000
    #fillet.Base = (App.getDocument('Unnamed').getObject(lname),["Face1",])
 
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
cube1= ['Body117', 'Body147', 'Body102', 'Body99', 'Body172',
        'Body150', 'Body184', 'Body15', 'Body67', 'Body02', 'Body05',
        'Body57']

#cube2
cube2 = [ 'Body87','Body189', 'Body89', 'Body146', 'Body127',
          'Body167', 'Body58', 'Body68', 'Body20', 'Body36', 'Body153',
          'Body22']

cube3 = ['Body82', 'Body159', 'Body70', 'Body178', 'Body38', 'Body85',
         'Body40', 'Body90', 'Body156', 'Body106', 'Body187',
         'Body52']      

cube4 = ['Body138', 'Body155', 'Body126', 'Body124', 'Body43' ,
         'Body174', 'Body53' , 'Body01' , 'Body183', 'Body14' ,
         'Body07' , 'Body157']

cube5= ['Body113', 'Body74' , 'Body21' , 'Body24' ,
        'Body81' , 'Body32' , 'Body180', 'Body175',
        'Body165', 'Body163', 'Body137', 'Body118']

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

cgiant_struts = [ 'Body120', 'Body79', 'Body12', 'Body134', 'Body140',
          'Body60', 'Body109', 'Body29', 'Body45', 'Body97']

struts = []
for strutname in cgiant_struts:
    struts.append(App.getDocument('Unnamed').getObject(strutname))

part = App.activeDocument().addObject("Part::Compound","central_giant")
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






