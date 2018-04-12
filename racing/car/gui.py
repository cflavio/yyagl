from panda3d.core import TextNode, LVector3f, Point2, Point3, TextNode
from yyagl.library.gui import Entry
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GuiColleague, GameObject


class CarParameter(GameObject):

    def __init__(self, attr_name, init_val, pos, val_range, callback, args=[]):
        GameObject.__init__(self)
        self.__callback = callback
        self.__args = args
        self.__lab = OnscreenText(
            text=attr_name, pos=pos, align=TextNode.ARight, fg=(1, 1, 1, 1),
            parent=base.a2dTopLeft, scale=.06)
        slider_pos = LVector3f(pos[0], 1, pos[1]) + (.3, 0, .01)
        self.__slider = Entry(
            pos=slider_pos, initialText=str(init_val),
            command=self.__set_attr, parent=base.a2dTopLeft,
            scale=.05, frameColor=(0, 0, 0, .2), text_fg=(1, 1, 1, 1))
        txt_pos = LVector3f(pos[0], pos[1], 1) + (.6, 0, 0)
        self.widgets = [self.__slider, self.__lab]
        self.toggle()

    def toggle(self):
        map(lambda wdg: (wdg.show if wdg.is_hidden() else wdg.hide)(),
            self.widgets)

    @property
    def is_visible(self):
        return any(not wdg.is_hidden() for wdg in self.widgets)

    def __set_attr(self, val):
        self.__callback(float(val), *self.__args)

    def hide(self):
        map(lambda wdg: wdg.hide(), self.widgets)

    def destroy(self):
        map(lambda wdg: wdg.destroy(), self.widgets)
        GameObject.destroy(self)


class CarParameters(GameObject):

    def __init__(self, phys, logic):
        GameObject.__init__(self)
        self.__pars = []
        pars_info = [
            ('max_speed', phys.max_speed),
            ('mass', phys.mass),
            ('steering', phys.steering),
            ('steering_clamp', phys.steering_clamp),
            ('steering_inc', phys.steering_inc),
            ('steering_dec', phys.steering_dec),
            ('suspension_stiffness', phys.suspension_stiffness),
            ('wheels_damping_relaxation', phys.wheels_damping_relaxation),
            ('wheels_damping_compression', phys.wheels_damping_compression),
            ('engine_acc_frc', phys.engine_acc_frc),
            ('engine_acc_frc_ratio', phys.engine_acc_frc_ratio),
            ('engine_dec_frc', phys.engine_dec_frc),
            ('brake_frc', phys.brake_frc)]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[0]), (.5, -.04 - i * .08),
                par_info[1], lambda val: setattr(phys, par_info[0], val))
            # refactor: par_info is a cell var
            self.__pars += [new_par]
        pars_info = [
            ('pitch_control', phys.pitch_control, phys.vehicle.setPitchControl),
            ('suspension_compression', phys.suspension_compression,
             phys.vehicle.getTuning().setSuspensionCompression),
            ('suspension_damping', phys.suspension_damping,
             phys.vehicle.getTuning().setSuspensionDamping)]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[0]), (.5, -.84 - i * .08),
                par_info[1], par_info[2])
            self.__pars += [new_par]
        pars_info = [
            ('max_suspension_force', phys.max_suspension_force, 'setMaxSuspensionForce'),
            ('max_suspension_travel_cm', phys.max_suspension_travel_cm,
             'setMaxSuspensionTravelCm'),
            ('skid_info', phys.skid_info, 'setSkidInfo'),
            ('friction_slip', phys.friction_slip, 'setFrictionSlip'),
            ('roll_influence', phys.roll_influence, 'setRollInfluence')
            ]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[0]), (.5, -1.08 - i * .08),
                par_info[1],
                lambda val: map(lambda whl: getattr(whl, par_info[2])(val),
                                phys.vehicle.get_wheels()))
            self.__pars += [new_par]
        for i, coord in enumerate(['x', 'y', 'z']):
            def set_cam(val, j):
                vec = logic.camera.cam_vec
                logic.camera.cam_vec = (
                    val if j == 0 else vec[0],
                    val if j == 1 else vec[1],
                    val if j == 2 else vec[2])
            new_par = CarParameter(
                'camera_' + coord, logic.camera.cam_vec[i],
                (.5, -1.72 - i * .08), (-1, 1), set_cam, [i])
            self.__pars += [new_par]

    def toggle(self):
        map(lambda par: par.toggle(), self.__pars)
        is_visible = self.__pars[0].is_visible
        (self.eng.show_cursor if is_visible else self.eng.hide_cursor)()

    def hide(self):
        map(lambda wdg: wdg.hide(), self.__pars)

    def destroy(self):
        map(lambda wdg: wdg.destroy(), self.__pars)
        GameObject.destroy(self)


