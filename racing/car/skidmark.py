from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat, \
    Geom, GeomTriangles, GeomNode, Mat4, Material, OmniBoundingVolume
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
from direct.interval.LerpInterval import LerpFunc


class Skidmark:

    def __init__(self, car, whl):
        self.car = car
        self.whl = whl
        v_f = GeomVertexFormat.getV3()
        self.vdata = GeomVertexData('skid', v_f, Geom.UHDynamic)
        self.vdata.setNumRows(1)
        self.vertex = GeomVertexWriter(self.vdata, 'vertex')
        self.width = .12
        self.prim = GeomTriangles(Geom.UHStatic)
        self.cnt = 1
        self.last_pos = self.car.gfx.wheels[self.whl].get_pos(render)
        geom = Geom(self.vdata)
        geom.addPrimitive(self.prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        nodePath = render.attachNewNode(node)
        nodePath.setTransparency(True)
        nodePath.setDepthOffset(1)
        mat = Material()
        mat.setAmbient((.35, .35, .35, .5))
        mat.setDiffuse((.35, .35, .35, .5))
        mat.setSpecular((.35, .35, .35, .5))
        mat.setShininess(12.5)
        nodePath.set_material(mat, 1)
        nodePath.node().setBounds(OmniBoundingVolume())
        self.add_vertices()
        self.add_vertices()
        self.remove_seq = Sequence(
            Wait(8),
            LerpFunc(nodePath.setAlphaScale, 8, 1, 0, 'easeInOut'),
            Func(nodePath.remove_node))
        self.remove_seq.start()

    def add_vertices(self):
        w_r = self.car.phys.vehicle.getWheels()[0].getWheelRadius()
        base_pos = self.last_pos + (0, 0, -w_r + .05)
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.car.gfx.nodepath.get_h(), (0, 0, 1))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((-self.width, 0, 0)))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((self.width, 0, 0)))
        if self.cnt >= 3:
            self.prim.addVertices(self.cnt - 3, self.cnt - 2, self.cnt - 1)
            self.prim.addVertices(self.cnt - 2, self.cnt, self.cnt - 1)
        self.cnt += 2

    def update(self):
        if not hasattr(self, 'vdata'):
            return
        fr_pos = self.car.gfx.wheels[self.whl].get_pos(render)
        if (fr_pos - self.last_pos).length() < .2:
            return
        self.last_pos = fr_pos
        self.add_vertices()

    def destroy(self):
        self.car = None
        self.remove_seq = self.remove_seq.finish()
