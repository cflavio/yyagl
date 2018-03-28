from panda3d.core import NodePath, Camera, OrthographicLens, TextureStage


class Signs(object):
    # signs where we write supporters' names

    def __init__(self, roots, sign_cb):
        self.buffers = []
        self.drs = []  # display regions
        self.cameras = []
        self.renders = []
        self.roots = roots
        self.sign_cb = sign_cb

    def set_signs(self):
        map(lambda i_sign: self.__set_sign(*i_sign), enumerate(self.roots))

    def __set_sign(self, i, sign):
        self.__set_render_to_texture()
        self.sign_cb(self.renders[i])
        t_s = TextureStage('ts')
        t_s.setMode(TextureStage.MDecal)
        sign.set_texture(t_s, self.buffers[i].get_texture())

    def __set_render_to_texture(self):
        buf = base.win.make_texture_buffer('result buffer', 256, 256)
        self.buffers += [buf]
        self.buffers[-1].set_sort(-100)

        self.drs += [self.buffers[-1].makeDisplayRegion()]
        self.drs[-1].setSort(20)

        self.cameras += [NodePath(Camera('camera 2d'))]
        lens = OrthographicLens()
        lens.set_film_size(1, 1)
        lens.set_near_far(-1000, 1000)
        self.cameras[-1].node().set_lens(lens)

        self.renders += [NodePath('result render')]
        self.renders[-1].set_depth_test(False)
        self.renders[-1].set_depth_write(False)
        self.cameras[-1].reparent_to(self.renders[-1])
        self.drs[-1].set_camera(self.cameras[-1])

    def destroy(self):
        map(base.graphicsEngine.remove_window, self.buffers)
        if base.win:  # if you close the window during a race
            map(base.win.remove_display_region, self.drs)
        map(lambda node: node.remove_node(), self.cameras + self.renders)
