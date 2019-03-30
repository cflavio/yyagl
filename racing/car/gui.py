from panda3d.core import TextNode, LVector3f, Point2, Point3, TextNode
from yyagl.lib.gui import Entry
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from yyagl.gameobject import GuiColleague, GameObject
from yyagl.engine.gui.circle import Circle


class CarParameter(GameObject):

    def __init__(self, attr_name, init_val, pos, val_range, callback, args=[]):
        GameObject.__init__(self)
        self.__callback = callback
        self.__args = args
        self.__lab = OnscreenText(
            text=attr_name, pos=pos, align=TextNode.ARight, fg=(1, 1, 1, 1),
            parent=base.a2dTopLeft, scale=.046)
        slider_pos = LVector3f(pos[0], 1, pos[1]) + (.05, 0, .01)
        self.__slider = Entry(
            pos=slider_pos, initial_text=str(init_val),
            cmd=self.__set_attr, parent=base.a2dTopLeft,
            scale=.05, frame_col=(0, 0, 0, .2), text_fg=(1, 1, 1, 1))
        txt_pos = LVector3f(pos[0], pos[1], 1) + (.6, 0, 0)
        self.widgets = [self.__slider, self.__lab]
        self.toggle()

    def toggle(self):
        #map(lambda wdg: (wdg.show if wdg.hidden else wdg.hide)(),
        #    self.widgets)
        # temporary hack: we're using non-dip widgets, they've is_hidden in
        # place of hidden, remove this when this is refactored
        for wdg in self.widgets:
            if hasattr(wdg, 'hidden'): (wdg.show if wdg.hidden else wdg.hide)()
            else: (wdg.show if wdg.is_hidden() else wdg.hide)()

    @property
    def is_visible(self):
        return any(not wdg.hidden for wdg in self.widgets)

    def __set_attr(self, val):
        try: self.__callback(float(val), *self.__args)
        except ValueError:
            self.__callback(eval(val), *self.__args)

    def hide(self):
        list(map(lambda wdg: wdg.hide(), self.widgets))

    def destroy(self):
        list(map(lambda wdg: wdg.destroy(), self.widgets))
        GameObject.destroy(self)


class EagerCaller(object):

    def __init__(self, meth, *args):
        self.meth = meth
        self.args = args

    def call(self, arg):
        self.meth(arg, *self.args)


