from collections import namedtuple
from random import uniform
from itertools import chain
from panda3d.core import Vec3, Vec2
from direct.showbase.InputStateGlobal import inputState
from yyagl.gameobject import Event
from yyagl.racing.race.event import NetMsgs
from yyagl.racing.weapon.rocket.rocket import Rocket
from yyagl.racing.weapon.rear_rocket.rear_rocket import RearRocket
from yyagl.racing.weapon.turbo.turbo import Turbo
from yyagl.racing.weapon.rotate_all.rotate_all import RotateAll
from yyagl.racing.weapon.mine.mine import Mine
from yyagl.computer_proxy import ComputerProxy, once_a_frame
from yyagl.engine.vec import Vec


Keys = namedtuple('Keys', 'forward rear left right fire respawn pause')
DirKeys = namedtuple('Keys', 'forward rear left right')


class InputBuilder(object):

    @staticmethod
    def create(state, joystick):
        if state == 'Results':
            return InputBuilderAi()
        elif joystick:
            return InputBuilderJoystick()
        else:
            return InputBuilderKeyboard()


class InputBuilderAi(InputBuilder):

    def build(self, ai, joystick_mgr):
        return ai.get_input()


class InputBuilderKeyboard(InputBuilder):

    def build(self, ai, joystick_mgr):
        keys = ['forward', 'rear', 'left', 'right']
        return DirKeys(*[inputState.isSet(key) for key in keys])


class InputBuilderJoystick(InputBuilder):

    def build(self, ai, joystick_mgr):
        j_x, j_y, j_a, j_b = joystick_mgr.get_joystick()
        if j_b and self.mdt.logic.weapon:
            self.on_fire()
        inp = {'forward': j_y < -.4, 'rear': j_y > .4 or j_a,
               'left': j_x < -.4, 'right': j_x > .4}
        keys = ['forward', 'rear', 'left', 'right']
        return DirKeys(*[inp[key] for key in keys])


class CarEvent(Event, ComputerProxy):

    def __init__(self, mdt, race_props):
        Event.__init__(self, mdt)
        ComputerProxy.__init__(self)
        self.eng.attach_obs(self.on_collision)
        self.props = race_props
        keys = race_props.keys
        self.label_events = [
            ('forward', keys.forward), ('left', keys.left),
            ('rear', keys.rear), ('right', keys.right)]
        watch = inputState.watchWithModifiers
        self.toks = map(lambda (lab, evt): watch(lab, evt), self.label_events)

    def start(self):
        self.eng.attach_obs(self.on_frame)

    def on_collision(self, obj, tgt_obj):
        if obj != self.mdt.gfx.nodepath.get_node():
            return
        obj_name = tgt_obj.get_name()
        if obj_name.startswith(self.props.respawn_name):
            self.process_respawn()
        if obj_name.startswith(self.props.pitstop_name):
            self.mdt.phys.apply_damage(True)
            self.mdt.gfx.apply_damage(True)
        if obj_name.startswith(self.props.goal_name):
            self._process_goal()
        obst_names = [self.props.wall_name, 'Vehicle']
        if any(obj_name.startswith(name) for name in obst_names):
            self._process_wall()
        if obj_name.startswith(self.props.bonus_name):
            self.on_bonus()
        weapons = ['Mine']
        if any(obj_name.startswith(wpn_name) for wpn_name in weapons):
            self.mdt.phys.pnode.apply_central_force((0, 0, 30000))

    def on_bonus(self):
        if self.mdt.logic.weapon:
            self.mdt.logic.weapon.destroy()
        wpn_classes = [Rocket, RearRocket, Turbo, RotateAll, Mine]
        probs = [.2, .2, .2, .1, .2]
        sel = uniform(0, sum(probs))
        for i, _ in enumerate(wpn_classes):
            if sum(probs[:i]) <= sel <= sum(probs[:i + 1]):
                wpn_cls = wpn_classes[i]
        part_path = self.props.particle_path
        wpn2path = {
            Rocket: self.props.rocket_path,
            RearRocket: self.props.rocket_path,
            Turbo: self.props.turbo_path,
            RotateAll: self.props.rotate_all_path,
            Mine: self.props.mine_path}
        path = wpn2path[wpn_cls]
        self.mdt.logic.weapon = wpn_cls(
            self.mdt, path, self.props.season_props.car_names, part_path)
        self.mdt.logic.weapon.attach_obs(self.on_rotate_all)
        return wpn_cls

    def on_rotate_all(self, sender):
        self.notify('on_rotate_all', sender)

    def _on_crash(self):
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            self.mdt.gfx.crash_sfx()

    def _process_wall(self):
        self._on_crash()

    def _process_goal(self):
        is_res = self.mdt.fsm.getCurrentOrNextState() == 'Results'
        has_started = self.mdt.logic.lap_time_start
        is_corr = self.mdt.logic.correct_lap
        if is_res or has_started and not is_corr:
            return
        self.mdt.logic.reset_waypoints()
        lap_times = self.mdt.logic.lap_times
        if self.mdt.logic.lap_time_start:
            lap_times += [self.mdt.logic.lap_time]
            self._process_nonstart_goals(1 + len(lap_times), self.mdt.laps)
        self.mdt.logic.lap_time_start = self.eng.curr_time

    def _process_nonstart_goals(self, lap_number, laps):
        pass

    def process_respawn(self):
        start_wp_n, end_wp_n = self.mdt.logic.last_wp
        self.mdt.gfx.nodepath.set_pos(start_wp_n.get_pos() + (0, 0, 2))
        wp_vec = Vec(end_wp_n.get_pos(start_wp_n).x, end_wp_n.get_pos(start_wp_n).y, 0).normalize()
        or_h = (wp_vec.xy).signed_angle_deg(Vec2(0, 1))
        self.mdt.gfx.nodepath.set_hpr((-or_h, 0, 0))
        self.mdt.gfx.nodepath.get_node().set_linear_velocity(0)
        self.mdt.gfx.nodepath.get_node().set_angular_velocity(0)

    def on_frame(self):
        _input = self._get_input()
        if self.mdt.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            _input = DirKeys(*[False for _ in range(4)])
            self.mdt.logic.reset_car()
        self.__update_contact_pos()
        self.mdt.phys.update_car_props()
        self.mdt.logic.update_waypoints()
        self.mdt.logic.update(_input)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.set_r(0)

    def __update_contact_pos(self):
        top = self.mdt.pos + (0, 0, 50)
        bottom = self.mdt.pos + (0, 0, -50)
        hits = self.eng.phys_mgr.ray_test_all(top, bottom).get_hits()
        r_n = self.props.road_name
        for hit in [hit for hit in hits if r_n in hit.get_node().get_name()]:
            self.mdt.logic.last_wp = self.mdt.logic.closest_wp()

    def destroy(self):
        map(self.eng.detach_obs, [self.on_collision, self.on_frame])
        map(lambda tok: tok.release(), self.toks)
        Event.destroy(self)
        ComputerProxy.destroy(self)