class CarPanel(GameObject):

    def __init__(self, race_props):
        GameObject.__init__(self)
        self.race_props = race_props
        sprops = self.race_props.season_props
        menu_args = sprops.gameprops.menu_args
        pars = {'scale': .065, 'parent': base.a2dTopRight,
                'fg': menu_args.text_active, 'align': TextNode.A_left,
                'font': self.eng.font_mgr.load_font(sprops.font)}
        self.speed_txt = OnscreenText(pos=(-.24, -.1), **pars)
        lap_str = '1/' + str(self.race_props.laps)
        self.lap_txt = OnscreenText(text=lap_str, pos=(-.24, -.2), **pars)
        self.time_txt = OnscreenText(pos=(-.24, -.3), **pars)
        self.best_txt = OnscreenText(pos=(-.24, -.4), **pars)
        self.ranking_txt = OnscreenText(pos=(-.24, -.5), **pars)
        self.damages_txt = OnscreenText(pos=(-.24, -.6), **pars)
        self.damages_txt['text'] = '-'
        self.damages_txt['fg'] = menu_args.text_normal
        pars = {'scale': .05, 'parent': pars['parent'],
                'fg': menu_args.text_normal,
                'align': TextNode.A_right, 'font': pars['font']}
        self.speed_lab = OnscreenText(_('speed:'), pos=(-.3, -.1), **pars)
        self.lap_lab = OnscreenText(
            text=_('lap:'), pos=(-.3, -.2), **pars)
        self.time_lab = OnscreenText(_('time:'), pos=(-.3, -.3), **pars)
        self.best_lab = OnscreenText(_('best lap:'), pos=(-.3, -.4), **pars)
        self.ranking_lab = OnscreenText(_('ranking:'), pos=(-.3, -.5), **pars)
        self.damages_lab = OnscreenText(_('damages:'), pos=(-.3, -.6), **pars)
        self.weapon_lab = OnscreenText(_('weapon:'), pos=(-.3, -.7), **pars)
        self.weapon_img = None
        self.forward_img = OnscreenImage(
            'assets/images/gui/direction.txo',
            scale=.15, parent=base.a2dTopCenter, pos=(0, 1, -.2))
        self.forward_img.set_transparency(True)
        self.forward_img.hide()

    def set_weapon(self, wpn):
        self.weapon_img = OnscreenImage(
            'assets/images/weapons/%s.txo' % wpn,
            scale=.05, parent=base.a2dTopRight, pos=(-.2, 1, -.69))
        self.weapon_img.set_transparency(True)

    def unset_weapon(self):
        self.weapon_img.destroy()

    def show_forward(self):
        self.forward_img.show()

    def hide_forward(self):
        self.forward_img.hide()

    def apply_damage(self, reset=False):
        col = self.race_props.season_props.gameprops.menu_args.text_normal
        if reset:
            self.damages_txt['text'] = '-'
            self.damages_txt['fg'] = col
        else:
            if self.damages_txt['text'] == '-':
                self.damages_txt['text'] = _('low')
                yellow = (col[0], col[1] - .25, col[2] - .5, col[3])
                self.damages_txt['fg'] = yellow
            elif self.damages_txt['text'] == _('low'):
                self.damages_txt['text'] = _('hi')
                red = (col[0], col[1] - .5, col[2] - .5, col[3])
                self.damages_txt['fg'] = red

    def hide(self):
        labels = [
            self.speed_txt, self.time_txt, self.lap_txt, self.best_txt,
            self.speed_lab, self.time_lab, self.lap_lab, self.best_lab,
            self.damages_txt, self.damages_lab, self.ranking_txt,
            self.ranking_lab, self.weapon_lab]
        map(lambda wdg: wdg.hide(), labels)
        if self.weapon_img and not self.weapon_img.is_empty():
            self.weapon_img.hide()
        self.forward_img.hide()

    def destroy(self):
        labels = [
            self.speed_txt, self.time_txt, self.lap_txt, self.best_txt,
            self.speed_lab, self.time_lab, self.lap_lab, self.best_lab,
            self.damages_txt, self.damages_lab, self.ranking_txt,
            self.ranking_lab, self.weapon_lab]
        map(lambda wdg: wdg.destroy(), labels)
        if self.weapon_img and not self.weapon_img.is_empty():
            self.weapon_img.destroy()
        self.forward_img.destroy()