class CarParameters(GameObject):

    def __init__(self, phys, logic):
        GameObject.__init__(self)
        self.__pars = []
        pars_info = [
            ('maxSpeed', phys.max_speed, 'max_speed'),
            ('steer', phys.steering, 'steering'),
            ('steerClamp', phys.steering_clamp, 'steering_clamp'),
            ('steerInc', phys.steering_inc, 'steering_inc'),
            ('steerDec', phys.steering_dec, 'steering_dec'),
            ('suspStiff', phys.suspension_stiffness, 'suspension_stiffness'),
            ('whlDampRelax', phys.wheels_damping_relaxation, 'wheels_damping_relaxation'),
            ('whlDampCompr', phys.wheels_damping_compression, 'wheels_damping_compression'),
            ('engAccFrc', phys.engine_acc_frc, 'engine_acc_frc'),
            ('engAccFrcRatio', phys.engine_acc_frc_ratio, 'engine_acc_frc_ratio'),
            ('engDecFrc', phys.engine_dec_frc, 'engine_dec_frc'),
            ('brakeFrc', phys.brake_frc, 'brake_frc'),
            ('brakeRatio', phys.brake_ratio, 'brake_ratio'),
            ('engBrakeFrc', phys.eng_brk_frc, 'eng_brk_frc'),
            ('rollInfl', phys.roll_influence, 'roll_influence'),
            ('fricSlip', phys.friction_slip, 'friction_slip'),
            ('fricSlipRear', phys.friction_slip_rear, 'friction_slip_rear')]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[2]), (.4, -.04 - i * .08),
                par_info[1],
                EagerCaller(self.assign_val, phys, par_info[2]).call)
            # refactor: par_info is a cell var
            self.__pars += [new_par]
        pars_info = [
            ('mass', phys.mass, phys.pnode.set_mass, 'mass'),
            ('pitchCtrl', phys.pitch_control, phys.vehicle.setPitchControl, 'pitch_control'),
            ('suspCompr', phys.suspension_compression,
             phys.vehicle.getTuning().setSuspensionCompression, 'suspension_compression'),
            ('suspDamp', phys.suspension_damping,
             phys.vehicle.getTuning().setSuspensionDamping, 'suspension_damping')]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[3]), (.4, -1.64 - i * .08),
                par_info[1], par_info[2])
            self.__pars += [new_par]
        pars_info = [
            ('maxSuspFrc', phys.max_suspension_force, 'setMaxSuspensionForce', 'max_suspension_force'),
            ('maxSuspTravelCm', phys.max_suspension_travel_cm,
             'setMaxSuspensionTravelCm', 'max_suspension_travel_cm'),
            ('skidInfo', phys.skid_info, 'setSkidInfo', 'skid_info')]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], getattr(phys, par_info[3]), (.4, -1.4 - i * .08),
                par_info[1],
                EagerCaller(self.assign_val_whl, phys, par_info[2]).call)
            self.__pars += [new_par]
        pars_info = [
            ('camDistMin', logic.camera.dist_min, 'dist_min'),
            ('camDistMax', logic.camera.dist_max, 'dist_max'),
            ('camLookMin', logic.camera.look_dist_min, 'look_dist_min'),
            ('camLookMax', logic.camera.look_dist_max, 'look_dist_max'),
            ('camOverwrite', logic.camera.overwrite, 'overwrite')]
        for i, par_info in enumerate(pars_info):
            new_par = CarParameter(
                par_info[0], par_info[1],
                (2.8, -.8 - .08 * i), (-1, 1), EagerCaller(self.assign_val, logic.camera, par_info[2]).call)
            self.__pars += [new_par]

    def assign_val(self, val, phys, field): setattr(phys, field, val)

    def assign_val_whl(self, val, phys, field):
        list(map(lambda whl: getattr(whl, field)(val), phys.vehicle.get_wheels()))

    def toggle(self):
        list(map(lambda par: par.toggle(), self.__pars))
        is_visible = self.__pars[0].is_visible
        (self.eng.show_cursor if is_visible else self.eng.hide_cursor)()

    def hide(self): list(map(lambda wdg: wdg.hide(), self.__pars))

    def destroy(self):
        list(map(lambda wdg: wdg.destroy(), self.__pars))
        GameObject.destroy(self)


