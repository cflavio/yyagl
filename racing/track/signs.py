from random import shuffle
from panda3d.core import NodePath, Camera, OrthographicLens, TextureStage
from direct.gui.OnscreenText import OnscreenText


class Signs(object):

    def __init__(self, model, sign_name, thanks):
        self.buffers = []
        self.drs = []
        self.cameras = []
        self.renders = []
        self.model = model
        self.sign_name = sign_name
        self.thanks = thanks

    def set_signs(self):
        signs = self.model.findAllMatches('**/%s*' % self.sign_name)
        for i, sign in enumerate(signs):
            self.__set_render_to_texture()
            shuffle(self.thanks)
            text = '\n\n'.join(self.thanks[:3])
            txt = OnscreenText(text, parent=self.renders[i], scale=.2,
                               fg=(0, 0, 0, 1), pos=(.245, 0))
            bounds = lambda: txt.getTightBounds()
            while bounds()[1][0] - bounds()[0][0] > .48:
                txt.setScale(txt.getScale()[0] - .01, txt.getScale()[0] - .01)
            height = txt.getTightBounds()[1][2] - txt.getTightBounds()[0][2]
            txt.setZ(.06 + height / 2)
            ts = TextureStage('ts')
            ts.setMode(TextureStage.MDecal)
            sign.setTexture(ts, self.buffers[i].getTexture())

    def __set_render_to_texture(self):
        self.buffers += [base.win.makeTextureBuffer('result buffer', 512, 512)]
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
