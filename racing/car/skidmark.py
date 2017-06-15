from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat, \
    Geom, GeomTriangles, GeomNode, Mat4, Material, OmniBoundingVolume
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.interval.LerpInterval import LerpFunc


class Skidmark:

    def __init__(self, wheel_pos, radius, heading):
        self.radius = radius
        v_f = GeomVertexFormat.getV3()
        self.vdata = GeomVertexData('skid', v_f, Geom.UHDynamic)
        self.vdata.setNumRows(1)
        self.vertex = GeomVertexWriter(self.vdata, 'vertex')
        self.prim = GeomTriangles(Geom.UHStatic)
        self.cnt = 1
        self.last_pos = wheel_pos
        geom = Geom(self.vdata)
        geom.addPrimitive(self.prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        nodePath = eng.gfx.root.attachNewNode(node)
        nodePath.setTransparency(True)
        nodePath.setDepthOffset(1)
        self.__set_material(nodePath)
        nodePath.node().setBounds(OmniBoundingVolume())
        self.add_vertices(radius, heading)
        self.add_vertices(radius, heading)
        def alpha(t, np):
            if not np.is_empty():
                np.setAlphaScale(t)
            # this if seems necessary since, if there are skidmarks and you
            # exit from the race (e.g. back to the menu), then alpha is being
            # called from the interval manager even if the interval manager
            # correctly says that there are 0 intervals.
        self.remove_seq = Sequence(
            Wait(8),
            LerpFunc(alpha, 8, 1, 0, 'easeInOut', [nodePath]),
            Func(nodePath.remove_node))
        self.remove_seq.start()

    def __set_material(self, nodePath):
        mat = Material()
        mat.setAmbient((.35, .35, .35, .5))
        mat.setDiffuse((.35, .35, .35, .5))
        mat.setSpecular((.35, .35, .35, .5))
        mat.setShininess(12.5)
        nodePath.set_material(mat, 1)

    def add_vertices(self, radius, heading):
        base_pos = self.last_pos + (0, 0, -radius + .05)
        rot_mat = Mat4()
        rot_mat.setRotateMat(heading, (0, 0, 1))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((-.12, 0, 0)))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((.12, 0, 0)))
        if self.cnt >= 3:
            self.prim.addVertices(self.cnt - 3, self.cnt - 2, self.cnt - 1)
            self.prim.addVertices(self.cnt - 2, self.cnt, self.cnt - 1)
        self.cnt += 2

    def update(self, pos, heading):
        if (pos - self.last_pos).length() > .2:
            self.last_pos = pos
            self.add_vertices(self.radius, heading)

    def destroy(self):
        self.remove_seq = self.remove_seq.finish()
