from panda3d.core import NodePath, Camera, OrthographicLens, TextureStage


class Signs(object):

    def __init__(self, track_model, sign_name, sign_cb):
        self.buffers = []
        self.drs = []
        self.cameras = []
        self.renders = []
        self.track_model = track_model
        self.sign_name = sign_name
        self.sign_cb = sign_cb

    def set_signs(self):
        signs = self.track_model.findAllMatches('**/%s*' % self.sign_name)
        map(lambda i_sign: self.__set_sign(*i_sign), enumerate(signs))

    def __set_sign(self, i, sign):
        self.__set_render_to_texture()
        self.sign_cb(self.renders[i])
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MDecal)
        sign.setTexture(ts, self.buffers[i].getTexture())

    def __set_render_to_texture(self):
        self.buffers += [base.win.makeTextureBuffer('result buffer', 256, 256)]
        self.buffers[-1].setSort(-100)

        self.drs += [self.buffers[-1].makeDisplayRegion()]
        self.drs[-1].setSort(20)

        self.cameras += [NodePath(Camera('camera 2d'))]
        lens = OrthographicLens()
        lens.setFilmSize(1, 1)
        lens.setNearFar(-1000, 1000)
        self.cameras[-1].node().setLens(lens)

        self.renders += [NodePath('result render')]
        self.renders[-1].setDepthTest(False)
        self.renders[-1].setDepthWrite(False)
        self.cameras[-1].reparentTo(self.renders[-1])
        self.drs[-1].setCamera(self.cameras[-1])

    def destroy(self):
        map(base.graphicsEngine.removeWindow, self.buffers)
        map(base.win.removeDisplayRegion, self.drs)
        map(lambda cam: cam.remove_node(), self.cameras + self.renders)