class CarPanel(GameObject):

    def __init__(self, race_props, player_idx, ncars):
        GameObject.__init__(self)
        self.race_props = race_props
        self.player_idx = player_idx
        self.ncars = ncars
        sprops = self.race_props.season_props
        menu_props = sprops.gameprops.menu_props
        if ncars == 1:
            parent_tr = base.a2dTopRight
        elif ncars == 2:
            if self.player_idx == 0: parent_tr = base.a2dTopCenter
            else: parent_tr = base.a2dTopRight
        elif ncars == 3:
            if self.player_idx == 0: parent_tr = base.a2dTopRight
            elif self.player_idx == 1: parent_tr = base.aspect2d
            else: parent_tr = base.a2dRightCenter
        elif ncars == 4:
            if self.player_idx == 0: parent_tr = base.a2dTopCenter
            elif self.player_idx == 1: parent_tr = base.a2dTopRight
            elif self.player_idx == 2: parent_tr = base.aspect2d
            else: parent_tr = base.a2dRightCenter
        if ncars == 1:
            parent_tl = base.a2dTopLeft
        elif ncars == 2:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            else: parent_tl = base.a2dTopCenter
        elif ncars == 3:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            elif self.player_idx == 1: parent_tl = base.a2dLeftCenter
            else: parent_tl = base.aspect2d
        elif ncars == 4:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            elif self.player_idx == 1: parent_tl = base.a2dTopCenter
            elif self.player_idx == 2: parent_tl = base.a2dLeftCenter
            else: parent_tl = base.aspect2d
        if ncars == 1:
            parent_bl = base.a2dBottomLeft
        elif ncars == 2:
            if self.player_idx == 0: parent_bl = base.a2dBottomLeft
            else: parent_bl = base.a2dBottomCenter
        elif ncars == 3:
            if self.player_idx == 0: parent_bl = base.a2dLeftCenter
            elif self.player_idx == 1: parent_bl = base.a2dBottomLeft
            else: parent_bl = base.a2dBottomCenter
        elif ncars == 4:
            if self.player_idx == 0: parent_bl = base.a2dLeftCenter
            elif self.player_idx == 1: parent_bl = base.aspect2d
            elif self.player_idx == 2: parent_bl = base.a2dBottomLeft
            else: parent_bl = base.a2dBottomCenter
        if ncars == 1: parent_t = base.a2dTopCenter
        elif ncars == 2:
            if self.player_idx == 0: parent_t = base.a2dTopQuarter
            else: parent_t = base.a2dTopThirdQuarter
        elif ncars == 3:
            if self.player_idx == 0: parent_t = base.a2dTop
            elif self.player_idx == 1: parent_t = base.a2dCenterQuarter
            else: parent_t = base.a2dCenterThirdQuarter
        elif ncars == 4:
            if self.player_idx == 0: parent_t = base.a2dTopQuarter
            elif self.player_idx == 1: parent_t = base.a2dTopThirdQuarter
            elif self.player_idx == 2: parent_t = base.a2dCenterQuarter
            else: parent_t = base.a2dCenterThirdQuarter
        if ncars == 1: parent_b = base.a2dBottomCenter
        elif ncars == 2:
            if self.player_idx == 0: parent_b = base.a2dBottomQuarter
            else: parent_b = base.a2dBottomThirdQuarter
        elif ncars == 3:
            if self.player_idx == 0: parent_b = base.aspect2d
            elif self.player_idx == 1: parent_b = base.a2dBottomQuarter
            else: parent_b = base.a2dBottomThirdQuarter
        elif ncars == 4:
            if self.player_idx == 0: parent_b = base.a2dCenterQuarter
            elif self.player_idx == 1: parent_b = base.a2dCenterThirdQuarter
            elif self.player_idx == 2: parent_b = base.a2dBottomQuarter
            else: parent_b = base.a2dBottomThirdQuarter
        yellow_scale = .065 if ncars == 1 else .042
        white_scale = .05 if ncars == 1 else .038
        damages_img_scale = (.12, 1, .12) if ncars == 1 else (.08, 1, .08)
        self.__weap_scale = .12 if ncars == 1 else .08
        txt_x = -.24 if ncars == 1 else -.18
        lab_x = -.3 if ncars == 1 else -.24
        offset_z = .1 if ncars == 1 else .08
        top_z = -.1
        damages_txt_pos = (.3, .1) if ncars == 1 else (.24, .06)
        damages_img_pos = (.46, 1, .12) if ncars == 1 else (.36, 1, .07)
        weapon_txt_pos = (.18, -.08) if ncars == 1 else (.14, -.08)
        self.__weapon_img_pos = (.18, 1, -.24) if ncars == 1 else (.14, 1, -.18)
        fwd_img_pos = (0, 1, -.2) if ncars == 1 else (0, 1, -.16)
        fwd_img_scale = .15 if ncars == 1 else .12
        pars = {'scale': yellow_scale, 'parent': parent_tr,
                'fg': menu_props.text_active_col, 'align': TextNode.A_left,
                'font': self.eng.font_mgr.load_font(sprops.font)}
        #self.glass_tl = OnscreenImage(
        #    'assets/images/gui/topleft.txo',
        #    scale=(.23, 1, .24), parent=parent_tl, pos=(.22, 1, -.23))
        #self.glass_tl.set_transparency(True)
        #self.glass_tr = OnscreenImage(
        #    'assets/images/gui/topright.txo',
        #    scale=(.36, 1, .36), parent=parent_tr, pos=(-.35, 1, -.35))
        #self.glass_tr.set_transparency(True)
        #self.glass_t = OnscreenImage(
        #    'assets/images/gui/top.txo',
        #    scale=(.24, 1, .22), parent=parent_t, pos=(0, 1, -.21))
        #self.glass_t.set_transparency(True)
        #self.glass_bl = OnscreenImage(
        #    'assets/images/gui/bottomleft.txo',
        #    scale=(.36, 1, .16), parent=parent_bl, pos=(.35, 1, .15))
        #self.glass_bl.set_transparency(True)
        #self.glass_br = OnscreenImage(
        #    'assets/images/gui/bottomright.txo',
        #    scale=(.26, 1, .26), parent=base.a2dBottomRight, pos=(-.25, 1, .25))
        #self.glass_br.set_transparency(True)
        #self.glass_b = OnscreenImage(
        #    'assets/images/gui/bottom.txo',
        #    scale=(1.02, 1, .26), parent=parent_b, pos=(0, 1, .25))
        #self.glass_b.set_transparency(True)
        #self.glass_tl.hide()
        #self.glass_t.hide()
        #self.glass_b.hide()
        self.speed_txt = OnscreenText(pos=(txt_x + .06, top_z), **pars)
        self.speed_txt['align'] = TextNode.A_center
        self.speed_c = Circle(
            size=.1, pos=(txt_x + .06, top_z), parent=parent_tr, ray=.4,
            thickness=.05, col_start=(.9, .6, .1, 1), col_end=(.2, .8, .2, 1))
        lap_str = '1/' + str(self.race_props.laps)
        self.lap_txt = OnscreenText(text=lap_str, pos=(txt_x, top_z - offset_z), **pars)
        self.time_txt = OnscreenText(pos=(txt_x, top_z - offset_z * 4), **pars)
        self.best_txt = OnscreenText(pos=(txt_x, top_z - offset_z * 5), **pars)
        self.ranking_txt = OnscreenText(pos=(txt_x, top_z - offset_z * 2), **pars)
        self.damages_img = OnscreenImage(
            'assets/images/gui/car_icon.txo',
            scale=damages_img_scale, parent=parent_bl, pos=damages_img_pos)
        self.damages_img.set_transparency(True)
        self.damages_img.set_color_scale(menu_props.text_normal_col)
        self.damages_img.set_r(90)
        pars = {'scale': white_scale, 'parent': pars['parent'],
                'fg': menu_props.text_normal_col,
                'align': TextNode.A_right, 'font': pars['font']}
        self.speed_lab = OnscreenText(_('speed:'), pos=(lab_x, top_z), **pars)
        self.lap_lab = OnscreenText(
            text=_('lap:'), pos=(lab_x, top_z - offset_z), **pars)
        self.time_lab = OnscreenText(_('time:'), pos=(lab_x, top_z - offset_z * 4), **pars)
        self.best_lab = OnscreenText(_('best lap:'), pos=(lab_x, top_z - offset_z * 5), **pars)
        self.ranking_lab = OnscreenText(_('ranking:'), pos=(lab_x, top_z - offset_z * 2), **pars)
        self.damages_lab = OnscreenText(_('damages:'), pos=damages_txt_pos, **pars)
        self.damages_lab.reparent_to(parent_bl)
        self.weapon_lab = OnscreenText(
            _('weapon'), pos=weapon_txt_pos, scale=white_scale, parent=parent_tl,
            fg=menu_props.text_normal_col, font=self.eng.font_mgr.load_font(sprops.font))
        self.weapon_img = None
        if ncars == 1: parent = base.a2dTopCenter
        elif ncars == 2:
            if player_idx == 0: parent = base.a2dTopQuarter
            else: parent = base.a2dTopThirdQuarter
        elif ncars == 3:
            if player_idx == 0: parent = base.a2dTopCenter
            elif player_idx == 0: parent = base.a2dCenterQuarter
            else: parent = base.a2dCenterThirdQuarter
        elif ncars == 4:
            if player_idx == 0: parent = base.a2dTopQuarter
            elif player_idx == 1: parent = base.a2dTopThirdQuarter
            elif player_idx == 2: parent = base.a2dCenterQuarter
            else: parent = base.a2dCenterThirdQuarter
        self.forward_img = OnscreenImage(
            'assets/images/gui/direction.txo',
            scale=fwd_img_scale, parent=parent, pos=fwd_img_pos)
        self.forward_img.set_transparency(True)
        self.forward_img.hide()

    def __close_vec(self, vec1, vec2):
        return all(abs(b - a) < .01 for a, b in zip(vec1, vec2))

    def enter_waiting(self):
        pass
        #if self.ncars == 1: parent = base.aspect2d
        #elif self.ncars == 2:
        #    if self.player_idx == 0: parent = base.a2dCenterQuarter
        #    else: parent = base.a2dCenterThirdQuarter
        #elif self.ncars == 3:
        #    if self.player_idx == 0: parent = base.a2dQuarterCenter
        #    elif self.player_idx == 1: parent = base.a2dThirdQuarterQuarter
        #    else: parent = base.a2dThirdQuarterThirdQuarter
        #elif self.ncars == 4:
        #    if self.player_idx == 0: parent = base.a2dQuarterQuarter
        #    elif self.player_idx == 1: parent = base.a2dQuarterThirdQuarter
        #    elif self.player_idx == 2: parent = base.a2dThirdQuarterQuarter
        #    else: parent = base.a2dThirdQuarterThirdQuarter
        #menu_props = self.race_props.season_props.gameprops.menu_props
        #pars = {'scale': .065, 'parent': parent,
        #        'fg': menu_props.text_normal_col,
        #        'font': self.eng.font_mgr.load_font(self.race_props.season_props.font)}

    def exit_waiting(self): pass

    def set_weapon(self, wpn):
        #self.glass_tl.show()
        self.weapon_lab.show()
        ncars = len(self.race_props.season_props.player_car_names)
        if ncars == 1:
            parent_tl = base.a2dTopLeft
        elif ncars == 2:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            else: parent_tl = base.a2dTopCenter
        elif ncars == 3:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            elif self.player_idx == 1: parent_tl = base.a2dLeftCenter
            else: parent_tl = base.aspect2d
        elif ncars == 4:
            if self.player_idx == 0: parent_tl = base.a2dTopLeft
            elif self.player_idx == 1: parent_tl = base.a2dTopCenter
            elif self.player_idx == 2: parent_tl = base.a2dLeftCenter
            else: parent_tl = base.aspect2d
        self.weapon_img = OnscreenImage(
            'assets/images/weapons/%s.txo' % wpn,
            scale=self.__weap_scale, parent=parent_tl, pos=self.__weapon_img_pos)
        self.weapon_img.set_transparency(True)

    def unset_weapon(self):
        #self.glass_tl.hide()
        self.weapon_lab.hide()
        self.weapon_img.destroy()

    def show_forward(self):
        #self.glass_t.show()
        self.forward_img.show()

    def set_forward_angle(self, angle):
        curr_angle = self.forward_img.get_r()
        curr_incr = globalClock.getDt() * 30
        if abs(curr_angle - angle) < curr_incr:
            tgt_val = angle
        else:
            sign = 1 if angle > curr_angle else -1
            tgt_val = curr_angle + curr_incr * sign
        self.forward_img.set_r(tgt_val)

    def hide_forward(self):
        #self.glass_t.hide()
        self.forward_img.hide()

    def apply_damage(self, reset=False):
        col = self.race_props.season_props.gameprops.menu_props.text_normal_col
        if reset:
            self.damages_img.set_color_scale(col)
        else:
            yellow = (col[0], col[1] - .25, col[2] - .5, col[3])
            if self.__close_vec(self.damages_img.get_color_scale(), col):
                self.damages_img.set_color_scale(yellow)
            elif self.__close_vec(self.damages_img.get_color_scale(), yellow):
                red = (col[0], col[1] - .5, col[2] - .5, col[3])
                self.damages_img.set_color_scale(red)

    def hide(self):
        labels = [
            self.speed_txt, self.speed_c, self.time_txt, self.lap_txt,
            self.best_txt, self.speed_lab, self.time_lab, self.lap_lab,
            self.best_lab, self.damages_img, self.damages_lab,
            self.ranking_txt, self.ranking_lab, self.weapon_lab,
            #self.glass_tl, self.glass_tr, self.glass_t,
            #self.glass_bl, self.glass_br, self.glass_b
            ]
        list(map(lambda wdg: wdg.hide(), labels))
        if self.weapon_img and not self.weapon_img.is_empty():
            self.weapon_img.hide()
        self.forward_img.hide()

    def destroy(self):
        labels = [
            self.speed_txt, self.speed_c, self.time_txt, self.lap_txt,
            self.best_txt, self.speed_lab, self.time_lab, self.lap_lab,
            self.best_lab, self.damages_img, self.damages_lab,
            self.ranking_txt, self.ranking_lab, self.weapon_lab,
            #self.glass_tl, self.glass_tr, self.glass_t,
            #self.glass_bl, self.glass_br, self.glass_b
            ]
        list(map(lambda wdg: wdg.destroy(), labels))
        if self.weapon_img and not self.weapon_img.is_empty():
            self.weapon_img.destroy()
        self.forward_img.destroy()