class CarPlayerEvent(CarEvent):

    def __init__(self, mdt, race_props):
        CarEvent.__init__(self, mdt, race_props)
        if not self.eng.is_runtime:
            self.accept('f11', self.mdt.gui.pars.toggle)
            self.accept('f8', self.notify, ['on_end_race'])
        state = self.mdt.fsm.getCurrentOrNextState()
        self.input_bld = InputBuilder.create(state, race_props.joystick)
        self.accept(self.props.keys.respawn, self.process_respawn)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mdt.logic.camera.update(
            self.mdt.phys.speed_ratio, self.mdt.logic.is_rolling,
            self.mdt.fsm.getCurrentOrNextState() == 'Countdown',
            self.mdt.logic.is_rotating)
        self.mdt.audio.update(self.mdt.logic.is_skidmarking,
                              self.mdt.phys.lin_vel_ratio,
                              self._get_input(),
                              self.mdt.logic.is_drifting,
                              self.mdt.phys.is_flying)

    def on_collision(self, obj, tgt_obj):
        CarEvent.on_collision(self, obj, tgt_obj)
        if obj != self.mdt.gfx.nodepath.get_node():
            return
        obj_name = tgt_obj.get_name()
        if any(obj_name.startswith(s) for s in self.props.roads_names):
            self.mdt.audio.landing_sfx.play()
        if obj_name.startswith(self.props.pitstop_name):
            self.mdt.gui.panel.apply_damage(True)
            self.mdt.gfx.set_decorator('pitstop')
            self.mdt.audio.pitstop_sfx.play()
        if 'Rocket' in obj_name:
            self.mdt.audio.rocket_hit_sfx.play()

    def on_bonus(self):
        if self.mdt.logic.weapon:
            self.mdt.gui.panel.unset_weapon()
        wpn_cls = CarEvent.on_bonus(self)
        self.accept(self.props.keys.fire, self.on_fire)
        self.mdt.gui.panel.set_weapon(
            self.props.season_props.wpn2img[wpn_cls.__name__])

    def on_fire(self):
        self.ignore(self.props.keys.fire)
        self.mdt.logic.fire()
        self.mdt.gui.panel.unset_weapon()

    def _process_wall(self):
        CarEvent._process_wall(self)
        self.mdt.audio.crash_sfx.play()

    def _process_nonstart_goals(self, lap_number, laps):
        CarEvent._process_nonstart_goals(self, lap_number, laps)
        curr_lap = min(laps, lap_number)
        self.mdt.gui.panel.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        self.mdt.audio.lap_sfx.play()

    def _process_end_goal(self):
        self.notify('on_end_race')

    def _process_goal(self):
        CarEvent._process_goal(self)
        lap_times = self.mdt.logic.lap_times
        is_best = not lap_times or min(lap_times) > self.mdt.logic.lap_time
        if self.mdt.logic.lap_time_start and (not lap_times or is_best):
            self.mdt.gui.panel.best_txt.setText(
                self.mdt.gui.panel.time_txt.getText())
        if len(lap_times) == self.mdt.laps:
            self._process_end_goal()
        # self.on_bonus()  # to test weapons

    @once_a_frame
    def _get_input(self):
        return self.input_bld.build(self.mdt.ai, self.eng.joystick_mgr)

    def destroy(self):
        evts = ['f11', 'f8', self.props.keys.fire, self.props.keys.respawn]
        map(self.ignore, evts)
        CarEvent.destroy(self)


class CarPlayerEventServer(CarPlayerEvent):

    def _process_end_goal(self):
        self.eng.server.send([NetMsgs.end_race])
        CarPlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mdt, race_props):
        CarPlayerEvent.__init__(self, mdt, race_props)
        self.last_sent = self.eng.curr_time

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mdt.pos
        hpr = self.mdt.gfx.nodepath.get_hpr()
        velocity = self.mdt.phys.vehicle.get_chassis().get_linear_velocity()
        packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
        if self.eng.curr_time - self.last_sent > .2:
            self.eng.client.send(packet)
            self.last_sent = self.eng.curr_time

    def _process_end_goal(self):
        self.eng.client.send([NetMsgs.end_race_player])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return DirKeys(False, False, False, False)


class CarAiEvent(CarEvent):

    @once_a_frame
    def _get_input(self):
        return self.mdt.ai.get_input()


class CarAiPlayerEvent(CarAiEvent, CarPlayerEvent):

    pass