class CarAIPanel(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.curr_logic = ''
        self.curr_wp = ''
        self.curr_car_dot_traj = ''
        self.curr_obsts = []
        self.curr_obsts_back = []
        self.curr_input = None
        self.wp_txt = OnscreenText(text='', pos=(-1.74, .5), scale=.06, fg=(1, 1, 1, 1), align=TextNode.A_left)

    def update(self):
        txt = 'current logic: ' + self.curr_logic.split('AiLogic')[0]
        txt += '\ncurrent wp: ' + self.curr_wp
        txt += '\ncar dot traj: %s' % self.curr_car_dot_traj
        txt += '\nobst center: %s (%s)' % (self.curr_obsts[0].name, round(self.curr_obsts[0].dist, 2))
        txt += '\nobst left: %s (%s)' % (self.curr_obsts[1].name, round(self.curr_obsts[1].dist, 2))
        txt += '\nobst right: %s (%s)' % (self.curr_obsts[2].name, round(self.curr_obsts[2].dist, 2))
        txt += '\nobst center back: %s (%s)' % (self.curr_obsts_back[0].name, round(self.curr_obsts_back[0].dist, 2))
        txt += '\nobst left back: %s (%s)' % (self.curr_obsts_back[1].name, round(self.curr_obsts_back[1].dist, 2))
        txt += '\nobst right back: %s (%s)' % (self.curr_obsts_back[2].name, round(self.curr_obsts_back[2].dist, 2))
        txt += '\nforward: %s' % self.curr_input.forward
        txt += '\nbrake: %s' % self.curr_input.rear
        txt += '\nleft: %s' % self.curr_input.left
        txt += '\nright: %s' % self.curr_input.right
        self.wp_txt['text'] = txt

    def hide(self): self.wp_txt.hide()


class CarGui(GuiColleague):

    def apply_damage(self, reset=False): pass

    def hide(self): pass


class CarPlayerGui(CarGui):

    def __init__(self, mediator, car_props):
        self.race_props = car_props
        CarGui.__init__(self, mediator)
        self.pars = CarParameters(mediator.phys, mediator.logic)
        self.panel = CarPanel(car_props)
        self.ai_panel = CarAIPanel()

    def upd_ranking(self, ranking):
        r_i = ranking.index(self.mediator.name) + 1
        self.panel.ranking_txt.setText(str(r_i) + "'")

    def upd_ai(self):
        self.ai_panel.update()

    def apply_damage(self, reset=False):
        self.panel.apply_damage(reset)

    def show_forward(self):
        self.panel.show_forward()

    def hide_forward(self):
        self.panel.hide_forward()

    def hide(self):
        CarGui.hide(self)
        self.pars.hide()
        self.panel.hide()
        self.ai_panel.hide()

    def destroy(self):
        map(lambda wdg: wdg.destroy(), [self.pars, self.panel, self.ai_panel])
        GuiColleague.destroy(self)


class CarNetworkGui(CarGui):

    def __init__(self, mediator, car_props):
        self.race_props = car_props
        CarGui.__init__(self, mediator)
        for drv in self.race_props.drivers:
            if drv.dprops.car_name == self.mediator.name:
                name = drv.dprops.info.name
        sprops = self.race_props.season_props
        menu_args = sprops.gameprops.menu_args
        pars = {'scale': .04, 'fg': menu_args.text_normal,
                'font': self.eng.font_mgr.load_font(sprops.font)}
        if '@' in name: name = name[:name.index('@')]
        self.name_txt = OnscreenText(name, **pars)
        self.eng.attach_obs(self.on_frame)

    def __2d_pos(self, node):
        p3d = base.cam.get_relative_point(node.node, Point3(0, 0, 0))
        p2d = Point2()
        return p2d if base.camLens.project(p3d, p2d) else None

    def on_frame(self):
        pos = self.__2d_pos(self.mediator.gfx.nodepath)
        if pos:
            self.name_txt.show()
            self.name_txt.set_pos((pos[0], 1, pos[1] + .16))
        else:
            self.name_txt.hide()

    def hide(self):
        CarGui.hide(self)
        self.name_txt.hide()

    def destroy(self):
        self.name_txt.destroy()
        self.eng.detach_obs(self.on_frame)
        CarGui.destroy(self)
