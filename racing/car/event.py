from random import choice
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
from yyagl.engine.joystick import JoystickMgr
from yyagl.engine.phys import PhysMgr
from yyagl.engine.network.client import Client
from yyagl.engine.network.server import Server


class InputDctBuilder(object):  # maybe a visitor?

    @staticmethod
    def build(state, joystick):
        if state == 'Results':
            return InputDctBuilderAi()
        elif joystick:
            return InputDctBuilderJoystick()
        else:
            return InputDctBuilderKeyboard()


class InputDctBuilderAi(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        return ai.get_input()


class InputDctBuilderKeyboard(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        keys = ['forward', 'left', 'reverse', 'right']
        return {key: inputState.isSet(key) for key in keys}


class InputDctBuilderJoystick(InputDctBuilder):

    def build_dct(self, ai, has_weapon):
        j_x, j_y, j_a, j_b = JoystickMgr().get_joystick()
        if j_b and has_weapon:
            self.on_fire()
        return {'forward': j_y < -.4, 'reverse': j_y > .4 or j_a,
                'left': j_x < -.4, 'right': j_x > .4}


class CarEvent(Event):

    def __init__(self, mdt, carevent_props):
        Event.__init__(self, mdt)
        eng.attach_obs(self.on_collision)
        self.props = carevent_props
        keys = carevent_props.keys
        self.label_events = [
            ('forward', keys['forward']), ('left', keys['left']),
            ('reverse', keys['rear']), ('right', keys['right'])]
        watch = inputState.watchWithModifiers
        self.toks = map(lambda (lab, evt): watch(lab, evt), self.label_events)
        self.has_weapon = False
        self._input_dct = None
        eng.attach_obs(self.on_start_frame)

    def start(self):
        eng.attach_obs(self.on_frame)

    def on_collision(self, obj, obj_name):
        if obj == self.mdt.gfx.nodepath.node():
            if obj_name.startswith(self.props.respawn_name):
                self.process_respawn()
            if obj_name.startswith(self.props.pitstop_name):
                self.mdt.gui.apply_damage(True)
                self.mdt.phys.apply_damage(True)
                self.mdt.gfx.apply_damage(True)
            if obj_name.startswith(self.props.goal_name):
                self._process_goal()
            if any(obj_name.startswith(name) for name in [self.props.wall_name, 'Vehicle']):
                self._process_wall()
            if obj_name.startswith(self.props.bonus_name):
                self.on_bonus()
            if obj_name.startswith('Mine'):
                self.mdt.phys.pnode.apply_central_force((0, 0, 200000))

    def on_bonus(self):
        if self.mdt.logic.weapon:
            self.mdt.logic.weapon.destroy()
        wpn_cls = choice([Rocket, RearRocket, Turbo, RotateAll, Mine])
        if wpn_cls == Rocket:
            path = self.props.rocket_path
            self.mdt.logic.weapon = wpn_cls(self.mdt, path, game.cars + [game.player_car], self.props.particle_path)
        elif wpn_cls == RearRocket:
            path = self.props.rocket_path
            self.mdt.logic.weapon = wpn_cls(self.mdt, path, game.cars + [game.player_car], self.props.particle_path)
        elif wpn_cls == Turbo:
            path = self.props.turbo_path
            self.mdt.logic.weapon = wpn_cls(self.mdt, path)
        elif wpn_cls == RotateAll:
            path = self.props.rotate_all_path
            self.mdt.logic.weapon = wpn_cls(self.mdt, path, game.cars + [game.player_car])
        elif wpn_cls == Mine:
            path = self.props.mine_path
            self.mdt.logic.weapon = wpn_cls(self.mdt, path, self.props.particle_path)
        self.has_weapon = True
        return wpn_cls

    def _on_crash(self):
        if self.mdt.fsm.getCurrentOrNextState() != 'Results':
            self.mdt.gfx.crash_sfx()

    def _process_wall(self):
        self._on_crash()

    def _process_goal(self):
        if self.mdt.fsm.getCurrentOrNextState() == 'Results' or \
                self.mdt.logic.last_time_start and \
                not self.mdt.logic.correct_lap:
            return
        self.mdt.logic.reset_waypoints()
        lap_times = self.mdt.logic.lap_times
        if self.mdt.logic.last_time_start:
            lap_times += [self.mdt.logic.lap_time]
            self._process_nonstart_goals(1 + len(lap_times), self.mdt.laps)
        self.mdt.logic.last_time_start = globalClock.getFrameTime()

    def _process_nonstart_goals(self, lap_number, laps):
        pass

    def process_respawn(self):
        start_wp_n, end_wp_n = self.mdt.logic.last_wp
        self.mdt.gfx.nodepath.setPos(start_wp_n.get_pos() + (0, 0, 2))
        wp_vec = Vec3(end_wp_n.getPos(start_wp_n).xy, 0)
        wp_vec.normalize()
        or_h = (wp_vec.xy).signedAngleDeg(Vec2(0, 1))
        self.mdt.gfx.nodepath.setHpr(-or_h, 0, 0)
        self.mdt.gfx.nodepath.node().setLinearVelocity(0)
        self.mdt.gfx.nodepath.node().setAngularVelocity(0)

    def on_start_frame(self):
        self._input_dct = None

    def on_frame(self):
        input_dct = self._get_input()
        if self.mdt.fsm.getCurrentOrNextState() in ['Loading', 'Countdown']:
            input_dct = {key: False for key in input_dct}
            self.mdt.logic.reset_car()
        self.__update_contact_pos()
        self.mdt.phys.update_car_props()
        self.mdt.logic.update_waypoints()
        self.mdt.logic.update(input_dct)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)

    def __update_contact_pos(self):
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top = (car_pos.x, car_pos.y, car_pos.z + 50)
        bottom = (car_pos.x, car_pos.y, car_pos.z - 50)
        hits = PhysMgr().ray_test_all(top, bottom).getHits()
        road_n = self.props.road_name
        for hit in [hit for hit in hits if road_n in hit.getNode().getName()]:
            self.mdt.logic.last_wp = self.mdt.logic.closest_wp()

    def destroy(self):
        eng.detach_obs(self.on_collision)
        eng.detach_obs(self.on_frame)
        eng.detach_obs(self.on_start_frame)
        map(lambda tok: tok.release(), self.toks)
        Event.destroy(self)


class CarPlayerEvent(CarEvent):

    def __init__(self, mdt, carevent_props):
        CarEvent.__init__(self, mdt, carevent_props)
        if not eng.is_runtime:
            self.accept('f11', self.mdt.gui.toggle)
        state = self.mdt.fsm.getCurrentOrNextState()
        self.input_dct_bld = InputDctBuilder.build(state,
                                                   carevent_props.joystick)
        self.accept(self.props.keys['respawn'], self.process_respawn)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mdt.logic.camera.update(
            self.mdt.phys.speed_ratio, self.mdt.logic.is_rolling,
            self.mdt.fsm.getCurrentOrNextState() == 'Countdown')
        self.mdt.audio.update(self._get_input())

    def on_collision(self, obj, obj_name):
        CarEvent.on_collision(self, obj, obj_name)
        if obj != self.mdt.gfx.nodepath.node():
            return
        if any(obj_name.startswith(s) for s in self.props.roads_names):
            eng.audio.play(self.mdt.audio.landing_sfx)

    def on_bonus(self):
        if self.mdt.logic.weapon:
            self.mdt.gui.unset_weapon()
        wpn_cls = CarEvent.on_bonus(self)
        self.accept(self.props.keys['button'], self.on_fire)
        wpn2img = {
            Rocket: 'rocketfront',
            RearRocket: 'rocketrear',
            Turbo: 'turbo',
            RotateAll: 'turn',
            Mine: 'mine'}
        self.mdt.gui.set_weapon(wpn2img[wpn_cls])

    def on_fire(self):
        self.ignore(self.props.keys['button'])
        self.mdt.logic.fire()
        self.has_weapon = False
        self.mdt.gui.unset_weapon()

    def _process_wall(self):
        CarEvent._process_wall(self)
        eng.play(self.mdt.audio.crash_sfx)

    def _process_nonstart_goals(self, lap_number, laps):
        CarEvent._process_nonstart_goals(self, lap_number, laps)
        curr_lap = min(laps, lap_number)
        self.mdt.gui.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        eng.play(self.mdt.audio.lap_sfx)

    def _process_end_goal(self):
        self.notify('on_end_race')

    def _process_goal(self):
        CarEvent._process_goal(self)
        lap_times = self.mdt.logic.lap_times
        is_best = not lap_times or min(lap_times) > self.mdt.logic.lap_time
        if self.mdt.logic.last_time_start and (not lap_times or is_best):
            self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
        if len(lap_times) == self.mdt.laps:
            self._process_end_goal()
        #self.on_bonus()  # to test weapons

    def _get_input(self):
        if not self._input_dct:
            self._input_dct = self.input_dct_bld.build_dct(self.mdt.ai, self.has_weapon)
        return self._input_dct

    def destroy(self):
        evts = ['f11', self.props.keys['button'], self.props.keys['respawn']]
        map(self.ignore, evts)
        CarEvent.destroy(self)


class CarPlayerEventServer(CarPlayerEvent):

    def __init__(self, mdt):
        CarPlayerEvent.__init__(self, mdt)

    def _process_end_goal(self):
        Server().send([NetMsgs.end_race])
        CarPlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mdt):
        CarPlayerEvent.__init__(self, mdt)
        self.last_sent = globalClock.getFrameTime()

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mdt.gfx.nodepath.getPos()
        hpr = self.mdt.gfx.nodepath.getHpr()
        velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
        packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
        if globalClock.getFrameTime() - self.last_sent > .2:
            Client().send(packet)
            self.last_sent = globalClock.getFrameTime()

    def _process_end_goal(self):
        Client().send([NetMsgs.end_race_player])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    def _get_input(self):
        if not self._input_dct:
            self._input_dct = {key: False for key in ['forward', 'left', 'reverse', 'right']}
        return self._input_dct


class CarAiEvent(CarEvent):

    def _get_input(self):
        if not self._input_dct:
            self._input_dct = self.mdt.ai.get_input()
        return self._input_dct


class CarAiPlayerEvent(CarAiEvent, CarPlayerEvent):

    pass