class CarMultiPlayerPanel(CarPanel):

    def enter_waiting(self):
        CarPanel.enter_waiting(self)
        self.wait_lab = OnscreenText(_('waiting for the other players'),
                                     pos=(0, 0), **pars)

    def exit_waiting(self):
        CarPanel.exit_waiting(self)
        self.wait_lab.destroy()


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

    panel_cls = CarPanel

    def __init__(self, mediator, car_props):
        self.race_props = car_props
        ncars = self.ncars
        CarGui.__init__(self, mediator)
        self.pars = CarParameters(mediator.phys, mediator.logic)
        self.panel = self.panel_cls(car_props, mediator.player_car_idx, ncars)
        self.ai_panel = CarAIPanel()
        if ncars == 1: parent = base.a2dBottomCenter
        elif ncars == 2:
            if mediator.player_car_idx == 0: parent = base.a2dBottomQuarter
            else: parent = base.a2dBottomThirdQuarter
        elif ncars == 3:
            if mediator.player_car_idx == 0: parent = base.aspect2d
            elif mediator.player_car_idx == 1: parent = base.a2dBottomQuarter
            else: parent = base.a2dBottomThirdQuarter
        elif ncars == 4:
            if mediator.player_car_idx == 0: parent = base.a2dCenterQuarter
            elif mediator.player_car_idx == 1: parent = base.a2dCenterThirdQuarter
            elif mediator.player_car_idx == 2: parent = base.a2dBottomQuarter
            else: parent = base.a2dBottomThirdQuarter
        way_txt_pos = (0, .1) if ncars == 1 else (0, .04)
        way_txt_scale = .1 if ncars == 1 else .06
        way_img_pos = (0, 1, .3) if ncars == 1 else (0, 1, .16)
        way_img_scale = .12 if ncars == 1 else .06
        self.way_txt = OnscreenText(
            '', pos=way_txt_pos, scale=way_txt_scale,
            fg=self.race_props.season_props.gameprops.menu_props.text_err_col,
            parent=parent,
            font=self.eng.font_mgr.load_font(self.race_props.season_props.font))
        self.way_img = OnscreenImage(
            'assets/images/gui/arrow_circle.txo', scale=way_img_scale,
            parent=parent, pos=way_img_pos)
        self.way_img.set_transparency(True)
        self.way_img.hide()

    @property
    def ncars(self): return len(self.race_props.season_props.player_car_names)

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

    def on_wrong_way(self, way_str):
        if way_str:
            #self.panel.glass_b.show()
            self.way_txt.setText(way_str)
            self.way_img.show()
        elif not self.mediator.logic.is_moving or self.mediator.logic.fly_time > 10:
            #self.panel.glass_b.show()
            keys = self.race_props.keys.players_keys[self.mediator.player_car_idx]
            txt = _('press %s to respawn') % self.eng.event.key2desc(keys.respawn)
            self.way_txt.setText(txt)
            self.way_img.hide()
        else:
            #self.panel.glass_b.hide()
            self.way_txt.setText('')
            self.way_img.hide()

    def destroy(self):
        list(map(lambda wdg: wdg.destroy(), [self.pars, self.panel, self.ai_panel]))
        self.way_txt.destroy()
        self.way_img.destroy()
        GuiColleague.destroy(self)


class CarPlayerLocalMPGui(CarPlayerGui):

    panel_cls = CarMultiPlayerPanel

    @property
    def ncars(self):
        return len(self.race_props.season_props.player_car_names)


class CarPlayerMPGui(CarPlayerGui):

    panel_cls = CarMultiPlayerPanel


class CarNetworkGui(CarGui):

    def __init__(self, mediator, car_props):
        self.race_props = car_props
        CarGui.__init__(self, mediator)
        for drv in self.race_props.drivers:
            if drv.dprops.car_name == self.mediator.name:
                name = drv.dprops.info.name
                break
        sprops = self.race_props.season_props
        menu_props = sprops.gameprops.menu_props
        pars = {'scale': .04, 'fg': menu_props.text_normal_col,
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
